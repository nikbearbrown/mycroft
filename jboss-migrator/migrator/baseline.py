"""Records the pre-migration state: build result, per-test outcomes and UI screenshots.

The baseline is what turns "business and UI unchanged" into something the verify stage can prove.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .buildtool import BuildTool
from .config import MigrationConfig
from .verify import test_compare

log = logging.getLogger(__name__)


@dataclass
class Baseline:
    commit: str
    build_ok: bool
    tests: dict[str, str] = field(default_factory=dict)
    screenshots: dict[str, str] = field(default_factory=dict)   # page -> png path
    characterization_tests: list[str] = field(default_factory=list)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Baseline":
        return cls(**json.loads(path.read_text(encoding="utf-8")))


def run_tests(build: BuildTool) -> tuple[bool, dict[str, str]]:
    result = build.test()
    tests = test_compare.parse_reports(build.report_dirs())
    log.info("tests: %d recorded, build rc=%d", len(tests), result.returncode)
    return result.ok, tests


def capture(cfg: MigrationConfig, build: BuildTool, commit: str, out_dir: Path) -> Baseline:
    generated: list[str] = []
    if cfg.baseline.characterization_tests:
        from .testplan import characterization
        generated = [str(p.relative_to(build.root)) for p in
                     characterization.generate(build.root, cfg.baseline.characterization_packages)]

    build_ok, tests = (run_tests(build) if cfg.baseline.run_tests else (build.compile().ok, {}))
    baseline = Baseline(commit=commit, build_ok=build_ok, tests=tests,
                        characterization_tests=generated)

    if cfg.ui.enabled:
        from .verify import ui_compare
        baseline.screenshots = ui_compare.snapshot(cfg.ui.base_url, cfg.ui.pages, out_dir / "ui-baseline")

    baseline.save(out_dir / "baseline.json")
    return baseline
