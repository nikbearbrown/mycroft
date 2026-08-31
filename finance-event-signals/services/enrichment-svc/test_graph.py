"""Graph branch-coverage tests. Run:  python -m pytest test_graph.py -q   (or: python test_graph.py)

Covers every terminal path:
  emit                          — confident directional read
  withhold (self-consistency)   — passes disagree
  withhold (unclear)            — extractor returns 'unclear'
  withhold (low confidence)     — below threshold
  withhold (verify rejects)     — critique says not ok
"""

import os

os.environ.setdefault("ENRICH_SELF_CONSISTENCY_PASSES", "3")

from graph import build_graph  # noqa: E402


class StubLLM:
    """direction is a list consumed one-per-extract-call; critique_ok fixed."""

    provider = "stub"

    def __init__(self, directions, confidence=0.9, critique_ok=True):
        self._dirs = list(directions)
        self._conf = confidence
        self._crit = critique_ok
        self.calls = 0

    def extract(self, event_type, title, items, temperature=0.0):
        d = self._dirs[self.calls % len(self._dirs)]
        self.calls += 1
        return {
            "direction": d,
            "magnitude": "medium",
            "confidence": self._conf,
            "rationale": f"stub pass {self.calls} -> {d}",
        }

    def critique(self, event_type, title, extraction):
        return {"ok": self._crit, "reason": "" if self._crit else "stub rejects"}


EVT = {"event": {"title": "8-K - Test Co", "items": ["2.02"]}}  # -> earnings


def run(llm):
    return build_graph(llm).invoke(dict(EVT))


def test_emit():
    r = run(StubLLM(["up", "up", "up"]))
    assert r["signal"]["status"] == "pending_review"
    assert r["signal"]["direction"] == "up"


def test_withhold_self_consistency():
    r = run(StubLLM(["up", "down", "up"]))
    assert r["signal"]["status"] == "withheld"
    assert "self-consistency" in r["signal"]["withheld_reason"]


def test_withhold_unclear():
    r = run(StubLLM(["unclear", "unclear", "unclear"]))
    assert r["signal"]["status"] == "withheld"
    assert "unclear" in r["signal"]["withheld_reason"]


def test_withhold_low_confidence():
    r = run(StubLLM(["up", "up", "up"], confidence=0.2))
    assert r["signal"]["status"] == "withheld"
    assert "confidence" in r["signal"]["withheld_reason"]


def test_withhold_verify_rejects():
    r = run(StubLLM(["down", "down", "down"], critique_ok=False))
    assert r["signal"]["status"] == "withheld"
    assert "verify" in r["signal"]["withheld_reason"]


def test_classify_from_items():
    r = build_graph(StubLLM(["up", "up", "up"])).invoke({"event": {"title": "x", "items": ["1.03", "9.01"]}})
    assert r["event_type"] == "bankruptcy"  # 1.03 wins the priority order


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} passed")
