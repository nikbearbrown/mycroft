"""Batch mode: migrate a portfolio of applications from one file.

portfolio.yaml holds shared `defaults` (any migration.yaml keys) and a list of `apps`, each
deep-merged over the defaults. Every app runs through the normal Pipeline in its own work
directory; one app failing never stops the others. A summary (Markdown + JSON) lists the
outcome, manual-item count, report and PR link per app.
"""

from __future__ import annotations

import copy
import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from . import config, report
from .pipeline import Options, Pipeline

log = logging.getLogger(__name__)

OK, ATTENTION, ERROR = "ok", "needs-attention", "error"
_NAME = re.compile(r"^[A-Za-z0-9][\w.-]*$")


def deep_merge(base: dict, override: dict) -> dict:
    """Mappings merge recursively; lists and scalars in `override` replace `base`."""
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


@dataclass
class App:
    name: str
    cfg: config.MigrationConfig


@dataclass
class Portfolio:
    apps: list[App]
    parallel: int = 1


def parse(raw: dict) -> Portfolio:
    defaults = raw.get("defaults") or {}
    apps_raw = raw.get("apps") or []
    if not isinstance(defaults, dict):
        raise config.ConfigError("'defaults' must be a mapping")
    if not isinstance(apps_raw, list) or not apps_raw:
        raise config.ConfigError("'apps' must be a non-empty list")

    apps, errors, seen = [], [], set()
    for i, entry in enumerate(apps_raw):
        if not isinstance(entry, dict):
            errors.append(f"apps[{i}]: must be a mapping")
            continue
        entry = dict(entry)
        name = str(entry.pop("name", "") or "")
        if not name:
            url = (entry.get("repo") or {}).get("url", "")
            name = url.rstrip("/").split("/")[-1].removesuffix(".git")
        if not _NAME.match(name):
            errors.append(f"apps[{i}]: invalid or missing name {name!r}")
            continue
        if name in seen:
            errors.append(f"apps[{i}]: duplicate name {name!r}")
            continue
        seen.add(name)
        try:
            apps.append(App(name, config.parse(deep_merge(defaults, entry))))
        except config.ConfigError as exc:
            errors.append(f"{name}: {exc}")
    if errors:
        # Report every bad entry at once instead of failing on the first.
        raise config.ConfigError("invalid portfolio:\n  " + "\n  ".join(errors))

    parallel = int(raw.get("parallel", 1))
    if parallel < 1:
        raise config.ConfigError("'parallel' must be >= 1")
    return Portfolio(apps, parallel)


def load(path: str | Path) -> Portfolio:
    with open(path, encoding="utf-8") as fh:
        return parse(yaml.safe_load(fh) or {})


@dataclass
class AppResult:
    name: str
    repo: str
    target: str
    status: str
    seconds: float
    checks: dict = field(default_factory=dict)
    manual_items: int = 0
    report: str | None = None
    pr_url: str | None = None
    error: str | None = None


def _run_app(app: App, opts: Options) -> AppResult:
    started = time.monotonic()
    result = AppResult(app.name, app.cfg.repo_url, app.cfg.target.server, ERROR, 0.0)
    try:
        app_opts = Options(workdir=opts.workdir / app.name, repo_path=None,
                           push=opts.push, skip_baseline=opts.skip_baseline)
        outcome = Pipeline(app.cfg, app_opts).run()
        result.status = OK if outcome.ok else ATTENTION
        result.checks = {"guard": outcome.guard_ok, "build": outcome.build_ok,
                         "tests": outcome.tests_ok, "ui": outcome.ui_ok}
        result.manual_items = outcome.manual_items
        result.report, result.pr_url = outcome.report, outcome.pr_url
    except Exception as exc:  # one broken app must not stop the portfolio
        log.exception("%s failed", app.name)
        result.error = f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}"
    result.seconds = round(time.monotonic() - started, 1)
    log.info("%s: %s in %.0fs", app.name, result.status, result.seconds)
    return result


def run(portfolio: Portfolio, opts: Options, parallel: int | None = None,
        only: list[str] | None = None) -> list[AppResult]:
    apps = portfolio.apps
    if only:
        unknown = set(only) - {a.name for a in apps}
        if unknown:
            raise config.ConfigError(f"unknown app(s) in --only: {sorted(unknown)}")
        apps = [a for a in apps if a.name in only]
    workers = max(1, min(parallel or portfolio.parallel, len(apps)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        # map() keeps portfolio order in the summary regardless of finish order.
        return list(pool.map(lambda a: _run_app(a, opts), apps))


def write_summary(results: list[AppResult], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = {s: sum(r.status == s for r in results) for s in (OK, ATTENTION, ERROR)}
    md = report.write("batch_summary.md.j2", out_dir / "batch-summary.md",
                      results=results, counts=counts)
    js = out_dir / "batch-summary.json"
    js.write_text(json.dumps({"counts": counts, "apps": [asdict(r) for r in results]}, indent=2),
                  encoding="utf-8")
    return md, js
