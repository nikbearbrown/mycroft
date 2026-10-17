# Form D identity queue

Which EDGAR CIK **is** a universe company. Until a named human answers that, nothing in `form_d_filings` joins to anything, because the alternative — joining on the issuer name — is wrong in a way that produces a plausible table.

## What the scan holds

- **49 quarters** scanned, `2014q1` → `2026q1`.
- **706 issuer rows** carry a universe company's name, filed 2014-01-22 → 2026-03-31.
- **595 of them are self-declared pooled investment vehicles** and are filtered out by the filer's own `ISPOOLEDINVESTMENTFUNDTYPE` flag before a human sees them.
- **46 distinct CIKs** remain as candidates. 0 of them are undecided.

> **Archive gap.** 2008Q2-2013Q4 are not published by the SEC; 2008Q1 and 2012Q1 exist as orphans and are deliberately excluded so that the earliest observed filing is a property of a contiguous archive rather than of which orphan a company happened to appear in.

## The proposals

Every row below is a **model judgment** (P8) and decides nothing. The verdict is whatever a named reviewer records with `--affirm`.

### Proposed `operating_company` (8)

The filed name normalises to the canonical name and carries no pooling token. These are the rows that would actually join.

| CIK | Filed entity name | Company pattern | Filings | First → last | Decided |
|---|---|---|---|---|---|
| `0001181412` | SPACE EXPLORATION TECHNOLOGIES CORP | Space Exploration Technologies Corp. | 19 | 2015-01-26 → 2022-08-05 | yes |
| `0001587468` | Databricks, Inc. | Databricks | 17 | 2014-07-03 → 2025-12-31 | yes |
| `0002002695` | X.AI CORP. | X.AI Corp | 4 | 2023-12-05 → 2025-02-25 | yes |
| `0001609052` | x.ai, inc. | X.AI Corp | 4 | 2014-05-30 → 2017-08-21 | yes |
| `0001686725` | Groq, Inc. | Groq | 3 | 2016-10-20 → 2018-09-05 | yes |
| `0002079267` | X.AI Holdings Corp. | X.AI Corp | 2 | 2025-08-06 → 2026-01-06 | yes |
| `0002014185` | Figure AI Inc. | Figure AI Inc. | 1 | 2024-03-13 → 2024-03-13 | yes |
| `0001972171` | Perplexity AI, Inc. | Perplexity AI | 1 | 2023-04-05 → 2023-04-05 | yes |

### Proposed `vehicle` (12)

Real Form D filers raising real money, named after a universe company and not being it. A vehicle must never be linked to a company: its raise would land on the company's round timeline.

| CIK | Filed entity name | Company pattern | Filings | First → last | Decided |
|---|---|---|---|---|---|
| `0001778383` | Adit Growth Equity Co-Invest, LLC - Series SpaceX-1 | Space Exploration Technologies Corp. | 1 | 2019-06-11 → 2019-06-11 | yes |
| `0001858851` | Adit Growth Equity III Co-Invest, LLC - Series Spacex-1 | Space Exploration Technologies Corp. | 1 | 2021-05-19 → 2021-05-19 | yes |
| `0002020040` | Align AJAX Figure AI Partners LLC | Figure AI Inc. | 1 | 2024-04-26 → 2024-04-26 | yes |
| `0002064427` | Anduril Holdings SPV, LP | Anduril Industries | 1 | 2025-04-17 → 2025-04-17 | yes |
| `0002039651` | Anduril Investors II LLC | Anduril Industries | 1 | 2024-10-09 → 2024-10-09 | yes |
| `0001990112` | Anduril Investors LLC | Anduril Industries | 1 | 2023-09-15 → 2023-09-15 | yes |
| `0001818225` | Community Philanthropic Ventures, LLC | Anthropic PBC | 1 | 2020-07-15 → 2020-07-15 | yes |
| `0002013225` | Eagle VP Fund 2 LLC-Series OpenAI | OpenAI Group PBC | 1 | 2024-03-18 → 2024-03-18 | yes |
| `0002012434` | Eagle VP Fund 2 LLC-Series SpaceX | Space Exploration Technologies Corp. | 1 | 2024-02-16 → 2024-02-16 | yes |
| `0002035722` | Perplexity AI I, a series of WeFunds LLC | Perplexity AI | 1 | 2024-09-30 → 2024-09-30 | yes |
| `0001811324` | SpaceX Series C Secondary Two, a series of Republic Master Fund, LP | Space Exploration Technologies Corp. | 1 | 2020-05-26 → 2020-05-26 | yes |
| `0002094874` | UIT Growth Equity Series SpaceX International I Limited Partnership | Space Exploration Technologies Corp. | 1 | 2025-10-31 → 2025-10-31 | yes |

### Proposed `not_in_universe` (26)

A different company whose name collides with a frozen pattern.

| CIK | Filed entity name | Company pattern | Filings | First → last | Decided |
|---|---|---|---|---|---|
| `0001798355` | Cohere Inc. | Cohere Inc. [FALSE POSITIVE] | 4 | 2019-12-31 → 2023-02-02 | yes |
| `0001998376` | Open Air Hotels & Resorts Inc. | OpenAI Group PBC | 4 | 2023-10-23 → 2024-06-13 | yes |
| `0002049664` | iDox.ai Corp. | X.AI Corp | 4 | 2024-12-23 → 2025-06-11 | yes |
| `0001851745` | Cohere Health Inc. | Cohere Inc. [FALSE POSITIVE] | 3 | 2021-04-14 → 2025-05-22 | yes |
| `0001556546` | GAINSPEED, INC. | Cohere Inc. [FALSE POSITIVE] | 3 | 2014-01-22 → 2015-06-03 | yes |
| `0001993205` | Stax.ai, Inc. | X.AI Corp | 3 | 2023-09-14 → 2024-09-13 | yes |
| `0001760021` | Apex.AI, Inc. | X.AI Corp | 2 | 2018-11-29 → 2021-12-15 | yes |
| `0001636993` | Cohere Technologies, Inc. | Cohere Inc. [FALSE POSITIVE] | 2 | 2015-03-20 → 2021-12-08 | yes |
| `0001891446` | Coherence Technologies Inc. | Cohere Inc. [FALSE POSITIVE] | 2 | 2021-11-02 → 2024-03-15 | yes |
| `0001581078` | Coherent Path Inc. | Cohere Inc. [FALSE POSITIVE] | 2 | 2014-06-26 → 2019-07-05 | yes |
| `0002016453` | CredX.AI, Inc. | X.AI Corp | 2 | 2024-03-21 → 2025-03-18 | yes |
| `0001715301` | Medaptive Health, Inc. | Cohere Inc. [FALSE POSITIVE] | 2 | 2017-10-10 → 2019-05-28 | yes |
| `0002048771` | Mindscale AI Inc. | Scale AI | 2 | 2024-12-31 → 2024-12-31 | yes |
| `0002082894` | BibleX.AI, Inc. | X.AI Corp | 1 | 2025-09-22 → 2025-09-22 | yes |
| `0001306066` | Cohere Communications LLC | Cohere Inc. [FALSE POSITIVE] | 1 | 2014-10-29 → 2014-10-29 | yes |
| `0001889203` | Cohere Network Ltd. | Cohere Inc. [FALSE POSITIVE] | 1 | 2021-12-30 → 2021-12-30 | yes |
| `0001985921` | Coherence Technologies Inc./British Virgin Islands | Cohere Inc. [FALSE POSITIVE] | 1 | 2023-07-20 → 2023-07-20 | yes |
| `0001928109` | Coherent Group Inc. | Cohere Inc. [FALSE POSITIVE] | 1 | 2022-05-11 → 2022-05-11 | yes |
| `0001785532` | Coherent Logix, Inc. | Cohere Inc. [FALSE POSITIVE] | 1 | 2019-08-16 → 2019-08-16 | yes |
| `0001756826` | Cohereum LLC | Cohere Inc. [FALSE POSITIVE] | 1 | 2018-10-24 → 2018-10-24 | yes |
| `0001995560` | Gaingels Databricks 2023 LLC | Databricks | 1 | 2023-11-14 → 2023-11-14 | yes |
| `0002048556` | Gaingels Databricks 2024 LLC | Databricks | 1 | 2024-12-31 → 2024-12-31 | yes |
| `0002021781` | MI SpaceX Investment, LLC | Space Exploration Technologies Corp. | 1 | 2024-05-06 → 2024-05-06 | yes |
| `0001665912` | OPENAIRPLANE INC. | OpenAI Group PBC | 1 | 2016-02-10 → 2016-02-10 | yes |
| `0001813696` | Open Air Resorts - Harker Heights, LP | OpenAI Group PBC | 1 | 2020-06-02 → 2020-06-02 | yes |
| `0002009212` | Siscale AI, Inc. | Scale AI | 1 | 2024-02-20 → 2024-02-20 | yes |

## Evidence, per candidate

**`0001798355` Cohere Inc.** — proposed `not_in_universe`, 4 filing(s)
  - filed name 'COHERE' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, PHOENIX, former names: none; 4 Form D filings 2019-12-31 → 2023-02-02

**`0002049664` iDox.ai Corp.** — proposed `not_in_universe`, 4 filing(s)
  - filed name 'IDOX.AI' != canonical 'X.AI'
  - EDGAR: incorporated DE, FREMONT, former names: none; 4 Form D filings 2024-12-23 → 2025-04-29

**`0001998376` Open Air Hotels & Resorts Inc.** — proposed `not_in_universe`, 4 filing(s)
  - filed name 'OPEN AIR HOTELS AND RESORTS' != canonical 'OPENAI GROUP'
  - EDGAR: incorporated DE, JERSEY CITY, former names: Open Air Hotels & Resorts Inc.; 5 Form D filings 2023-10-23 → 2023-10-23

**`0001851745` Cohere Health Inc.** — proposed `not_in_universe`, 3 filing(s)
  - filed name 'COHERE HEALTH' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, BOSTON, former names: none; 3 Form D filings 2021-04-14 → 2025-05-22

**`0001556546` GAINSPEED, INC.** — proposed `not_in_universe`, 3 filing(s)
  - filed name 'GAINSPEED' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, SUNNYVALE, former names: COHERE NETWORKS, INC.; 5 Form D filings 2012-09-26 → 2015-01-07

**`0001993205` Stax.ai, Inc.** — proposed `not_in_universe`, 3 filing(s)
  - filed name 'STAX.AI' != canonical 'X.AI'
  - EDGAR: incorporated DE, SCOTTSDALE, former names: none; 3 Form D filings 2023-09-14 → 2024-09-13

**`0001760021` Apex.AI, Inc.** — proposed `not_in_universe`, 2 filing(s)
  - filed name 'APEX.AI' != canonical 'X.AI'
  - EDGAR: incorporated DE, PALO ALTO, former names: none; 2 Form D filings 2018-11-29 → 2021-12-15

**`0001636993` Cohere Technologies, Inc.** — proposed `not_in_universe`, 2 filing(s)
  - filed name 'COHERE TECHNOLOGIES' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, SANTA CLARA, former names: none; 2 Form D filings 2015-03-20 → 2021-12-08

**`0001891446` Coherence Technologies Inc.** — proposed `not_in_universe`, 2 filing(s)
  - filed name 'COHERENCE TECHNOLOGIES' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, NEW YORK, former names: none; 2 Form D filings 2021-11-02 → 2024-03-15

**`0001581078` Coherent Path Inc.** — proposed `not_in_universe`, 2 filing(s)
  - filed name 'COHERENT PATH' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, ARLINGTON, former names: none; 3 Form D filings 2013-07-10 → 2019-07-05

**`0002016453` CredX.AI, Inc.** — proposed `not_in_universe`, 2 filing(s)
  - filed name 'CREDX.AI' != canonical 'X.AI'
  - EDGAR: incorporated DE, MERRITT ISLAND, former names: none; 2 Form D filings 2024-03-21 → 2024-03-21

**`0001715301` Medaptive Health, Inc.** — proposed `not_in_universe`, 2 filing(s)
  - filed name 'MEDAPTIVE HEALTH' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, NEW YORK, former names: none; 2 Form D filings 2017-10-10 → 2017-10-10

**`0002048771` Mindscale AI Inc.** — proposed `not_in_universe`, 2 filing(s)
  - filed name 'MINDSCALE AI' != canonical 'SCALE AI'
  - EDGAR: incorporated DE, SAN FRANCISCO, former names: none; 2 Form D filings 2024-12-31 → 2024-12-31

**`0002082894` BibleX.AI, Inc.** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'BIBLEX.AI' != canonical 'X.AI'
  - EDGAR: incorporated DE, SPRINGFIELD, former names: none; 1 Form D filings 2025-09-22 → 2025-09-22

**`0001306066` Cohere Communications LLC** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'COHERE COMMUNICATIONS' != canonical 'COHERE FALSE POSITIVE'
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, NEW YORK, former names: none; 1 Form D filings 2014-10-29 → 2014-10-29

**`0001889203` Cohere Network Ltd.** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'COHERE NETWORK' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, LEWES, former names: none; 1 Form D filings 2021-12-30 → 2021-12-30

**`0001985921` Coherence Technologies Inc./British Virgin Islands** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'COHERENCE TECHNOLOGIES BRITISH VIRGIN ISLANDS' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated D8, ROAD TOWN, TORTOLA, former names: none; 1 Form D filings 2023-07-20 → 2023-07-20

**`0001928109` Coherent Group Inc.** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'COHERENT GROUP' != canonical 'COHERE FALSE POSITIVE'
  - entity type is 'Other'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated E9, TAMPA, former names: none; 1 Form D filings 2022-05-11 → 2022-05-11

**`0001785532` Coherent Logix, Inc.** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'COHERENT LOGIX' != canonical 'COHERE FALSE POSITIVE'
  - EDGAR: incorporated DE, AUSTIN, former names: none; 1 Form D filings 2019-08-16 → 2019-08-16

**`0001756826` Cohereum LLC** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'COHEREUM' != canonical 'COHERE FALSE POSITIVE'
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated MN, EDINA, former names: none; 1 Form D filings 2018-10-24 → 2018-10-24

**`0001995560` Gaingels Databricks 2023 LLC** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'GAINGELS DATABRICKS 2023' != canonical 'DATABRICKS'
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated VT, BURLINGTON, former names: none; 1 Form D filings 2023-11-14 → 2023-11-14

**`0002048556` Gaingels Databricks 2024 LLC** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'GAINGELS DATABRICKS 2024' != canonical 'DATABRICKS'
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated VT, BURLINGTON, former names: none; 1 Form D filings 2024-12-31 → 2024-12-31

**`0002021781` MI SpaceX Investment, LLC** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'MI SPACEX INVESTMENT' != canonical 'SPACE EXPLORATION TECHNOLOGIES'
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated MI, BIRMINGHAM, former names: none; 1 Form D filings 2024-05-06 → 2024-05-06

**`0001813696` Open Air Resorts - Harker Heights, LP** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'OPEN AIR RESORTS HARKER HEIGHTS' != canonical 'OPENAI GROUP'
  - entity type is 'Limited Partnership'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated TX, HARKER HEIGHTS, former names: none; 1 Form D filings 2020-06-02 → 2020-06-02

**`0001665912` OPENAIRPLANE INC.** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'OPENAIRPLANE' != canonical 'OPENAI GROUP'
  - EDGAR: incorporated DE, CHICAGO, former names: none; 1 Form D filings 2016-02-10 → 2016-02-10

**`0002009212` Siscale AI, Inc.** — proposed `not_in_universe`, 1 filing(s)
  - filed name 'SISCALE AI' != canonical 'SCALE AI'
  - EDGAR: incorporated DE, DOVER, former names: none; 1 Form D filings 2024-02-20 → 2024-02-20

**`0001181412` SPACE EXPLORATION TECHNOLOGIES CORP** — proposed `operating_company`, 19 filing(s)
  - filed name normalises to the canonical name ('SPACE EXPLORATION TECHNOLOGIES')
  - EDGAR: incorporated TX, STARBASE, former names: none; 21 Form D filings 2009-03-31 → 2022-08-05

**`0001587468` Databricks, Inc.** — proposed `operating_company`, 17 filing(s)
  - filed name normalises to the canonical name ('DATABRICKS')
  - EDGAR: incorporated DE, SAN FRANCISCO, former names: none; 20 Form D filings 2013-09-25 → 2026-08-27

**`0002002695` X.AI CORP.** — proposed `operating_company`, 4 filing(s)
  - filed name normalises to the canonical name ('X.AI')
  - EDGAR: incorporated NV, PALO ALTO, former names: none; 4 Form D filings 2023-12-05 → 2025-02-25

**`0001609052` x.ai, inc.** — proposed `operating_company`, 4 filing(s)
  - filed name normalises to the canonical name ('X.AI')
  - EDGAR: incorporated DE, NEW YORK, former names: none; 4 Form D filings 2014-05-30 → 2017-08-21

**`0001686725` Groq, Inc.** — proposed `operating_company`, 3 filing(s)
  - filed name normalises to the canonical name ('GROQ')
  - EDGAR: incorporated DE, SAN JOSE, former names: Groq, Inc.; 4 Form D filings 2016-10-20 → 2026-07-24

**`0002079267` X.AI Holdings Corp.** — proposed `operating_company`, 2 filing(s)
  - filed name normalises to the canonical name ('X.AI')
  - EDGAR: incorporated NV, PALO ALTO, former names: none; 2 Form D filings 2025-08-06 → 2026-01-06

**`0002014185` Figure AI Inc.** — proposed `operating_company`, 1 filing(s)
  - filed name normalises to the canonical name ('FIGURE AI')
  - EDGAR: incorporated DE, SUNNYVALE, former names: none; 1 Form D filings 2024-03-13 → 2024-03-13

**`0001972171` Perplexity AI, Inc.** — proposed `operating_company`, 1 filing(s)
  - filed name normalises to the canonical name ('PERPLEXITY AI')
  - EDGAR: incorporated DE, SAN FRANCISCO, former names: none; 1 Form D filings 2023-04-05 → 2023-04-05

**`0001778383` Adit Growth Equity Co-Invest, LLC - Series SpaceX-1** — proposed `vehicle`, 1 filing(s)
  - filed name 'ADIT GROWTH EQUITY INVEST SERIES SPACEX 1' != canonical 'SPACE EXPLORATION TECHNOLOGIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Other'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, NEW YORK, former names: none; 1 Form D filings 2019-06-11 → 2019-06-11

**`0001858851` Adit Growth Equity III Co-Invest, LLC - Series Spacex-1** — proposed `vehicle`, 1 filing(s)
  - filed name 'ADIT GROWTH EQUITY III INVEST SERIES SPACEX 1' != canonical 'SPACE EXPLORATION TECHNOLOGIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, NEW YORK, former names: none; 2 Form D filings 2021-05-19 → 2021-05-19

**`0002020040` Align AJAX Figure AI Partners LLC** — proposed `vehicle`, 1 filing(s)
  - filed name 'ALIGN AJAX FIGURE AI PARTNERS' != canonical 'FIGURE AI'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, SPARTA, former names: none; 1 Form D filings 2024-04-26 → 2024-04-26

**`0002064427` Anduril Holdings SPV, LP** — proposed `vehicle`, 1 filing(s)
  - filed name 'ANDURIL SPV' != canonical 'ANDURIL INDUSTRIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Limited Partnership'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, NEW YORK, former names: none; 1 Form D filings 2025-04-17 → 2025-04-17

**`0002039651` Anduril Investors II LLC** — proposed `vehicle`, 1 filing(s)
  - filed name 'ANDURIL INVESTORS II' != canonical 'ANDURIL INDUSTRIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, BETHESDA, former names: none; 1 Form D filings 2024-10-09 → 2024-10-09

**`0001990112` Anduril Investors LLC** — proposed `vehicle`, 1 filing(s)
  - filed name 'ANDURIL INVESTORS' != canonical 'ANDURIL INDUSTRIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, BETHESDA, former names: none; 1 Form D filings 2023-09-15 → 2023-09-15

**`0001818225` Community Philanthropic Ventures, LLC** — proposed `vehicle`, 1 filing(s)
  - filed name 'COMMUNITY PHILANTHROPIC VENTURES' != canonical 'ANTHROPIC'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated CO, BROOMFIELD, former names: none; 1 Form D filings 2020-07-15 → 2020-07-15

**`0002013225` Eagle VP Fund 2 LLC-Series OpenAI** — proposed `vehicle`, 1 filing(s)
  - filed name 'EAGLE VP FUND 2 SERIES OPENAI' != canonical 'OPENAI GROUP'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, NEW YORK, former names: none; 1 Form D filings 2024-03-18 → 2024-03-18

**`0002012434` Eagle VP Fund 2 LLC-Series SpaceX** — proposed `vehicle`, 1 filing(s)
  - filed name 'EAGLE VP FUND 2 SERIES SPACEX' != canonical 'SPACE EXPLORATION TECHNOLOGIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Investing', which is an investing activity rather than an operating one
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, NEW YORK, former names: none; 1 Form D filings 2024-02-16 → 2024-02-16

**`0002035722` Perplexity AI I, a series of WeFunds LLC** — proposed `vehicle`, 1 filing(s)
  - filed name 'PERPLEXITY AI I A SERIES OF WEFUNDS' != canonical 'PERPLEXITY AI'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - entity type is 'Limited Liability Company'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, HENDERSON, former names: none; 1 Form D filings 2024-09-30 → 2024-09-30

**`0001811324` SpaceX Series C Secondary Two, a series of Republic Master Fund, LP** — proposed `vehicle`, 1 filing(s)
  - filed name 'SPACEX SERIES C SECONDARY TWO A SERIES OF REPUBLIC MASTER FUND' != canonical 'SPACE EXPLORATION TECHNOLOGIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Pooled Investment Fund', which is an investing activity rather than an operating one
  - entity type is 'Limited Partnership'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated DE, SALT LAKE CITY, former names: none; 2 Form D filings 2020-05-26 → 2020-05-26

**`0002094874` UIT Growth Equity Series SpaceX International I Limited Partnership** — proposed `vehicle`, 1 filing(s)
  - filed name 'UIT GROWTH EQUITY SERIES SPACEX INTERNATIONAL I PARTNERSHIP' != canonical 'SPACE EXPLORATION TECHNOLOGIES'
  - entity name carries a pooling token (a series, fund, SPV, co-invest or investors vehicle)
  - industry group is 'Pooled Investment Fund', which is an investing activity rather than an operating one
  - entity type is 'Limited Partnership'; an operating company in this universe files as a Corporation
  - EDGAR: incorporated A6, TORONTO, former names: none; 1 Form D filings 2025-10-31 → 2025-10-31

## Decisions recorded so far

| Verdict | CIKs |
|---|---|
| `not_in_universe` | 27 |
| `operating_company` | 7 |
| `vehicle` | 12 |
