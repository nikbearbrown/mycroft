"""Regenerates server configuration for the target as JBoss CLI scripts.

Reads legacy datasources and PicketBox security domains from any standalone*.xml in the repo
(plus jboss-web.xml / persistence.xml references) and writes idempotent CLI scripts under
migration/jboss-cli/. Login modules that have no mechanical Elytron equivalent are emitted as
TODO comments and reported as manual items.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

OUT_DIR = Path("migration") / "jboss-cli"


@dataclass
class Datasource:
    name: str
    jndi: str
    url: str = "${env.DB_URL}"
    driver: str = "${env.DB_DRIVER:postgresql}"
    user: str = "${env.DB_USER}"


@dataclass
class SecurityDomain:
    name: str
    modules: list[dict] = field(default_factory=list)   # [{"code": ..., "options": {...}}]


@dataclass
class ServerModel:
    datasources: list[Datasource] = field(default_factory=list)
    security_domains: list[SecurityDomain] = field(default_factory=list)


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def parse_standalone(path: Path, model: ServerModel) -> None:
    root = ET.parse(path).getroot()
    for el in root.iter():
        tag = _local(el.tag)
        if tag == "datasource":
            ds = Datasource(name=el.get("pool-name") or el.get("jndi-name", "ds").split("/")[-1],
                            jndi=el.get("jndi-name", ""))
            for child in el.iter():
                ctag = _local(child.tag)
                if ctag == "connection-url" and child.text:
                    ds.url = child.text.strip()
                elif ctag == "driver" and child.text:
                    ds.driver = child.text.strip()
                elif ctag == "user-name" and child.text:
                    ds.user = child.text.strip()
            model.datasources.append(ds)
        elif tag == "security-domain" and el.get("name") not in ("other", "jboss-web-policy",
                                                                  "jboss-ejb-policy", "jaspitest"):
            dom = SecurityDomain(el.get("name", ""))
            for lm in el.iter():
                if _local(lm.tag) == "login-module":
                    opts = {o.get("name"): o.get("value") for o in lm if _local(o.tag) == "module-option"}
                    dom.modules.append({"code": lm.get("code", ""), "options": opts})
            if dom.modules:
                model.security_domains.append(dom)


def collect_references(root: Path, model: ServerModel) -> None:
    """Adds placeholder entries for datasources / domains referenced by the app but not defined."""
    known_jndi = {d.jndi for d in model.datasources}
    for pxml in root.rglob("persistence.xml"):
        for jndi in re.findall(r"<jta-data-source>\s*([^<\s]+)\s*</jta-data-source>",
                               pxml.read_text(encoding="utf-8", errors="replace")):
            if jndi not in known_jndi:
                model.datasources.append(Datasource(name=jndi.split("/")[-1], jndi=jndi))
                known_jndi.add(jndi)
    known_dom = {d.name for d in model.security_domains}
    for jw in root.rglob("jboss-web.xml"):
        for name in re.findall(r"<security-domain>\s*([^<\s]+)\s*</security-domain>",
                               jw.read_text(encoding="utf-8", errors="replace")):
            name = name.removeprefix("java:/jaas/")
            if name not in known_dom:
                model.security_domains.append(SecurityDomain(name, [{"code": "UNKNOWN", "options": {}}]))
                known_dom.add(name)


def datasource_cli(model: ServerModel) -> str:
    lines = ["# Datasources for the target server (review credentials; prefer a credential store).",
             "batch"]
    for ds in model.datasources:
        lines.append(
            f"data-source add --name={ds.name} --jndi-name={ds.jndi} --driver-name={ds.driver} "
            f"--connection-url={ds.url} --user-name={ds.user} --password=${{env.DB_PASSWORD}} "
            f"--enabled=true")
    lines += ["run-batch", ""]
    return "\n".join(lines)


def _realm_for(domain: SecurityDomain, module: dict) -> tuple[list[str], str | None]:
    """Returns (cli lines, realm name) or ([], None) with a TODO when not mechanical."""
    code, opts, realm = module["code"], module["options"], f"{domain.name}-realm"
    if code == "Database":
        ds = opts.get("dsJndiName", "java:/UNKNOWN").split("/")[-1]
        principals = opts.get("principalsQuery", "SELECT password FROM users WHERE username=?")
        roles = opts.get("rolesQuery", "SELECT role, 'Roles' FROM roles WHERE username=?")
        # Elytron's clear-password mapper assumes plain text; hashed passwords need a different mapper.
        return [
            f'/subsystem=elytron/jdbc-realm={realm}:add(principal-query=['
            f'{{sql="{principals}", data-source={ds}, clear-password-mapper={{password-index=1}}}}, '
            f'{{sql="{roles}", data-source={ds}, attribute-mapping=[{{index=1, to=Roles}}]}}])'
        ], realm
    if code == "UsersRoles":
        users = opts.get("usersProperties", "users.properties")
        roles = opts.get("rolesProperties", "roles.properties")
        return [
            f'/subsystem=elytron/properties-realm={realm}:add(users-properties={{path={users}, '
            f'relative-to=jboss.server.config.dir, plain-text=true}}, groups-properties={{path={roles}, '
            f'relative-to=jboss.server.config.dir}})'
        ], realm
    if code == "RealmDirect":
        return [], "ApplicationRealm"
    return [f"# TODO({domain.name}): login-module '{code}' has no mechanical Elytron mapping; "
            f"options={opts}"], None


def elytron_cli(model: ServerModel) -> tuple[str, list[str]]:
    lines = ["# Legacy PicketBox/PicketLink security domains -> Elytron.",
             "# Application security domains keep the legacy names so jboss-web.xml and",
             "# @SecurityDomain references continue to resolve.", "batch"]
    manual: list[str] = []
    for dom in model.security_domains:
        realm = None
        for module in dom.modules:
            cli, realm = _realm_for(dom, module)
            lines.extend(cli)
            if realm:
                break
        if not realm:
            manual.append(f"Security domain '{dom.name}': login modules "
                          f"{[m['code'] for m in dom.modules]} need a hand-written Elytron realm.")
            continue
        sd = f"{dom.name}-sd"
        lines += [
            f"/subsystem=elytron/security-domain={sd}:add(realms=[{{realm={realm}, "
            f"role-decoder=groups-to-roles}}], default-realm={realm}, permission-mapper=default-permission-mapper)",
            f"/subsystem=elytron/http-authentication-factory={dom.name}-http:add("
            f"http-server-mechanism-factory=global, security-domain={sd}, "
            f"mechanism-configurations=[{{mechanism-name=FORM}}, {{mechanism-name=BASIC}}])",
            f"/subsystem=undertow/application-security-domain={dom.name}:add("
            f"http-authentication-factory={dom.name}-http)",
            f"/subsystem=ejb3/application-security-domain={dom.name}:add(security-domain={sd})",
        ]
    lines += ["run-batch", ""]
    return "\n".join(lines), manual


def run(root: Path, include_security: bool) -> tuple[list[str], list[str]]:
    """Writes CLI scripts; returns (written repo-relative paths, manual items)."""
    model = ServerModel()
    for cfg in root.rglob("standalone*.xml"):
        if ".git" not in cfg.parts:
            try:
                parse_standalone(cfg, model)
            except ET.ParseError:
                continue
    collect_references(root, model)

    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    written, manual = [], []
    if model.datasources:
        (out / "01-datasources.cli").write_text(datasource_cli(model), encoding="utf-8")
        written.append((OUT_DIR / "01-datasources.cli").as_posix())
    if include_security and model.security_domains:
        script, manual = elytron_cli(model)
        (out / "02-elytron.cli").write_text(script, encoding="utf-8")
        written.append((OUT_DIR / "02-elytron.cli").as_posix())
    return written, manual
