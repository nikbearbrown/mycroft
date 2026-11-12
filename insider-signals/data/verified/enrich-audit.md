# Enrich audit (G3)

Run at 2026-11-10T00:10:55+00:00 by `enrich.py`. This audit reports what was found. The halting checks decide promotion; clearing G3 is the owner's logged decision.

- Input: `data/verified/insider_buys.csv`, 78,495 buys, SHA-256 `a7ec55298bf886c0090f7c5fc4e93bfb18faeabc5d4c407db8d77abefdb75b16`
- Prices: Yahoo Finance via yfinance (adjusted close, auto_adjust=False); requested 2023-03-24 to 2026-11-09 (end exclusive); market calendar = SPY bars, last bar **2026-11-06**
- Rules: windows 21, 63 trading days; minimum coverage 80% (PRE_REGISTRATION.md Rules 7-9 (2026-11-09))
- **Promoted:** `data/verified/enriched_buys.csv` (SHA-256 `fa14627333ac754a7f904e3417e5475241d7523659d46d6385779a7c65295bde`)

**Returns are computed per buy in the enriched file but not summarized here:** no averages or other return statistics are reported before the signals are registered.

## Halting checks

| Check | Result | Violations | Detail |
|---|---|---:|---|
| input_hash | PASS | 0 | insider_buys.csv SHA-256 = insider_buys_sha256 (G2) |
| spy_present | PASS | 0 | SPY cached and covering the first entry day |
| cache_consistent | PASS | 0 | every symbol fetched for [2023-03-24, 2026-11-09) like SPY |
| status_complete | PASS | 0 | every buy has a known status; no number without a closed window |
| lookahead | PASS | 0 | entry = first SPY day after FILING_DATE; exit = entry + N SPY days |
| filing_price_check | PASS | 0 | filed price within 25% of the split-adjusted unadjusted close on TRANS_DATE, else price_mismatch_vs_filing (Rule 9) |
| coverage | PASS | 0 | priced ÷ verified buys = 80.09% (minimum 80%, Rule 8) |

## Price coverage (priced ÷ verified buys)

| Quarter | Buys | Priced | Coverage |
|---|---:|---:|---:|
| 2023q2 | 7,964 | 5,701 | 71.58% |
| 2023q3 | 5,785 | 4,326 | 74.78% |
| 2023q4 | 6,240 | 4,650 | 74.52% |
| 2024q1 | 5,214 | 3,967 | 76.08% |
| 2024q2 | 5,444 | 4,227 | 77.65% |
| 2024q3 | 5,070 | 4,003 | 78.95% |
| 2024q4 | 5,983 | 4,726 | 78.99% |
| 2025q1 | 5,285 | 4,243 | 80.28% |
| 2025q2 | 6,297 | 5,268 | 83.66% |
| 2025q3 | 4,788 | 4,137 | 86.40% |
| 2025q4 | 5,313 | 4,648 | 87.48% |
| 2026q1 | 4,817 | 4,186 | 86.90% |
| 2026q2 | 5,180 | 4,493 | 86.74% |
| 2026q3 | 5,115 | 4,293 | 83.93% |
| **All** | 78,495 | 62,868 | 80.09% |

## price_status

| Status | Buys | Share |
|---|---:|---:|
| priced | 62,868 | 80.09% |
| placeholder_symbol | 2,945 | 3.75% |
| multiple_symbols | 175 | 0.22% |
| unparseable_symbol | 298 | 0.38% |
| no_data | 8,832 | 11.25% |
| series_starts_after_entry | 1,014 | 1.29% |
| no_bar_on_entry_date | 11 | 0.01% |
| price_mismatch_vs_filing | 2,352 | 3.00% |

By quarter:

| Quarter | priced | placeholder_symbol | multiple_symbols | unparseable_symbol | no_data | series_starts_after_entry | no_bar_on_entry_date | price_mismatch_vs_filing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023q2 | 5,701 | 138 | 34 | 21 | 1,800 | 88 | 0 | 182 |
| 2023q3 | 4,326 | 211 | 15 | 21 | 999 | 57 | 0 | 156 |
| 2023q4 | 4,650 | 192 | 13 | 15 | 1,143 | 53 | 1 | 173 |
| 2024q1 | 3,967 | 238 | 16 | 16 | 816 | 29 | 0 | 132 |
| 2024q2 | 4,227 | 196 | 13 | 15 | 775 | 69 | 0 | 149 |
| 2024q3 | 4,003 | 172 | 3 | 6 | 703 | 55 | 0 | 128 |
| 2024q4 | 4,726 | 222 | 15 | 28 | 780 | 79 | 0 | 133 |
| 2025q1 | 4,243 | 212 | 5 | 12 | 567 | 113 | 0 | 133 |
| 2025q2 | 5,268 | 192 | 0 | 23 | 531 | 163 | 0 | 120 |
| 2025q3 | 4,137 | 277 | 2 | 5 | 202 | 79 | 1 | 85 |
| 2025q4 | 4,648 | 237 | 25 | 10 | 181 | 65 | 3 | 144 |
| 2026q1 | 4,186 | 245 | 18 | 4 | 169 | 63 | 2 | 130 |
| 2026q2 | 4,493 | 198 | 0 | 39 | 102 | 48 | 0 | 300 |
| 2026q3 | 4,293 | 215 | 16 | 83 | 64 | 53 | 4 | 387 |

## Window 21d: window status

| Quarter | closed | no_entry_price | series_ends_before_exit |
|---|---:|---:|---:|
| 2023q2 | 5,701 | 2,263 | 0 |
| 2023q3 | 4,326 | 1,459 | 0 |
| 2023q4 | 4,650 | 1,590 | 0 |
| 2024q1 | 3,967 | 1,247 | 0 |
| 2024q2 | 4,227 | 1,217 | 0 |
| 2024q3 | 4,003 | 1,067 | 0 |
| 2024q4 | 4,726 | 1,257 | 0 |
| 2025q1 | 4,243 | 1,042 | 0 |
| 2025q2 | 5,268 | 1,029 | 0 |
| 2025q3 | 4,137 | 651 | 0 |
| 2025q4 | 4,648 | 665 | 0 |
| 2026q1 | 4,186 | 631 | 0 |
| 2026q2 | 4,493 | 687 | 0 |
| 2026q3 | 4,289 | 822 | 4 |
| **All** | **62,864** | **15,627** | **4** |

## Window 63d: window status

| Quarter | closed | not_yet_closed | no_entry_price |
|---|---:|---:|---:|
| 2023q2 | 5,701 | 0 | 2,263 |
| 2023q3 | 4,326 | 0 | 1,459 |
| 2023q4 | 4,650 | 0 | 1,590 |
| 2024q1 | 3,967 | 0 | 1,247 |
| 2024q2 | 4,227 | 0 | 1,217 |
| 2024q3 | 4,003 | 0 | 1,067 |
| 2024q4 | 4,726 | 0 | 1,257 |
| 2025q1 | 4,243 | 0 | 1,042 |
| 2025q2 | 5,268 | 0 | 1,029 |
| 2025q3 | 4,137 | 0 | 651 |
| 2025q4 | 4,648 | 0 | 665 |
| 2026q1 | 4,186 | 0 | 631 |
| 2026q2 | 4,493 | 0 | 687 |
| 2026q3 | 1,179 | 3,114 | 822 |
| **All** | **59,754** | **3,114** | **15,627** |

## Filed price vs market close (Rule 9)

Checked 65,220 buys priced at entry: ok 61,688 · **mismatch 2,352** (→ `price_mismatch_vs_filing`, no returns) · not checkable 1,180 (no bar on or before the trade date). A split adjustment was applied to 6,484 checked buys. Mismatches come from 535 issuers.

Mismatches by filed price:

| Filed price | Buys |
|---|---:|
| ≥ $20 | 920 |
| $5–20 | 597 |
| $1–5 | 422 |
| < $1 | 413 |

Mismatches by filed price ÷ reference close:

| Filed price ÷ reference close | Buys |
|---|---:|
| filed 50–75% of close | 635 |
| filed 10–50% of close | 549 |
| filed 125–200% of close | 430 |
| filed 2–10× close | 348 |
| filed > 10× close | 274 |
| filed < 10% of close | 116 |

Mismatches by parse flags (rule 1):

| PARSE flags (Rule 1) | Buys |
|---|---:|
| no flag | 1,897 |
| private | 236 |
| espp_or_drip | 219 |

Mismatches by split adjustment applied:

| Split adjustment applied | Buys |
|---|---:|
| no | 1,926 |
| yes | 426 |

Mismatches by reference bar before the trade date:

| Reference bar before the trade date | Buys |
|---|---:|
| same day | 2,289 |
| 1–3 days | 63 |

Mismatches by document type:

| Document type | Buys |
|---|---:|
| 4 | 2,312 |
| 4/A | 40 |

Mismatches by quarter:

| Quarter | Buys |
|---|---:|
| 2023q2 | 182 |
| 2023q3 | 156 |
| 2023q4 | 173 |
| 2024q1 | 132 |
| 2024q2 | 149 |
| 2024q3 | 128 |
| 2024q4 | 133 |
| 2025q1 | 133 |
| 2025q2 | 120 |
| 2025q3 | 85 |
| 2025q4 | 144 |
| 2026q1 | 130 |
| 2026q2 | 300 |
| 2026q3 | 387 |

Issuers with the most mismatches:

| Issuer CIK | Issuer | Symbol | Buys |
|---|---|---|---:|
| 0001046179 | TAIWAN SEMICONDUCTOR MANUFACTURING CO LTD | TSM | 211 |
| 0001562401 | American Homes 4 Rent | AMH | 79 |
| 0000040417 | GENERAL AMERICAN INVESTORS CO INC | GAM | 72 |
| 0001332551 | ACRES Commercial Realty Corp. | ACR | 51 |
| 0000707388 | STAR EQUITY HOLDINGS, INC. | STRR | 45 |
| 0000082473 | INNSUITES HOSPITALITY TRUST | IHT | 34 |
| 0001726173 | Biglari Holdings Inc. | BH | 31 |
| 0002115119 | Columbia Financial, Inc./MD/ | CLBK | 30 |
| 0001487718 | AMERICAN BATTERY MATERIALS, INC. | BLTH | 29 |
| 0001160330 | BANK BRADESCO | BBD | 28 |
| 0001895249 | ConnectM Technology Solutions, Inc. | CNTM | 24 |
| 0001268884 | CBRE GLOBAL REAL ESTATE INCOME FUND | IGR | 22 |
| 0001712184 | Liberty Latin America Ltd. | LILA | 21 |
| 0001539850 | Starco Brands, Inc. | STCB | 20 |
| 0001505497 | BioRestorative Therapies, Inc. | BRTX | 19 |
| 0001011060 | Nordicus Partners Corp | NORD | 18 |
| 0001754195 | Trulieve Cannabis Corp. | TRUL | 18 |
| 0001345099 | MESOBLAST LTD | MESO | 18 |
| 0001408534 | First Guaranty Bancshares, Inc. | FGBI | 18 |
| 0001538495 | Earth Science Tech, Inc. | ETST | 17 |

## Symbols

- Distinct symbols requested from the buys: 4,640; price cache: no_data 808, ok 3,833
- Symbols used by more than one issuer CIK: 32 (729 buys). The symbol is as filed and is not checked against the issuer; a shared symbol may be a reuse after a rename or a filing error.
- Issuers filing under more than one symbol: 183

Unusual symbols as filed (not priced; not mapped):

| ticker_as_filed | price_status | Buys |
|---|---|---:|
| `NONE` | placeholder_symbol | 2,256 |
| `N/A` | placeholder_symbol | 561 |
| `AXIA3` | unparseable_symbol | 50 |
| `RANGER` | unparseable_symbol | 50 |
| `PPTINC` | unparseable_symbol | 48 |
| `none` | placeholder_symbol | 44 |
| `PRTFTM` | unparseable_symbol | 40 |
| `GEF, GEF-B` | multiple_symbols | 36 |
| `None` | placeholder_symbol | 35 |
| `NA` | placeholder_symbol | 34 |
| `HEI, HEI.A` | multiple_symbols | 32 |
| `SQFT,SQFTP` | multiple_symbols | 22 |
| `LEN, LEN.B` | multiple_symbols | 22 |
| `GEF,GEF.B` | multiple_symbols | 22 |
| `NASDAQ:DHC` | unparseable_symbol | 14 |
| `BCDA;BCDAW` | multiple_symbols | 12 |
| `SNV PRE` | unparseable_symbol | 11 |
| `NYSE:NYCB` | unparseable_symbol | 9 |
| `DMA; MSFIX` | multiple_symbols | 9 |
| `WLY, WLYB` | multiple_symbols | 7 |
| `WLY/WLYB` | unparseable_symbol | 7 |
| `JUSH/JUSHF` | unparseable_symbol | 7 |
| `NASDAQ:SVC` | unparseable_symbol | 7 |
| `N O G` | unparseable_symbol | 7 |
| `UHAL,UHALB` | multiple_symbols | 6 |
| `N.A.` | placeholder_symbol | 5 |
| `[NONE]` | placeholder_symbol | 5 |
| `AB-Lend` | unparseable_symbol | 5 |
| `NYSE:EVC` | unparseable_symbol | 4 |
| `CETXP,CETX` | multiple_symbols | 4 |
| `ASX:LNW` | unparseable_symbol | 4 |
| `BBXIA/B` | unparseable_symbol | 3 |
| `SNV PrE` | unparseable_symbol | 3 |
| `MDBH?` | unparseable_symbol | 3 |
| `SHFS)` | unparseable_symbol | 2 |
| `[ N/A ]` | placeholder_symbol | 2 |
| `[ NONE ]` | placeholder_symbol | 2 |
| `NYSE/TRN` | unparseable_symbol | 2 |
| `[HURC` | unparseable_symbol | 2 |
| `[ENTX]` | unparseable_symbol | 2 |
| `CSAN3` | unparseable_symbol | 2 |
| `9qgnc@ry` | unparseable_symbol | 1 |
| `HLBZ,HLBZW` | multiple_symbols | 1 |
| `PARAA,PARA` | multiple_symbols | 1 |
| `BFRG,BFRGW` | multiple_symbols | 1 |
| `PREDEX` | unparseable_symbol | 1 |
| `HYAC U` | unparseable_symbol | 1 |
| `(SIRI)` | unparseable_symbol | 1 |
| `UHAL UHALB` | unparseable_symbol | 1 |
| `(CALX)` | unparseable_symbol | 1 |
| `[NONE` | placeholder_symbol | 1 |
| `CCIX U` | unparseable_symbol | 1 |
| `NCLH]` | unparseable_symbol | 1 |
| `xw#w6qqr` | unparseable_symbol | 1 |
| `GTII/GTBIF` | unparseable_symbol | 1 |
| `NYSE: KRC` | unparseable_symbol | 1 |
| `pm2c#xro` | unparseable_symbol | 1 |
| `LBRA]` | unparseable_symbol | 1 |
| `CLBR U` | unparseable_symbol | 1 |
| `NYSE:FLG` | unparseable_symbol | 1 |
| `CFTR-PRA` | unparseable_symbol | 1 |

Issuers with the most unpriced buys (no data or a series that does not cover entry):

| Issuer CIK | Issuer | Symbol | price_status | Buys |
|---|---|---|---|---:|
| 0000867028 | FOMO WORLDWIDE, INC. | FOMC | no_data | 242 |
| 0001836057 | BlackRock Innovation & Growth Term Trust | BIGZ | no_data | 195 |
| 0001072627 | KINGSWAY FINANCIAL SERVICES INC | KFS | no_data | 150 |
| 0001077428 | TEXAS CAPITAL BANCSHARES INC/TX | TCBI | no_data | 138 |
| 0001842939 | Carmell Corp | CTCX | no_data | 124 |
| 0001562733 | Synergy CHC Corp. | SNYR | series_starts_after_entry | 123 |
| 0000102109 | UNIVERSAL SAFETY PRODUCTS, INC. | UUU | series_starts_after_entry | 114 |
| 0001258943 | PIONEER MUNICIPAL HIGH INCOME ADVANTAGE FUND, INC. | MAV | no_data | 113 |
| 0001372807 | Portman Ridge Finance Corp | PTMN | no_data | 109 |
| 0001339688 | LION COPPER & GOLD CORP. | LCGMF | series_starts_after_entry | 96 |
| 0001938109 | Pineapple Financial Inc. | PAPL | series_starts_after_entry | 90 |
| 0000883107 | NANOPHASE TECHNOLOGIES Corp | NANX | no_data | 86 |
| 0000893739 | 180 DEGREE CAPITAL CORP. /NY/ | TURN | no_data | 83 |
| 0001223026 | PIONEER MUNICIPAL HIGH INCOME FUND, INC. | MHI | no_data | 82 |
| 0001756908 | PIMCO Energy & Tactical Credit Opportunities Fund | NRGX | no_data | 76 |
| 0000929351 | LIONS GATE ENTERTAINMENT CORP /CN/ | LGF | no_data | 75 |
| 0000740971 | OLD POINT FINANCIAL CORP | OPOF | no_data | 71 |
| 0000101594 | US ENERGY CORP | USEG | no_data | 71 |
| 0001313275 | BRIGHTCOVE INC | BCOV | no_data | 70 |
| 0001220754 | ModivCare Inc | MODV | no_data | 67 |
| 0000020520 | Frontier Communications Parent, Inc. | FYBR | no_data | 65 |
| 0000725394 | DALRADA FINANCIAL CORP | DFCO | no_data | 63 |
| 0001930313 | Pono Capital Two, Inc. | PTWO | no_data | 63 |
| 0001864290 | Pioneer Municipal High Income Opportunities Fund, Inc. | MIO | no_data | 61 |
| 0001104038 | VerifyMe, Inc. | VRME | no_data | 58 |

## Fetch

- Splits (Rule 9): 3,741 symbols with a priced buy; range 2023-03-24 to 2026-11-10 (end exclusive). This run requested 0 (ok 0, no data 0, errors 0, refusals 0).
- This run: 0 symbols requested in 0 batches; ok 0, no data 0, errors 0, refusals 0. Every batch is in `data/raw/prices/fetch_log.jsonl`.
- All runs (`fetch_log.jsonl`): 211 batch requests, 8,382 symbol requests, 0 refused; 2026-11-09T23:18:21+00:00 to 2026-11-10T00:10:11+00:00.
- Yahoo Finance is not an authoritative source; adjusted closes reflect Yahoo's adjustments as of the fetch date (`prices_manifest.json`, `fetched_at`).
