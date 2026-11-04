import json
import threading
import time

import pytest

from migrator import batch, config
from migrator.pipeline import Options, Outcome
from tests.conftest import ROOT


def test_example_portfolio_loads():
    p = batch.load(ROOT / "portfolio.yaml")
    assert [a.name for a in p.apps] == ["orders", "billing", "customer-portal"]
    assert p.parallel == 2
    orders, billing, portal = (a.cfg for a in p.apps)
    assert "picketlink-to-elytron" in orders.upgrades           # list replaced
    assert "picketlink-to-elytron" not in billing.upgrades      # defaults kept
    assert portal.source.server == "jboss-eap-7.4" and portal.source.java == 8   # mapping merged
    assert portal.ui.enabled and not billing.ui.enabled
    assert billing.custom_recipes == ["com.company.migration.CompanyConventions"]


def test_deep_merge_does_not_mutate_defaults():
    defaults = {"a": {"b": 1, "c": [1]}, "d": 1}
    merged = batch.deep_merge(defaults, {"a": {"c": [2]}, "e": 3})
    assert merged == {"a": {"b": 1, "c": [2]}, "d": 1, "e": 3}
    assert defaults == {"a": {"b": 1, "c": [1]}, "d": 1}


def _raw(apps, **kw):
    return {"defaults": {"source": {"server": "jboss-eap-7.2", "java": 8},
                         "target": {"server": "jboss-eap-8.0", "java": 17},
                         "upgrades": ["javax-to-jakarta"]},
            "apps": apps, **kw}


def test_name_defaults_to_repo_and_all_errors_reported():
    p = batch.parse(_raw([{"repo": {"url": "https://x/y/shop.git"}}]))
    assert p.apps[0].name == "shop"

    with pytest.raises(config.ConfigError) as exc:
        batch.parse(_raw([
            {"name": "a", "repo": {"url": "https://x/a.git"}},
            {"name": "a", "repo": {"url": "https://x/a2.git"}},
            {"name": "b", "repo": {"url": "https://x/b.git"}, "upgrades": ["nope"]},
            {"name": "c"},
        ]))
    msg = str(exc.value)
    assert "duplicate name 'a'" in msg and "b: unknown upgrades" in msg and "c: 'repo.url'" in msg


class FakePipeline:
    """Stands in for Pipeline: outcome chosen by app name, records concurrency."""
    active = 0
    peak = 0
    lock = threading.Lock()

    def __init__(self, cfg, opts):
        self.name = opts.workdir.name

    def run(self):
        with FakePipeline.lock:
            FakePipeline.active += 1
            FakePipeline.peak = max(FakePipeline.peak, FakePipeline.active)
        time.sleep(0.05)
        with FakePipeline.lock:
            FakePipeline.active -= 1
        if self.name == "broken":
            raise RuntimeError("git clone failed\nfatal: repository not found")
        ok = self.name != "risky"
        return Outcome(guard_ok=ok, build_ok=True, tests_ok=True, manual_items=0 if ok else 4,
                       report=f"/w/{self.name}/migration-report.md",
                       pr_url=f"https://github.com/o/{self.name}/pull/1")


def test_run_isolates_failures_keeps_order_and_writes_summary(monkeypatch, tmp_path):
    monkeypatch.setattr(batch, "Pipeline", FakePipeline)
    FakePipeline.peak = 0
    names = ["good", "broken", "risky", "good2"]
    p = batch.parse(_raw([{"name": n, "repo": {"url": f"https://x/{n}.git"}} for n in names]))

    results = batch.run(p, Options(workdir=tmp_path), parallel=3)
    assert [r.name for r in results] == names
    assert [r.status for r in results] == [batch.OK, batch.ERROR, batch.ATTENTION, batch.OK]
    assert results[1].error == "RuntimeError: git clone failed"
    assert results[2].manual_items == 4 and results[2].checks["guard"] is False
    assert FakePipeline.peak > 1

    md, js = batch.write_summary(results, tmp_path)
    text = md.read_text(encoding="utf-8")
    assert "**2 ok**, **1 need attention**, **1 errored**" in text
    assert "| risky | jboss-eap-8.0 | needs-attention | ❌ | ✅ | ✅ | – | 4 |" in text
    assert "- **broken** (`https://x/broken.git`): RuntimeError: git clone failed" in text
    assert json.loads(js.read_text())["counts"] == {"ok": 2, "needs-attention": 1, "error": 1}


def test_only_filter(monkeypatch, tmp_path):
    monkeypatch.setattr(batch, "Pipeline", FakePipeline)
    p = batch.parse(_raw([{"name": n, "repo": {"url": f"https://x/{n}.git"}} for n in "abc"]))
    assert [r.name for r in batch.run(p, Options(workdir=tmp_path), only=["c", "a"])] == ["a", "c"]
    with pytest.raises(config.ConfigError, match="unknown app"):
        batch.run(p, Options(workdir=tmp_path), only=["zzz"])
