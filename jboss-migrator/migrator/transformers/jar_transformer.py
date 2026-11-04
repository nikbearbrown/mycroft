"""Runs Eclipse Transformer over bundled third-party JARs that still reference javax.* APIs."""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path

from .. import shell

log = logging.getLogger(__name__)

_JAVAX_PREFIXES = (b"javax/servlet/", b"javax/persistence/", b"javax/ejb/", b"javax/inject/",
                   b"javax/enterprise/", b"javax/faces/", b"javax/ws/rs/", b"javax/validation/",
                   b"javax/xml/bind/", b"javax/jms/", b"javax/json/", b"javax/transaction/")


def uses_javax(jar: Path) -> bool:
    """Cheap check: does any class file reference a moved javax package?"""
    try:
        with zipfile.ZipFile(jar) as zf:
            for name in zf.namelist():
                if name.endswith(".class") and any(p in zf.read(name) for p in _JAVAX_PREFIXES):
                    return True
    except zipfile.BadZipFile:
        log.warning("not a valid jar: %s", jar)
    return False


def run(root: Path, jars: list[str], transformer_jar: str) -> tuple[list[str], list[str]]:
    """Transforms jars in place. Returns (transformed paths, manual items)."""
    targets = [j for j in jars if uses_javax(root / j)]
    if not targets:
        return [], []
    if not transformer_jar or not Path(transformer_jar).exists():
        return [], [f"{j}: bundled JAR uses javax.*; set tools.eclipse_transformer_jar or replace "
                    f"it with a Jakarta release" for j in targets]
    done = []
    for rel in targets:
        src = root / rel
        tmp = src.with_suffix(".jakarta.jar")
        res = shell.run(["java", "-jar", transformer_jar, str(src), str(tmp), "-o"], check=False)
        if res.ok and tmp.exists():
            tmp.replace(src)
            done.append(rel)
        else:
            log.warning("Eclipse Transformer failed on %s", rel)
    manual = [f"{j}: Eclipse Transformer failed" for j in targets if j not in done]
    return done, manual
