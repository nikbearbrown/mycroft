"""Targeted, formatting-preserving namespace rewrites for descriptors, JSP and JSF views.

Only namespace URIs, schema locations, descriptor versions and javax.* class/property names
are touched; every other byte of the file is left as is.
"""

from __future__ import annotations

from pathlib import Path

from .. import namespaces

DESCRIPTOR_NAMES = {
    "web.xml", "web-fragment.xml", "persistence.xml", "orm.xml", "beans.xml", "faces-config.xml",
    "ejb-jar.xml", "application.xml", "jboss-web.xml", "jboss-deployment-structure.xml",
    "jboss-ejb3.xml", "jboss-app.xml",
}
VIEW_SUFFIXES = {".jsp", ".jspx", ".jspf", ".tag", ".tagx", ".xhtml", ".tld", ".taglib.xml"}
SKIP_DIRS = {".git", "target", "build", "node_modules", ".mvn", ".gradle"}


def candidates(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or SKIP_DIRS.intersection(path.relative_to(root).parts):
            continue
        if path.name in DESCRIPTOR_NAMES or path.suffix in VIEW_SUFFIXES \
                or path.name.endswith(".taglib.xml"):
            yield path


def transform_file(path: Path) -> bool:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="surrogateescape")
    new = namespaces.rewrite_text(text)
    if path.name in DESCRIPTOR_NAMES or path.suffix == ".tld" or path.name.endswith(".taglib.xml"):
        new = namespaces.bump_root_version(new)
    if new == text:
        return False
    path.write_bytes(new.encode("utf-8", errors="surrogateescape"))
    return True


def run(root: Path) -> list[str]:
    """Returns the repo-relative paths that changed."""
    return [p.relative_to(root).as_posix() for p in candidates(root) if transform_file(p)]
