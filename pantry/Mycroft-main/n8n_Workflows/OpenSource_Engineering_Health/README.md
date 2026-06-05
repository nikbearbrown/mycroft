## Sub-task 2: Engineering maturity scoring

### Inputs
Raw repo snapshots (JSON):
- data/sample_raw/*.json

### Run analysis
From OpenSource_Engineering_Health directory:

python3 scripts/analyze_oss_health.py \
  --raw-dir data/sample_raw \
  --out-dir outputs/example

### Outputs
- outputs/example/oss_signals.csv  (per-repo signals + computed features)
- outputs/example/oss_scores.csv   (ranked scores)
- outputs/example/ossreport.md     (comparison report)

### Scoring model (0–100)
Popularity (0–40) + Activity (0–30) + Issue Health (0–20) + License (0–10)

Notes:
- Popularity is normalized within the current repo set (log scale).
- Issue health uses issue density (issues per 1k stars) as a proxy.
