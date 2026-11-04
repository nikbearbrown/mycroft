"""Fails the run if anything in protected_paths changed beyond imports, annotations, or
namespace URIs.

Removed and added lines of each protected file are compared after normalization (see
namespaces.normalize_line). Import lines and annotation-only lines are always allowed.
Whatever is left over on either side is a violation.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from .. import namespaces
from ..git_ops import Repo

_IMPORT = re.compile(r"^\s*import\s+(static\s+)?[\w.*]+\s*;\s*$")
_ANNOTATION = re.compile(r"^\s*@[\w.]+(\(.*\))?\s*$")


def glob_to_regex(pattern: str) -> re.Pattern:
    """Glob with ** (any depth), * (within a segment) and ? support."""
    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def is_protected(path: str, patterns: list[str]) -> bool:
    return any(glob_to_regex(p).match(path) for p in patterns)


@dataclass
class Violation:
    file: str
    removed: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)


@dataclass
class GuardResult:
    checked: list[str] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def _always_allowed(line: str) -> bool:
    return not line.strip() or bool(_IMPORT.match(line) or _ANNOTATION.match(line))


def check_diff(path: str, diff: str) -> Violation | None:
    removed, added = [], []
    for line in diff.splitlines():
        if line.startswith(("---", "+++")):
            continue
        if line.startswith("-"):
            removed.append(line[1:])
        elif line.startswith("+"):
            added.append(line[1:])

    removed = [l for l in removed if not _always_allowed(l)]
    added = [l for l in added if not _always_allowed(l)]
    before = Counter(namespaces.normalize_line(l) for l in removed)
    after = Counter(namespaces.normalize_line(l) for l in added)
    if before == after:
        return None
    extra_removed, extra_added = before - after, after - before
    return Violation(path,
                     [l for l in removed if namespaces.normalize_line(l) in extra_removed],
                     [l for l in added if namespaces.normalize_line(l) in extra_added])


def check(repo: Repo, base: str, head: str, patterns: list[str]) -> GuardResult:
    result = GuardResult()
    if not patterns:
        return result
    for path in repo.changed_files(base, head):
        if not is_protected(path, patterns):
            continue
        result.checked.append(path)
        violation = check_diff(path, repo.file_diff(base, head, path))
        if violation:
            result.violations.append(violation)
    return result
