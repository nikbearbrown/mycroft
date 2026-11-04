# Conformance audit (G2) — 2026q3

Run at 2026-11-04T17:49:19.368Z by `conformance.py`. This audit reports what was found. The halting checks decide promotion; clearing G2 is the owner's logged decision.

**Promoted:** 5,115 rows → `data/verified/insider_buys.csv` (SHA-256 `dead8bee1a423dd97028b8e643b3e1ad24185c138cc7f3cad2410b1c86026e07`).

## Halting checks

| Quarter | Check | Result | Violations | Detail |
|---|---|---|---:|---|
| 2026q3 | hash | PASS | 0 | manifest SHA-256 a4e6a681cfcfa43a3d9e4ca9cfec1fd26a59d0a01eac7e9f7b5a0122092c90f3 |
| 2026q3 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2026q3 | keys | PASS | 0 | 59,885 NONDERIV_TRANS keys, 5,115 buys |
| 2026q3 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2026q3 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2026q3 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,115 buys; buys file: 5,115 |
| 2026q3 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |

## Findings — 2026q3

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 59,834 |
| … code P | 5,183 |
| … qualifying buys (PARSE) | 5,115 |
| … promoted to verified | 5,115 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_missing` | 4 |
| `code_A_grant_award` | 9,791 |
| `code_C_conversion` | 902 |
| `code_D_disposition_to_issuer` | 1,382 |
| `code_F_tax_or_exercise_payment` | 6,801 |
| `code_G_gift` | 1,033 |
| `code_I_discretionary_16b3f` | 23 |
| `code_J_other` | 1,672 |
| `code_L_small_acquisition` | 63 |
| `code_M_option_exercise_16b3` | 7,433 |
| `code_O_option_exercise_otm` | 1 |
| `code_S_sale` | 25,430 |
| `code_U_tender_change_of_control` | 38 |
| `code_W_will_or_descent` | 14 |
| `code_X_option_exercise_itm` | 56 |
| `code_Z_voting_trust` | 8 |
| `p_not_acquired` | 6 |
| `p_shares_missing_or_not_positive` | 8 |
| `p_price_missing_or_not_positive` | 53 |
| `p_equity_swap` | 1 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 336 |
| … private flag | 135 |
| … ESPP/DRIP flag | 201 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 136 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **4,779** |

### Amendments (4/A)

- 144 promoted buys come from 92 Form 4/A filings.
- Original filing found in this quarter (same issuer, same owners, filed on `DATE_OF_ORIG_SUB`): unique 65, none_in_quarter 27.
- Amendment buys that repeat a buy in a candidate original (same trade date, shares and price): **42**. These may be the same purchase counted twice.
- Resolution: each amendment is kept as its own dated event at its own `FILING_DATE`; it is not linked to or merged with an original. The matching rule is recipe `[TODO: DEV]` 3, still open.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 165 | 41 |
| `N/A` | 45 | 21 |
| `NA` | 3 | 1 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,095, `E` 20.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 791, of which 791 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 6 | 342 | 7,308 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 662 | 2,565 | 1,313 | 360 | 170 | 45 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

686 buys from 231 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,429, 2: 275, 3: 85, 4: 99, 5: 75, 6: 132, 7: 7, 8: 5, 9: 8.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 588 buys are priced below $1.00 and 92 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 2
- Unparseable dates: 0
- Code blank or not in SEC's list: 4
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0

## Spot-check against the individual filings

25 buys drawn at random (seed `14553824015086086844`, derived from the source ZIP hashes). Each filing's Form 4 XML was compared with the data set. **15 of 25 match exactly** on code, shares, price and date; **10** differ only because the data set rounds shares or price to 2 decimals; **0** differ in another way. Requests to SEC this run: 0 (1/s, logged in `data/raw/filings/request_log.jsonl`). Mismatches are listed, not corrected.

| # | Accession | Form | Issuer | Data set (code · shares · price · date) | Filing XML | Code | Shares | Price | Date | Result |
|---:|---|---|---|---|---|:-:|:-:|:-:|:-:|---|
| 1 | [0001628873-26-000057](https://www.sec.gov/Archives/edgar/data/1059213/000162887326000057/0001628873-26-000057.txt) | 4 | BEXIL INVESTMENT TRUST | P · 5000.0 · 17.78 · 2026-08-10 | P · 5000 · 17.78 · 2026-08-10 | ✓ | ✓ | ✓ | ✓ | match |
| 2 | [0001422493-26-000012](https://www.sec.gov/Archives/edgar/data/879635/000142249326000012/0001422493-26-000012.txt) | 4 | MID PENN BANCORP INC | P · 287.0 · 34.84 · 2026-06-30 | P · 287 · 34.84 · 2026-06-30 | ✓ | ✓ | ✓ | ✓ | match |
| 3 | [0001193125-26-402849](https://www.sec.gov/Archives/edgar/data/1325702/000119312526402849/0001193125-26-402849.txt) | 4 | MAGNACHIP SEMICONDUCTOR Corp | P · 20000.0 · 3.22 · 2026-09-24 | P · 20000 · 3.2199 · 2026-09-24 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 4 | [0001325533-26-000006](https://www.sec.gov/Archives/edgar/data/1821175/000132553326000006/0001325533-26-000006.txt) | 4 | Motorsport Games Inc. | P · 1497.0 · 3.91 · 2026-08-28 | P · 1497 · 3.913 · 2026-08-28 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 5 | [0001477932-26-004305](https://www.sec.gov/Archives/edgar/data/1434740/000147793226004305/0001477932-26-004305.txt) | 4 | Ranger Gold Corp. | P · 27836.0 · 0.01 · 2025-07-10 | P · 27836 · 0.006 · 2025-07-10 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 6 | [0001221359-26-000053](https://www.sec.gov/Archives/edgar/data/1500217/000122135926000053/0001221359-26-000053.txt) | 4 | American Assets Trust, Inc. | P · 50000.0 · 22.56 · 2026-08-27 | P · 50000 · 22.56 · 2026-08-27 | ✓ | ✓ | ✓ | ✓ | match |
| 7 | [0001451455-26-000011](https://www.sec.gov/Archives/edgar/data/766421/000145145526000011/0001451455-26-000011.txt) | 4 | ALASKA AIR GROUP, INC. | P · 25000.0 · 40.06 · 2026-08-20 | P · 25000 · 40.0604 · 2026-08-20 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 8 | [0001213900-26-092276](https://www.sec.gov/Archives/edgar/data/1979414/000121390026092276/0001213900-26-092276.txt) | 4/A | NEONC TECHNOLOGIES HOLDINGS, INC. | P · 10000.0 · 4.8 · 2026-04-24 | P · 10000 · 4.80 · 2026-04-24 | ✓ | ✓ | ✓ | ✓ | match |
| 9 | [0002029760-26-000006](https://www.sec.gov/Archives/edgar/data/1659494/000202976026000006/0002029760-26-000006.txt) | 4 | 51Talk Online Education Group | P · 158460.0 · 19.2 · 2026-08-05 | P · 158460 · 19.2 · 2026-08-05 | ✓ | ✓ | ✓ | ✓ | match |
| 10 | [0001193125-26-392656](https://www.sec.gov/Archives/edgar/data/790816/000119312526392656/0001193125-26-392656.txt) | 4 | BRANDYWINE REALTY TRUST | P · 33900.0 · 2.96 · 2026-09-14 | P · 33900 · 2.96 · 2026-09-14 | ✓ | ✓ | ✓ | ✓ | match |
| 11 | [0001213900-26-100498](https://www.sec.gov/Archives/edgar/data/1439124/000121390026100498/0001213900-26-100498.txt) | 4 | AXIA Energia S.A. | P · 15800.0 · 10.5 · 2026-09-14 | P · 15800 · 10.50 · 2026-09-14 | ✓ | ✓ | ✓ | ✓ | match |
| 12 | [0001213900-26-099887](https://www.sec.gov/Archives/edgar/data/1795251/000121390026099887/0001213900-26-099887.txt) | 4 | Nano-X Imaging Ltd. | P · 30000.0 · 0.76 · 2026-09-14 | P · 30000 · 0.76 · 2026-09-14 | ✓ | ✓ | ✓ | ✓ | match |
| 13 | [0001628280-26-050262](https://www.sec.gov/Archives/edgar/data/2035713/000162828026050262/0001628280-26-050262.txt) | 4 | Crestline Lending Solutions, LLC | P · 10190.82 · 19.63 · 2026-07-24 | P · 10190.823 · 19.63 · 2026-07-24 | ✓ | ✗ | ✓ | ✓ | rounding only |
| 14 | [0001104659-26-081762](https://www.sec.gov/Archives/edgar/data/1612940/000110465926081762/0001104659-26-081762.txt) | 4 | ProQR Therapeutics N.V. | P · 150000.0 · 1.59 · 2026-07-07 | P · 150000 · 1.59 · 2026-07-07 | ✓ | ✓ | ✓ | ✓ | match |
| 15 | [0001475597-26-000246](https://www.sec.gov/Archives/edgar/data/1327068/000147559726000246/0001475597-26-000246.txt) | 4 | United States Oil Fund, LP | P · 26472.0 · 160.0 · 2026-09-14 | P · 26472 · 160 · 2026-09-14 | ✓ | ✓ | ✓ | ✓ | match |
| 16 | [0001628280-26-059399](https://www.sec.gov/Archives/edgar/data/1909747/000162828026059399/0001628280-26-059399.txt) | 4 | Jushi Holdings Inc. | P · 500000.0 · 0.49 · 2026-08-27 | P · 500000 · 0.49 · 2026-08-27 | ✓ | ✓ | ✓ | ✓ | match |
| 17 | [0001626337-26-000011](https://www.sec.gov/Archives/edgar/data/711404/000162633726000011/0001626337-26-000011.txt) | 4 | COOPER COMPANIES, INC. | P · 4701.02 · 53.18 · 2026-09-11 | P · 4701.015 · 53.18 · 2026-09-11 | ✓ | ✗ | ✓ | ✓ | rounding only |
| 18 | [0001475597-26-000246](https://www.sec.gov/Archives/edgar/data/1327068/000147559726000246/0001475597-26-000246.txt) | 4 | United States Oil Fund, LP | P · 2553.0 · 158.08 · 2026-09-14 | P · 2553 · 158.08 · 2026-09-14 | ✓ | ✓ | ✓ | ✓ | match |
| 19 | [0001554855-26-001756](https://www.sec.gov/Archives/edgar/data/1029199/000155485526001756/0001554855-26-001756.txt) | 4 | EURONET WORLDWIDE, INC. | P · 781.0 · 70.6 · 2026-08-07 | P · 781 · 70.6 · 2026-08-07 | ✓ | ✓ | ✓ | ✓ | match |
| 20 | [0001654954-26-008365](https://www.sec.gov/Archives/edgar/data/1375205/000165495426008365/0001654954-26-008365.txt) | 4 | UR-ENERGY INC | P · 75581.0 · 1.29 · 2026-09-11 | P · 75581 · 1.29 · 2026-09-11 | ✓ | ✓ | ✓ | ✓ | match |
| 21 | [0002017181-26-000005](https://www.sec.gov/Archives/edgar/data/701719/000201718126000005/0002017181-26-000005.txt) | 4 | Envela Corp | P · 105.0 · 13.76 · 2026-08-31 | P · 105 · 13.76 · 2026-08-31 | ✓ | ✓ | ✓ | ✓ | match |
| 22 | [0001184754-26-000010](https://www.sec.gov/Archives/edgar/data/2090312/000118475426000010/0001184754-26-000010.txt) | 4 | Mobility Global Inc. | P · 15000.0 · 19.87 · 2026-08-13 | P · 15000 · 19.8714 · 2026-08-13 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 23 | [0001477932-26-004305](https://www.sec.gov/Archives/edgar/data/1434740/000147793226004305/0001477932-26-004305.txt) | 4 | Ranger Gold Corp. | P · 31400.0 · 0.01 · 2025-10-21 | P · 31400 · 0.006 · 2025-10-21 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 24 | [0000905148-26-004111](https://www.sec.gov/Archives/edgar/data/1031203/000090514826004111/0000905148-26-004111.txt) | 4 | GROUP 1 AUTOMOTIVE INC | P · 19286.0 · 302.46 · 2026-09-04 | P · 19286 · 302.4635 · 2026-09-04 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 25 | [0000905148-26-003881](https://www.sec.gov/Archives/edgar/data/1839341/000090514826003881/0000905148-26-003881.txt) | 4 | Core Scientific, Inc./tx | P · 6000.0 · 18.33 · 2026-08-20 | P · 6000 · 18.3324 · 2026-08-20 | ✓ | ✓ | ✗ | ✓ | rounding only |
