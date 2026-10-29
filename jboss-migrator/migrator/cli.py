"""Entry point: jboss-migrator migrate --config migration.yaml"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__, analyzer, buildtool, config, planner
from .git_ops import Repo
from .pipeline import Options, Pipeline
from .verify import diff_guard


def _cmd_migrate(args) -> int:
    cfg = config.load(args.config)
    opts = Options(workdir=Path(args.workdir), repo_path=Path(args.repo_path) if args.repo_path else None,
                   push=not args.no_push, skip_baseline=args.skip_baseline)
    outcome = Pipeline(cfg, opts).run()
    print(json.dumps(asdict(outcome) | {"ok": outcome.ok}, indent=2))
    return 0 if outcome.ok else 2


def _inventory(args):
    cfg = config.load(args.config)
    root = Path(args.repo_path).resolve()
    build = buildtool.detect(root, cfg.tools)
    out = Path(args.workdir).resolve() / "analyze"
    return cfg, analyzer.analyze(cfg, root, build.name, out)


def _cmd_analyze(args) -> int:
    _, inv = _inventory(args)
    print(f"build tool: {inv.build_tool}; {inv.java_files} main / {inv.test_files} test Java files")
    print(f"descriptors: {', '.join(inv.descriptors) or 'none'}")
    for cat, items in sorted(inv.by_category().items()):
        auto = sum(f.automatable for f in items)
        print(f"  {cat:24s} {len(items):5d} findings ({auto} automatable)")
    return 0


def _cmd_plan(args) -> int:
    cfg, inv = _inventory(args)
    plan = planner.build_plan(cfg, inv)
    for i, step in enumerate(plan.steps, 1):
        recipes = f"  [{', '.join(step.recipes)}]" if step.recipes else ""
        print(f"{i:2d}. {step.id:24s} {step.engine:16s} {step.description}{recipes}")
    print(f"\n{len(plan.manual_items)} item(s) need a human:")
    for item in plan.manual_items:
        print(f"  - {item}")
    return 0


def _cmd_guard(args) -> int:
    cfg = config.load(args.config)
    result = diff_guard.check(Repo(Path(args.repo_path)), args.base, args.head, cfg.protected_paths)
    for v in result.violations:
        print(f"VIOLATION {v.file}")
        for line in v.removed:
            print(f"  -{line}")
        for line in v.added:
            print(f"  +{line}")
    print(f"{len(result.checked)} protected file(s) changed, {len(result.violations)} violation(s)")
    return 0 if result.ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jboss-migrator", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp, needs_repo: bool):
        sp.add_argument("--config", default="migration.yaml")
        sp.add_argument("--workdir", default="workspace")
        sp.add_argument("--repo-path", required=needs_repo,
                        help="existing checkout to use instead of cloning repo.url")

    m = sub.add_parser("migrate", help="run the full pipeline")
    common(m, needs_repo=False)
    m.add_argument("--no-push", action="store_true", help="keep the branch local; no PR")
    m.add_argument("--skip-baseline", action="store_true",
                   help="skip baseline build/tests/UI (faster, but nothing to compare against)")
    m.set_defaults(func=_cmd_migrate)

    a = sub.add_parser("analyze", help="inventory + findings only")
    common(a, needs_repo=True)
    a.set_defaults(func=_cmd_analyze)

    pl = sub.add_parser("plan", help="show the steps a migration would run")
    common(pl, needs_repo=True)
    pl.set_defaults(func=_cmd_plan)

    g = sub.add_parser("guard", help="run the diff guard between two commits")
    common(g, needs_repo=True)
    g.add_argument("--base", required=True)
    g.add_argument("--head", default="HEAD")
    g.set_defaults(func=_cmd_guard)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    try:
        return args.func(args)
    except config.ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 64


if __name__ == "__main__":
    sys.exit(main())
