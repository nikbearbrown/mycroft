"""Lightweight Java source inspection (regex based; good enough for planning, not compiling)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_PACKAGE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.M)
_TYPE = re.compile(r"^\s*(?:public\s+)?(?:abstract\s+|final\s+)*(class|interface|enum|record)\s+(\w+)", re.M)
_METHOD = re.compile(
    r"^\s*public\s+(?:static\s+|final\s+|synchronized\s+|abstract\s+)*"
    r"(?:<[^>]+>\s+)?[\w.<>\[\],\s?]+?\s+(\w+)\s*\(([^)]*)\)", re.M)
_COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)


@dataclass
class JavaClass:
    path: str
    package: str
    name: str
    kind: str
    public_methods: list[str] = field(default_factory=list)
    annotations: set[str] = field(default_factory=set)

    @property
    def fqcn(self) -> str:
        return f"{self.package}.{self.name}" if self.package else self.name


def parse(path: Path, rel: str) -> JavaClass | None:
    src = _COMMENT.sub("", path.read_text(encoding="utf-8", errors="replace"))
    type_match = _TYPE.search(src)
    if not type_match:
        return None
    pkg = _PACKAGE.search(src)
    methods = []
    for m in _METHOD.finditer(src):
        name = m.group(1)
        if name != type_match.group(2) and name not in methods:   # skip constructors
            methods.append(name)
    return JavaClass(path=rel, package=pkg.group(1) if pkg else "", name=type_match.group(2),
                     kind=type_match.group(1), public_methods=methods,
                     annotations=set(re.findall(r"@(\w+)", src)))


def test_sources(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.java") if "src/test/" in p.as_posix()
            and not {"target", "build", ".git"}.intersection(p.relative_to(root).parts)]


def uses_junit5(root: Path) -> bool:
    return any("org.junit.jupiter" in p.read_text(encoding="utf-8", errors="replace")
               for p in test_sources(root))
