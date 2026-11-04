import pytest

from migrator import config
from tests.conftest import ROOT


def test_example_config_loads():
    cfg = config.load(ROOT / "migration.yaml")
    assert cfg.source.java == 8 and cfg.target.java == 17
    assert cfg.target_family == "jboss-eap-8"
    assert cfg.migration_branch == "migration/jboss-eap-8.0"
    assert "src/main/webapp/**" in cfg.protected_paths
    assert cfg.output.test_plan_format == ["markdown", "xlsx"]


def _raw(**overrides):
    raw = {"repo": {"url": "https://example.com/a.git"},
           "source": {"server": "jboss-eap-7.2", "java": 8},
           "target": {"server": "jboss-eap-8.0", "java": 17},
           "upgrades": ["javax-to-jakarta"]}
    raw.update(overrides)
    return raw


def test_unknown_upgrade_rejected():
    with pytest.raises(config.ConfigError, match="unknown upgrades"):
        config.parse(_raw(upgrades=["struts-to-spring"]))


def test_java_downgrade_rejected():
    with pytest.raises(config.ConfigError):
        config.parse(_raw(target={"server": "jboss-eap-8.0", "java": 7}))


def test_unknown_section_key_rejected():
    with pytest.raises(config.ConfigError, match="unknown keys in 'ui'"):
        config.parse(_raw(ui={"enabled": True, "colour": "blue"}))
