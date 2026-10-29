"""Orchestrates the stages: clone & baseline -> analyze -> transform -> verify -> test plan & PR."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from . import analyzer, baseline as baseline_mod, buildtool, planner, report, shell
from .config import MigrationConfig
from .git_ops import Repo, open_pull_request
from .testplan import generator
from .transformers import jar_transformer, llm_suggest, openrewrite, server_config, xml_descriptors
from .verify import deploy, diff_guard, test_compare, ui_compare

log = logging.getLogger(__name__)


@dataclass
class StepRun:
    step: planner.Step
    before: str
    commit: str | None = None
    files: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class Outcome:
    guard_ok: bool = True
    build_ok: bool = False
    tests_ok: bool | None = None
    ui_ok: bool | None = None
    pr_url: str | None = None

    @property
    def ok(self) -> bool:
        return self.guard_ok and self.build_ok and self.tests_ok is not False and self.ui_ok is not False


@dataclass
class Options:
    workdir: Path = Path("workspace")
    repo_path: Path | None = None      # use an existing checkout instead of cloning
    push: bool = True
    skip_baseline: bool = False


class Pipeline:
    def __init__(self, cfg: MigrationConfig, opts: Options):
        self.cfg, self.opts = cfg, opts
        name = cfg.repo_url.rstrip("/").split("/")[-1].removesuffix(".git")
        self.run_dir = (opts.workdir / name).resolve()
        self.artifacts = self.run_dir / "artifacts"     # outside the repo; never committed
        self.manual: list[str] = []
        self.skipped: list[str] = []

    # ---- stage 2: clone and baseline -------------------------------------------------------
    def checkout(self) -> Repo:
        if self.opts.repo_path:
            return Repo(self.opts.repo_path.resolve())
        dest = self.run_dir / "repo"
        if dest.exists():
            repo = Repo(dest)
            repo.git("fetch", "origin", self.cfg.branch)
            repo.git("checkout", "-B", self.cfg.branch, f"origin/{self.cfg.branch}")
            repo.git("clean", "-fdx")
            return repo
        return Repo.clone(self.cfg.repo_url, self.cfg.branch, dest)

    def capture_ui(self, build: buildtool.BuildTool, server: str, out: Path,
                   cli_scripts: list[Path] = ()) -> dict[str, str]:
        if not build.package().ok or not build.artifacts():
            self.skipped.append(f"UI snapshots on {server}: package failed")
            return {}
        try:
            deploy.start(server, build.artifacts()[0], list(cli_scripts))
            if not deploy.wait_ready(self.cfg.ui.base_url):
                self.skipped.append(f"UI snapshots on {server}: server did not become ready")
                return {}
            return ui_compare.snapshot(self.cfg.ui.base_url, self.cfg.ui.pages, out)
        except (FileNotFoundError, shell.CommandError) as exc:
            self.skipped.append(f"UI snapshots on {server}: {exc}")
            return {}
        finally:
            deploy.stop()

    # ---- stage 4: transform ----------------------------------------------------------------
    def apply_step(self, repo: Repo, build: buildtool.BuildTool, step: planner.Step,
                   inv: analyzer.Inventory) -> StepRun:
        run = StepRun(step, before=repo.head())
        try:
            if step.engine == "openrewrite":
                openrewrite.run(build, step.recipes, step.artifacts, self.artifacts)
            elif step.engine == "xml":
                xml_descriptors.run(repo.path)
            elif step.engine == "jar-transformer":
                _, manual = jar_transformer.run(repo.path, inv.bundled_jars,
                                                self.cfg.tools.eclipse_transformer_jar)
                self.manual.extend(manual)
            elif step.engine == "server-config":
                _, manual = server_config.run(repo.path, include_security=step.id == "picketlink-to-elytron")
                self.manual.extend(manual)
        except (shell.CommandError, OSError) as exc:
            run.error = str(exc).splitlines()[0]
            self.skipped.append(f"{step.id}: {run.error}")
            repo.git("reset", "--hard", run.before)
            repo.git("clean", "-fd")
            return run
        run.commit = repo.commit_all(step.commit_message)
        if run.commit:
            run.files = repo.changed_files(run.before, run.commit)
        return run

    # ---- full run ----------------------------------------------------------------------------
    def run(self) -> Outcome:
        cfg, outcome = self.cfg, Outcome()
        self.artifacts.mkdir(parents=True, exist_ok=True)

        repo = self.checkout()
        repo.create_branch(cfg.migration_branch)
        build = buildtool.detect(repo.path, cfg.tools)

        if self.opts.skip_baseline:
            base = baseline_mod.Baseline(commit=repo.head(), build_ok=True)
        else:
            base = baseline_mod.capture(cfg, build, repo.head(), self.artifacts)
            if base.characterization_tests:
                repo.commit_all("migrator(baseline): characterization test skeletons")
            if cfg.ui.enabled:
                base.screenshots = self.capture_ui(build, cfg.source.server,
                                                   self.artifacts / "ui-baseline")
            base.save(self.artifacts / "baseline.json")
            if not base.build_ok:
                self.manual.append("Baseline build/tests were already failing; comparisons use "
                                   "the recorded per-test results.")
        diff_base = repo.head()

        inv = analyzer.analyze(cfg, repo.path, build.name, self.artifacts)
        plan = planner.build_plan(cfg, inv)
        self.manual.extend(plan.manual_items)
        if not shell.available(cfg.tools.mta_cli):
            self.skipped.append("MTA analysis (CLI not found)")

        runs = [self.apply_step(repo, build, step, inv) for step in plan.steps]

        guard = diff_guard.check(repo, diff_base, "HEAD", cfg.protected_paths)
        outcome.guard_ok = guard.ok

        compiled = build.compile()
        outcome.build_ok = compiled.ok
        suggestions = None
        if not compiled.ok and cfg.llm.enabled:
            suggestions = llm_suggest.suggest(compiled.stdout, repo.path, cfg.llm.model,
                                              self.artifacts / "llm-suggestions.md")

        tests = None
        if cfg.baseline.run_tests and compiled.ok and not self.opts.skip_baseline:
            _, migrated = baseline_mod.run_tests(build)
            tests = test_compare.compare(base.tests, migrated)
            outcome.tests_ok = tests.ok

        ui = None
        if cfg.ui.enabled and base.screenshots and compiled.ok:
            scripts = sorted((repo.path / server_config.OUT_DIR).glob("*.cli"))
            current = self.capture_ui(build, cfg.target.server, self.artifacts / "ui-target", scripts)
            ui = ui_compare.compare(base.screenshots, current, cfg.ui.max_pixel_diff_ratio,
                                    self.artifacts)
            outcome.ui_ok = ui.ok

        # ---- stage 6: test plan, report, PR ----------------------------------------------
        out = repo.path / cfg.output.report_dir
        step_commits = [generator.StepCommit(r.step, r.before, r.commit) for r in runs if r.commit]
        tplan = generator.build(repo, step_commits, cfg.protected_paths, cfg.target.java,
                                base.characterization_tests)
        test_plan_path = out / "test-plan.md"
        if "markdown" in cfg.output.test_plan_format:
            report.write("test_plan.md.j2", test_plan_path, cfg=cfg, plan=tplan)
        if "xlsx" in cfg.output.test_plan_format:
            generator.write_xlsx(tplan, out / "test-plan.xlsx")

        ctx = dict(cfg=cfg, baseline=base, inventory=inv, steps=runs, guard=guard, tests=tests,
                   ui=ui, outcome=outcome, manual=self.manual, skipped=self.skipped,
                   suggestions=suggestions)
        report_path = report.write("migration_report.md.j2", out / "migration-report.md", **ctx)
        repo.commit_all("migrator: migration report and unit test plan")

        rel = lambda p: p.relative_to(repo.path).as_posix()
        if cfg.output.create_pr and self.opts.push:
            repo.push(cfg.migration_branch)
            body = report.render("pr_body.md.j2", report_path=rel(report_path),
                                 test_plan_path=rel(test_plan_path), **ctx)
            outcome.pr_url = open_pull_request(
                repo, cfg.migration_branch, cfg.branch,
                f"Migrate to {cfg.target.server} / Java {cfg.target.java}", body)
        log.info("report: %s", report_path)
        return outcome
