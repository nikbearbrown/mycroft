#!/usr/bin/env python3
"""conformance — the machine half of P4 (Snickerdoodle).

Deterministic, fast checks that either pass or halt. It does NOT judge whether the
pipeline is *adequate* — that is the human gate. Run: `make verify`.

Checks:
  1. every *.json parses
  2. every *.yaml / *.yml parses
  3. recipe frontmatter parses; status is a valid lifecycle value; todos_open is int>=0;
     recipe_version present
  4. required governance files exist and are non-empty
  5. every services/*/ has a Dockerfile
  6. generated proto Go stubs are present (committed, so docker builds don't need codegen)
  7. no committed secrets (ANTHROPIC_API_KEY empty in .env.example; no 'sk-ant-' tokens tracked)
  8. deploy/k8s/_config/* matches its canonical source (otel/, deploy/postgres/) — `make
     k8s-sync` closes any drift
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", "node_modules", "gen"}  # gen/ = generated, validated by go build
LIFECYCLE = {"DRAFT", "SPECIFIED", "RUNNABLE-SAMPLE", "RUNNABLE-LIVE", "VERIFIED"}

fails: list[str] = []
passes = 0


def ok(msg: str) -> None:
    global passes
    passes += 1
    print(f"  ok   {msg}")


def bad(msg: str) -> None:
    fails.append(msg)
    print(f"  FAIL {msg}")


def walk(*exts: str):
    for p in ROOT.rglob("*"):
        if any(part in SKIP for part in p.parts):
            continue
        if p.suffix in exts and p.is_file():
            yield p


# 1 + 2 — structured files parse
print("[1/8] json parses")
n = 0
for p in walk(".json"):
    n += 1
    try:
        json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        bad(f"{p.relative_to(ROOT)}: {e}")
if not [f for f in fails]:
    ok(f"{n} json files parse")

print("[2/8] yaml parses")
n = 0
for p in walk(".yaml", ".yml"):
    n += 1
    try:
        list(yaml.safe_load_all(p.read_text(encoding="utf-8")))
    except Exception as e:  # noqa: BLE001
        bad(f"{p.relative_to(ROOT)}: {e}")
ok(f"{n} yaml files parse")

# 3 — recipe frontmatter
print("[3/8] recipe frontmatter")
recipe = ROOT / "recipes" / "finance-event-signals.md"
if not recipe.exists():
    bad("recipes/finance-event-signals.md missing")
else:
    m = re.match(r"^---\n(.*?)\n---\n", recipe.read_text(encoding="utf-8"), re.S)
    if not m:
        bad("recipe has no YAML frontmatter")
    else:
        try:
            fm = yaml.safe_load(m.group(1))
            if fm.get("status") not in LIFECYCLE:
                bad(f"recipe status {fm.get('status')!r} not a lifecycle value")
            elif not isinstance(fm.get("todos_open"), int) or fm["todos_open"] < 0:
                bad(f"recipe todos_open must be int>=0, got {fm.get('todos_open')!r}")
            elif not fm.get("recipe_version"):
                bad("recipe_version missing")
            else:
                ok(f"recipe frontmatter valid (status={fm['status']}, "
                   f"todos_open={fm['todos_open']}, v{fm['recipe_version']})")
        except Exception as e:  # noqa: BLE001
            bad(f"recipe frontmatter: {e}")

# 4 — governance files present + non-empty
print("[4/8] governance files")
for rel in ("GOVERNANCE.md", "PRE_REGISTRATION.md", "logs/RUN_LOG.md",
            "data/verified/SCHEMA_REFERENCE.md", "docs/PLAN.md"):
    p = ROOT / rel
    if not p.exists() or p.stat().st_size == 0:
        bad(f"{rel} missing or empty")
if not any("missing or empty" in f for f in fails):
    ok("GOVERNANCE, PRE_REGISTRATION, RUN_LOG, SCHEMA_REFERENCE, PLAN present")

# 5 — every deployable service has a Dockerfile ('common' is a shared library module)
print("[5/8] service Dockerfiles")
LIBS = {"common"}
for svc in sorted((ROOT / "services").iterdir()):
    if svc.is_dir() and svc.name not in LIBS and not (svc / "Dockerfile").exists():
        bad(f"services/{svc.name}/Dockerfile missing")
if not any("Dockerfile missing" in f for f in fails):
    ok("every deployable services/*/ has a Dockerfile (common = shared lib)")

# 6 — generated proto stubs committed
print("[6/8] generated proto stubs")
for rel in ("proto/gen/fes/v1/fes.pb.go", "proto/gen/fes/v1/fes_grpc.pb.go"):
    if not (ROOT / rel).exists():
        bad(f"{rel} missing — run `make proto` and commit it")
if not any("run `make proto`" in f for f in fails):
    ok("proto/gen stubs present")

# 7 — no committed secrets
print("[7/8] no committed secrets")
envx = (ROOT / ".env.example").read_text(encoding="utf-8")
if not re.search(r"^ANTHROPIC_API_KEY=\s*$", envx, re.M):
    bad(".env.example: ANTHROPIC_API_KEY must be empty")
key_re = re.compile(r"sk-ant-api\d{2}-[A-Za-z0-9_-]{20,}")  # real Anthropic key shape
leak = []
for p in walk(".md", ".py", ".go", ".yaml", ".yml", ".json", ".example", ".env"):
    if key_re.search(p.read_text(encoding="utf-8", errors="ignore")):
        leak.append(str(p.relative_to(ROOT)))
if leak:
    bad(f"possible API key in: {', '.join(leak)}")
if not any("API key" in f for f in fails):
    ok("no committed secrets (ANTHROPIC_API_KEY empty; no key tokens tracked)")

# 8 — deploy/k8s/_config/* must match its canonical source (no drift)
print("[8/8] k8s config copies match source (`make k8s-sync`)")
K8S_SYNC_MAP = {
    "deploy/k8s/_config/collector-config.yaml": "otel/collector-config.yaml",
    "deploy/k8s/_config/prometheus.yml": "otel/prometheus.yml",
    "deploy/k8s/_config/grafana-datasources.yaml": "otel/grafana-datasources.yaml",
    "deploy/k8s/_config/001_init.sql": "deploy/postgres/001_init.sql",
    "deploy/k8s/_config/002_signals.sql": "deploy/postgres/002_signals.sql",
    "deploy/k8s/_config/003_outcomes.sql": "deploy/postgres/003_outcomes.sql",
}
for copy_rel, src_rel in K8S_SYNC_MAP.items():
    copy_p, src_p = ROOT / copy_rel, ROOT / src_rel
    if not copy_p.exists():
        bad(f"{copy_rel} missing — run `make k8s-sync`")
    elif not src_p.exists():
        bad(f"{src_rel} (source of {copy_rel}) missing")
    elif copy_p.read_bytes() != src_p.read_bytes():
        bad(f"{copy_rel} has drifted from {src_rel} — run `make k8s-sync`")
if not any("k8s-sync" in f or "drifted" in f for f in fails):
    ok(f"{len(K8S_SYNC_MAP)} k8s config copies match their canonical source")

# summary
print()
if fails:
    print(f"CONFORMANCE FAILED — {len(fails)} problem(s), {passes} ok")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print(f"CONFORMANCE OK — {passes} checks passed")
