# scored-signals-audit.md — spot-check worksheet for the signal-quality gate (Gate 3, OPEN)

Generated 2026-07-24T16:41:54Z by audit_signals.py from data/verified/scored_signals.json.
This audit does not say pass. It surfaces every signal with its evidence links so a named
human can verify each against the primary source and log the gate decision (P4).

## Counts

- clusters: 6 -> STRONG 5 / WATCH 1 / SKIP 0
- alpha used in classification: False (must be False)

## Per-signal checklist (human: open each filing; verify insider name, date, shares, price)

### STRONG GENB — 4 insiders, $150,060,800, alpha 13.9041

- [ ] `0001193125-26-085855` — https://www.sec.gov/Archives/edgar/data/1780956/000119312526085855/ownership.xml  (sha256 64d35796eaa348f6...)
- [ ] `0001193125-26-085872` — https://www.sec.gov/Archives/edgar/data/1672424/000119312526085872/ownership.xml  (sha256 3d1eef586a340c39...)
- [ ] `0001193125-26-085888` — https://www.sec.gov/Archives/edgar/data/1780951/000119312526085888/ownership.xml  (sha256 151a7ce6ba3c9a40...)
- [ ] `0001193125-26-085898` — https://www.sec.gov/Archives/edgar/data/2109011/000119312526085898/ownership.xml  (sha256 1234df8be6026517...)
- [ ] `0001193125-26-085939` — https://www.sec.gov/Archives/edgar/data/2109144/000119312526085939/ownership.xml  (sha256 bbe062fb1ba680b8...)

### STRONG LRMR — 4 insiders, $25,550,000, alpha -5.4287

- [ ] `0001193125-26-085510` — https://www.sec.gov/Archives/edgar/data/1230482/000119312526085510/ownership.xml  (sha256 6da3288fb91778bb...)
- [ ] `0001193125-26-085514` — https://www.sec.gov/Archives/edgar/data/1242616/000119312526085514/ownership.xml  (sha256 d22de41ceb9ab45e...)
- [ ] `0001193125-26-085515` — https://www.sec.gov/Archives/edgar/data/1374690/000119312526085515/ownership.xml  (sha256 bd569009a6bb8bbb...)
- [ ] `0001193805-26-000205` — https://www.sec.gov/Archives/edgar/data/1374690/000119380526000205/e665206_4-larimar.xml  (sha256 3b51d2af1fefac9d...)

### STRONG CTEV — 3 insiders, $638,625, alpha 22.3451

- [ ] `0001828369-26-000005` — https://www.sec.gov/Archives/edgar/data/1828369/000182836926000005/wk-form4_1772488893.xml  (sha256 1a2b93f7ff1f6da8...)
- [ ] `0001841409-26-000003` — https://www.sec.gov/Archives/edgar/data/1841409/000184140926000003/wk-form4_1772487511.xml  (sha256 17586116afe7db13...)
- [ ] `0002036762-26-000005` — https://www.sec.gov/Archives/edgar/data/2036762/000203676226000005/wk-form4_1772487033.xml  (sha256 983cf0686820b6a4...)

### STRONG TNC — 3 insiders, $1,261,670, alpha 15.5463

- [ ] `0001406019-26-000002` — https://www.sec.gov/Archives/edgar/data/97134/000140601926000002/form4-03022026_100319.xml  (sha256 d801e77bd1ac36d7...)
- [ ] `0001624242-26-000002` — https://www.sec.gov/Archives/edgar/data/97134/000162424226000002/form4-03022026_100335.xml  (sha256 e238c31ac0a02a36...)
- [ ] `0002036886-26-000005` — https://www.sec.gov/Archives/edgar/data/97134/000203688626000005/form4-03022026_100353.xml  (sha256 8f18d111c36da3e8...)

### STRONG LAW — 2 insiders, $188,800, alpha 24.3642

- [ ] `0001625641-26-000063` — https://www.sec.gov/Archives/edgar/data/2019077/000162564126000063/wk-form4_1772490040.xml  (sha256 51c18216577010e8...)
- [ ] `0001625641-26-000065` — https://www.sec.gov/Archives/edgar/data/1439921/000162564126000065/wk-form4_1772490159.xml  (sha256 6b8d2a65af4d89f0...)

### WATCH PVLA — 2 insiders, $800,000, alpha -9.2096

- [ ] `0001104659-26-021921` — https://www.sec.gov/Archives/edgar/data/1583648/000110465926021921/tm267613-1_4seq1.xml  (sha256 c2cf0874d7f86cf2...)
- [ ] `0001104659-26-021922` — https://www.sec.gov/Archives/edgar/data/1583648/000110465926021922/tm267613-2_4seq1.xml  (sha256 801c6f9ac602f493...)

## Anomalies surfaced for the reviewer

- GENB: one member (AFEYAN NOUBAR, director) accounts for $150.0M of the $150.06M total —
  cluster value is dominated by a single large buyer; conviction weighting treats members
  equally regardless of trade size. Judge whether this matches signal intent.
- LAW mean alpha (+24.36) averages 2 trades; CTEV (+22.35) averages 3 — small samples.
- 2 negative-alpha clusters (LRMR -5.43, PVLA -9.21) retained; detector reports what it finds.
- Filings to verify: 19 accession URLs above; every sha256 traces to a fetch manifest.
