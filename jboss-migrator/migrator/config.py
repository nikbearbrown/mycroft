"""Loads and validates migration.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

KNOWN_UPGRADES = {
    "javax-to-jakarta",
    "hibernate-5-to-6",
    "junit4-to-junit5",
    "picketlink-to-elytron",
}
KNOWN_TARGETS = ("jboss-eap-8", "wildfly-3", "quarkus", "spring-boot")
TEST_PLAN_FORMATS = {"markdown", "xlsx"}


class ConfigError(ValueError):
    pass


@dataclass
class ServerSpec:
    server: str
    java: int


@dataclass
class UiConfig:
    enabled: bool = False
    base_url: str = "http://localhost:8080"
    pages: list[str] = field(default_factory=lambda: ["/"])
    max_pixel_diff_ratio: float = 0.01


@dataclass
class BaselineConfig:
    run_tests: bool = True
    characterization_tests: bool = False
    characterization_packages: list[str] = field(default_factory=list)


@dataclass
class ToolsConfig:
    mta_cli: str = "mta-cli"
    eclipse_transformer_jar: str = ""
    wildfly_server_migration: str = ""
    maven: str = "mvn"
    gradle: str = "gradle"


@dataclass
class LlmConfig:
    enabled: bool = False
    model: str = "claude-opus-5-5"


@dataclass
class OutputConfig:
    create_pr: bool = True
    test_plan_format: list[str] = field(default_factory=lambda: ["markdown"])
    report_dir: str = "migration"


@dataclass
class MigrationConfig:
    repo_url: str
    branch: str
    source: ServerSpec
    target: ServerSpec
    upgrades: list[str]
    protected_paths: list[str] = field(default_factory=list)
    custom_recipes: list[str] = field(default_factory=list)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    ui: UiConfig = field(default_factory=UiConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    llm: LlmConfig = field(default_factory=LlmConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @property
    def target_family(self) -> str:
        for prefix in KNOWN_TARGETS:
            if self.target.server.startswith(prefix):
                return prefix
        return self.target.server

    @property
    def migration_branch(self) -> str:
        return f"migration/{self.target.server}"


def _section(raw: dict, key: str, cls):
    data = raw.get(key) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"'{key}' must be a mapping")
    allowed = cls.__dataclass_fields__.keys()
    unknown = set(data) - set(allowed)
    if unknown:
        raise ConfigError(f"unknown keys in '{key}': {sorted(unknown)}")
    return cls(**data)


def _server(raw: dict, key: str) -> ServerSpec:
    data = raw.get(key)
    if not isinstance(data, dict) or "server" not in data or "java" not in data:
        raise ConfigError(f"'{key}' needs 'server' and 'java'")
    return ServerSpec(server=str(data["server"]), java=int(data["java"]))


def parse(raw: dict) -> MigrationConfig:
    repo = raw.get("repo") or {}
    if not repo.get("url"):
        raise ConfigError("'repo.url' is required")

    upgrades = list(raw.get("upgrades") or [])
    unknown = [u for u in upgrades if u not in KNOWN_UPGRADES]
    if unknown:
        raise ConfigError(f"unknown upgrades {unknown}; known: {sorted(KNOWN_UPGRADES)}")

    source, target = _server(raw, "source"), _server(raw, "target")
    if target.java < source.java:
        raise ConfigError("target.java must be >= source.java")

    cfg = MigrationConfig(
        repo_url=repo["url"],
        branch=repo.get("branch", "main"),
        source=source,
        target=target,
        upgrades=upgrades,
        protected_paths=list(raw.get("protected_paths") or []),
        custom_recipes=list(raw.get("custom_recipes") or []),
        baseline=_section(raw, "baseline", BaselineConfig),
        ui=_section(raw, "ui", UiConfig),
        tools=_section(raw, "tools", ToolsConfig),
        llm=_section(raw, "llm", LlmConfig),
        output=_section(raw, "output", OutputConfig),
    )
    bad = set(cfg.output.test_plan_format) - TEST_PLAN_FORMATS
    if bad:
        raise ConfigError(f"unsupported test_plan_format {sorted(bad)}")
    return cfg


def load(path: str | Path) -> MigrationConfig:
    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return parse(raw)
