"""Inventories the application: build tool, dependencies, descriptors, server config and
risky API usage. Optionally runs the Red Hat MTA (Konveyor) CLI and merges its issues."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import shell
from .config import MigrationConfig

log = logging.getLogger(__name__)

DESCRIPTORS = (
    "web.xml", "jboss-web.xml", "jboss-deployment-structure.xml", "persistence.xml",
    "beans.xml", "faces-config.xml", "ejb-jar.xml", "jboss-ejb3.xml", "application.xml",
    "jboss-app.xml", "standalone.xml", "standalone-full.xml", "domain.xml",
)

# (regex, category, message, automatable)
API_RULES: list[tuple[str, str, str, bool]] = [
    (r"\bimport\s+javax\.(servlet|persistence|ejb|inject|enterprise|faces|ws\.rs|validation|"
     r"annotation\.(security|sql)|annotation\.Resource|annotation\.Post|annotation\.Pre|"
     r"transaction|jms|json|mail|xml\.bind|xml\.ws|websocket|security\.enterprise|batch|"
     r"interceptor|decorator|el|resource)\b",
     "jakarta-namespace", "javax.* Jakarta EE API (renamed to jakarta.*)", True),
    (r"\borg\.picketlink\.", "security", "PicketLink API (removed; move to Elytron)", False),
    (r"\borg\.jboss\.security\.", "security", "Legacy PicketBox security API (removed in EAP 8)", False),
    (r"\borg\.jboss\.ejb3\.annotation\.SecurityDomain\b", "security",
     "@SecurityDomain needs an Elytron application-security-domain mapping", True),
    (r"\bLoginModule\b", "security", "Custom JAAS LoginModule (rewrite as Elytron realm)", False),
    (r"[\"']java:jboss/[^\"']*[\"']", "jndi", "Vendor-specific java:jboss/ JNDI lookup", False),
    (r"\bnew\s+InitialContext\s*\(", "jndi", "Manual JNDI lookup (verify names on target)", False),
    (r"\borg\.jboss\.seam\.", "framework", "JBoss Seam (no supported migration path)", False),
    (r"\borg\.hibernate\.Criteria\b|\bcreateCriteria\s*\(", "hibernate",
     "Legacy Hibernate Criteria API (removed in Hibernate 6)", False),
    (r"\borg\.hibernate\.annotations\.Type\b|@Type\s*\(\s*type\s*=", "hibernate",
     "@Type(type=...) changed in Hibernate 6", True),
    (r"\borg\.junit\.(Test|Before|After|Rule|runner)\b", "test", "JUnit 4 API", True),
    (r"\borg\.jboss\.logging\.Logger\b", "logging", "JBoss Logging (still supported, check version)", True),
    (r"\bsun\.misc\.|\bcom\.sun\.", "jdk", "Internal JDK API (may be inaccessible on Java 17)", False),
]
_COMPILED = [(re.compile(p), c, m, a) for p, c, m, a in API_RULES]


@dataclass
class Finding:
    file: str
    line: int
    category: str
    message: str
    automatable: bool
    source: str = "scanner"   # "scanner" | "mta"


@dataclass
class Dependency:
    group: str
    artifact: str
    version: str
    scope: str = "compile"


@dataclass
class Inventory:
    build_tool: str
    java_files: int = 0
    test_files: int = 0
    dependencies: list[Dependency] = field(default_factory=list)
    descriptors: list[str] = field(default_factory=list)
    jsp_jsf_files: list[str] = field(default_factory=list)
    bundled_jars: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    mta_ran: bool = False

    def by_category(self) -> dict[str, list[Finding]]:
        out: dict[str, list[Finding]] = {}
        for f in self.findings:
            out.setdefault(f.category, []).append(f)
        return out

    @property
    def manual_findings(self) -> list[Finding]:
        return [f for f in self.findings if not f.automatable]


_POM_NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def parse_pom_dependencies(pom: Path) -> list[Dependency]:
    root = ET.parse(pom).getroot()
    ns = _POM_NS if root.tag.startswith("{") else {}
    q = (lambda t: f"m:{t}") if ns else (lambda t: t)
    props = {}
    for p in root.findall(q("properties"), ns):
        for child in p:
            props[child.tag.split("}")[-1]] = (child.text or "").strip()

    def text(el, tag, default=""):
        node = el.find(q(tag), ns)
        value = (node.text or "").strip() if node is not None else default
        return re.sub(r"\$\{([^}]+)\}", lambda m: props.get(m.group(1), m.group(0)), value)

    deps = []
    for dep in root.iter(f"{{{_POM_NS['m']}}}dependency" if ns else "dependency"):
        deps.append(Dependency(text(dep, "groupId"), text(dep, "artifactId"),
                               text(dep, "version"), text(dep, "scope", "compile")))
    return deps


def scan_sources(root: Path) -> tuple[int, int, list[Finding]]:
    findings: list[Finding] = []
    main = tests = 0
    for path in root.rglob("*.java"):
        rel = path.relative_to(root).as_posix()
        if "/target/" in f"/{rel}" or "/build/" in f"/{rel}":
            continue
        if "/src/test/" in f"/{rel}":
            tests += 1
        else:
            main += 1
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for rx, cat, msg, auto in _COMPILED:
                if rx.search(line):
                    findings.append(Finding(rel, lineno, cat, msg, auto))
    return main, tests, findings


def run_mta(cfg: MigrationConfig, root: Path, out_dir: Path) -> list[Finding]:
    """Runs `mta-cli analyze` in source mode and parses its Konveyor output.yaml."""
    if not shell.available(cfg.tools.mta_cli):
        log.warning("MTA CLI '%s' not found; using built-in scanner only", cfg.tools.mta_cli)
        return []
    mta_out = out_dir / "mta"
    source = "eap" + cfg.source.server.split("-")[-1].split(".")[0]
    target = "eap" + cfg.target.server.split("-")[-1].split(".")[0]
    res = shell.run([cfg.tools.mta_cli, "analyze", "--input", str(root), "--output", str(mta_out),
                     "--source", source, "--target", target, "--mode", "source-only",
                     "--overwrite"], check=False)
    if not res.ok:
        log.warning("MTA analysis failed: %s", res.stderr[-500:])
        return []
    return parse_mta_output(mta_out / "output.yaml", root)


def parse_mta_output(path: Path, root: Path) -> list[Finding]:
    if not path.exists():
        return []
    rulesets = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    findings = []
    for ruleset in rulesets:
        for rule_id, violation in (ruleset.get("violations") or {}).items():
            category = violation.get("category", "mta")
            effort = violation.get("effort") or 0
            for inc in violation.get("incidents") or []:
                uri = inc.get("uri", "").removeprefix("file://")
                try:
                    rel = Path(uri).resolve().relative_to(root.resolve()).as_posix()
                except ValueError:
                    rel = uri
                findings.append(Finding(
                    file=rel, line=int(inc.get("lineNumber") or 0),
                    category=f"mta:{category}",
                    message=f"[{rule_id}] {inc.get('message') or violation.get('description', '')}".strip(),
                    automatable=effort <= 1, source="mta"))
    return findings


def analyze(cfg: MigrationConfig, root: Path, build_tool: str, out_dir: Path) -> Inventory:
    inv = Inventory(build_tool=build_tool)
    if (root / "pom.xml").exists():
        for pom in root.rglob("pom.xml"):
            if "/target/" not in pom.as_posix():
                inv.dependencies.extend(parse_pom_dependencies(pom))

    for path in root.rglob("*"):
        if not path.is_file() or "/target/" in path.as_posix() or "/.git/" in path.as_posix():
            continue
        rel = path.relative_to(root).as_posix()
        if path.name in DESCRIPTORS:
            inv.descriptors.append(rel)
        elif path.suffix in (".jsp", ".jspx", ".tag", ".xhtml", ".tld"):
            inv.jsp_jsf_files.append(rel)
        elif path.suffix == ".jar" and "/.mvn/" not in f"/{rel}" and "gradle/wrapper" not in rel:
            inv.bundled_jars.append(rel)

    inv.java_files, inv.test_files, inv.findings = scan_sources(root)
    mta = run_mta(cfg, root, out_dir)
    inv.mta_ran = bool(mta)
    inv.findings.extend(mta)
    return inv
