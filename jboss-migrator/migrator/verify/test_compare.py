"""Parses JUnit XML reports and compares per-test outcomes between baseline and migrated runs."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

PASSED, FAILED, ERROR, SKIPPED = "passed", "failed", "error", "skipped"


def parse_reports(report_dirs: list[Path]) -> dict[str, str]:
    """Returns {"com.x.FooTest#method": status} from every TEST-*.xml under report_dirs."""
    results: dict[str, str] = {}
    for d in report_dirs:
        for xml in Path(d).rglob("TEST-*.xml"):
            results.update(parse_file(xml))
    return results


def parse_file(path: Path) -> dict[str, str]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    out: dict[str, str] = {}
    for suite in suites:
        for case in suite.iter("testcase"):
            # JUnit 5 adds "()" to method names; strip it so JUnit 4 baselines still match.
            name = case.get("name", "").removesuffix("()")
            key = f"{case.get('classname', suite.get('name', ''))}#{name}"
            if case.find("failure") is not None:
                out[key] = FAILED
            elif case.find("error") is not None:
                out[key] = ERROR
            elif case.find("skipped") is not None:
                out[key] = SKIPPED
            else:
                out[key] = PASSED
    return out


@dataclass
class Comparison:
    regressions: list[str] = field(default_factory=list)   # passed -> failed/error
    fixed: list[str] = field(default_factory=list)         # failed/error -> passed
    missing: list[str] = field(default_factory=list)       # in baseline, not in migrated run
    new: list[str] = field(default_factory=list)           # only in migrated run
    newly_skipped: list[str] = field(default_factory=list)
    unchanged: int = 0

    @property
    def ok(self) -> bool:
        return not (self.regressions or self.missing or self.newly_skipped)


def compare(baseline: dict[str, str], migrated: dict[str, str]) -> Comparison:
    c = Comparison()
    for test, before in sorted(baseline.items()):
        after = migrated.get(test)
        if after is None:
            c.missing.append(test)
        elif before == PASSED and after in (FAILED, ERROR):
            c.regressions.append(test)
        elif before in (FAILED, ERROR) and after == PASSED:
            c.fixed.append(test)
        elif before != SKIPPED and after == SKIPPED:
            c.newly_skipped.append(test)
        else:
            c.unchanged += 1
    c.new = sorted(set(migrated) - set(baseline))
    return c
