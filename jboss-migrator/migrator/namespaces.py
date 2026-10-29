"""javax -> jakarta namespace rules, shared by the XML transformer and the diff guard.

Keeping one source of truth means the guard accepts exactly the edits the transformer is allowed
to make in protected code.
"""

from __future__ import annotations

import re

# javax packages that moved to jakarta. JDK-owned javax packages (javax.sql, javax.naming,
# javax.xml.parsers, javax.annotation.processing, javax.transaction.xa, ...) are excluded.
JAVAX_PACKAGE = re.compile(
    r"\bjavax\.(?=(?:activation|batch|decorator|ejb|el|enterprise|faces|inject|interceptor|jms|"
    r"json|jws|mail|persistence|resource|security\.auth\.message|security\.enterprise|"
    r"security\.jacc|servlet|validation|websocket|ws\.rs|xml\.bind|xml\.soap|xml\.ws)\b"
    r"|annotation\.(?:PostConstruct|PreDestroy|Resource|Resources|Priority|ManagedBean|Generated|"
    r"security|sql)\b"
    r"|transaction\.(?!xa\b))"
)

# Literal URI rewrites, most specific first.
URI_REWRITES: list[tuple[str, str]] = [
    # JSF / Facelets view namespaces
    ("http://xmlns.jcp.org/jsf/html", "jakarta.faces.html"),
    ("http://xmlns.jcp.org/jsf/core", "jakarta.faces.core"),
    ("http://xmlns.jcp.org/jsf/facelets", "jakarta.faces.facelets"),
    ("http://xmlns.jcp.org/jsf/composite", "jakarta.faces.composite"),
    ("http://xmlns.jcp.org/jsf/passthrough", "jakarta.faces.passthrough"),
    ("http://xmlns.jcp.org/jsf", "jakarta.faces"),
    ("http://java.sun.com/jsf/html", "jakarta.faces.html"),
    ("http://java.sun.com/jsf/core", "jakarta.faces.core"),
    ("http://java.sun.com/jsf/facelets", "jakarta.faces.facelets"),
    ("http://java.sun.com/jsf/composite", "jakarta.faces.composite"),
    # JSTL taglib URIs
    ("http://xmlns.jcp.org/jsp/jstl/core", "jakarta.tags.core"),
    ("http://xmlns.jcp.org/jsp/jstl/fmt", "jakarta.tags.fmt"),
    ("http://xmlns.jcp.org/jsp/jstl/functions", "jakarta.tags.functions"),
    ("http://xmlns.jcp.org/jsp/jstl/sql", "jakarta.tags.sql"),
    ("http://xmlns.jcp.org/jsp/jstl/xml", "jakarta.tags.xml"),
    ("http://java.sun.com/jsp/jstl/core", "jakarta.tags.core"),
    ("http://java.sun.com/jsp/jstl/fmt", "jakarta.tags.fmt"),
    ("http://java.sun.com/jsp/jstl/functions", "jakarta.tags.functions"),
    ("http://java.sun.com/jsp/jstl/sql", "jakarta.tags.sql"),
    ("http://java.sun.com/jsp/jstl/xml", "jakarta.tags.xml"),
    # Descriptor schema namespaces
    ("http://xmlns.jcp.org/xml/ns/persistence", "https://jakarta.ee/xml/ns/persistence"),
    ("http://java.sun.com/xml/ns/persistence", "https://jakarta.ee/xml/ns/persistence"),
    ("http://xmlns.jcp.org/xml/ns/javaee", "https://jakarta.ee/xml/ns/jakartaee"),
    ("http://java.sun.com/xml/ns/javaee", "https://jakarta.ee/xml/ns/jakartaee"),
]

# Schema file versions for Jakarta EE 10.
SCHEMA_FILES = re.compile(
    r"(web-app|web-fragment|persistence|orm|beans|web-facesconfig|ejb-jar|application|"
    r"web-jsptaglibrary)_\d+_\d+\.xsd")
SCHEMA_TARGETS = {
    "web-app": "6_0", "web-fragment": "6_0", "persistence": "3_0", "orm": "3_1",
    "beans": "4_0", "web-facesconfig": "4_0", "ejb-jar": "4_0", "application": "10",
    "web-jsptaglibrary": "3_0",
}
# Root element -> version attribute value for Jakarta EE 10.
ROOT_VERSIONS = {
    "web-app": "6.0", "web-fragment": "6.0", "persistence": "3.0", "entity-mappings": "3.1",
    "beans": "4.0", "faces-config": "4.0", "ejb-jar": "4.0", "application": "10", "taglib": "3.0",
}


def rewrite_text(text: str) -> str:
    """Applies URI, schema-file and package rewrites. Idempotent."""
    for old, new in URI_REWRITES:
        text = text.replace(old, new)
    text = SCHEMA_FILES.sub(lambda m: f"{m.group(1)}_{SCHEMA_TARGETS[m.group(1)]}.xsd", text)
    return JAVAX_PACKAGE.sub("jakarta.", text)


_ROOT_TAG = re.compile(r"<(?P<tag>[\w-]+)\b(?P<attrs>[^>]*)>", re.S)


def bump_root_version(text: str) -> str:
    """Sets the version attribute on the descriptor's root element (first non-<? element)."""
    for m in _ROOT_TAG.finditer(text):
        tag = m.group("tag")
        if tag not in ROOT_VERSIONS:
            return text
        attrs = re.sub(r'(\bversion\s*=\s*)(["\'])[^"\']*\2',
                       lambda a: f'{a.group(1)}{a.group(2)}{ROOT_VERSIONS[tag]}{a.group(2)}',
                       m.group("attrs"), count=1)
        return text[:m.start("attrs")] + attrs + text[m.end("attrs"):]
    return text


_VERSION_ATTR = re.compile(r'\bversion\s*=\s*(["\'])[\d.]+\1')


def normalize_line(line: str) -> str:
    """Canonical form used by the diff guard: two lines that only differ by allowed namespace
    or descriptor-version changes normalize to the same string."""
    return _VERSION_ATTR.sub('version=""', rewrite_text(line)).strip()
