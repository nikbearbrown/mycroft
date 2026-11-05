# Conformance audit (G2) — 2023q2, 2023q3, 2023q4, 2024q1, 2024q2, 2024q3, 2024q4, 2025q1, 2025q2, 2025q3, 2025q4, 2026q1, 2026q2, 2026q3

Run at 2026-11-05T00:27:28.843Z by `conformance.py`. This audit reports what was found. The halting checks decide promotion; clearing G2 is the owner's logged decision.

**Promoted:** 78,495 rows → `data/verified/insider_buys.csv` (SHA-256 `a7ec55298bf886c0090f7c5fc4e93bfb18faeabc5d4c407db8d77abefdb75b16`).

## Halting checks

| Quarter | Check | Result | Violations | Detail |
|---|---|---|---:|---|
| 2023q2 | hash | PASS | 0 | manifest SHA-256 7e636787231ae0f00accf5c3627298402dedd1aefffd7c50fb48292e5d3a8fbb |
| 2023q2 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2023q2 | keys | PASS | 0 | 68,588 NONDERIV_TRANS keys, 7,964 buys |
| 2023q2 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2023q2 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2023q2 | buy_filter_purity | PASS | 0 | independent filter on raw: 7,964 buys; buys file: 7,964 |
| 2023q2 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2023q3 | hash | PASS | 0 | manifest SHA-256 26947559fbd710ca4fb007e2ff0481b13ebc3ca47153e77a9b0bc84db250a48e |
| 2023q3 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2023q3 | keys | PASS | 0 | 53,078 NONDERIV_TRANS keys, 5,785 buys |
| 2023q3 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2023q3 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2023q3 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,785 buys; buys file: 5,785 |
| 2023q3 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2023q4 | hash | PASS | 0 | manifest SHA-256 be19822ad9116ea6c1a55303b1f2e23864f21101e42d2da0455a6ff2b33e1a9e |
| 2023q4 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2023q4 | keys | PASS | 0 | 57,852 NONDERIV_TRANS keys, 6,240 buys |
| 2023q4 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2023q4 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2023q4 | buy_filter_purity | PASS | 0 | independent filter on raw: 6,240 buys; buys file: 6,240 |
| 2023q4 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2024q1 | hash | PASS | 0 | manifest SHA-256 8e9bb34335416829a88e4ca7d09bb8aaceca689da9718fef22c298d6f18c9b04 |
| 2024q1 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2024q1 | keys | PASS | 0 | 111,404 NONDERIV_TRANS keys, 5,214 buys |
| 2024q1 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2024q1 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2024q1 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,214 buys; buys file: 5,214 |
| 2024q1 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2024q2 | hash | PASS | 0 | manifest SHA-256 782abee663e466b243f953625ae319da93c3e896816007d5a375e558c94dc7c1 |
| 2024q2 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2024q2 | keys | PASS | 0 | 69,412 NONDERIV_TRANS keys, 5,444 buys |
| 2024q2 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2024q2 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2024q2 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,444 buys; buys file: 5,444 |
| 2024q2 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2024q3 | hash | PASS | 0 | manifest SHA-256 8b55b4ffd91e56770fc0e71f9b73e6886f3c60fac8b7266e4b3e5586d2857910 |
| 2024q3 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2024q3 | keys | PASS | 0 | 55,881 NONDERIV_TRANS keys, 5,070 buys |
| 2024q3 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2024q3 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2024q3 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,070 buys; buys file: 5,070 |
| 2024q3 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2024q4 | hash | PASS | 0 | manifest SHA-256 44763a00aa8a2077747bc015f12c6a4c09ba7cae4a2d031bf24398f9db9e52f3 |
| 2024q4 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2024q4 | keys | PASS | 0 | 63,647 NONDERIV_TRANS keys, 5,983 buys |
| 2024q4 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2024q4 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2024q4 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,983 buys; buys file: 5,983 |
| 2024q4 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2025q1 | hash | PASS | 0 | manifest SHA-256 37f6b4287df129b88acf0782498540640d055b1c893320877e329945b534a8c2 |
| 2025q1 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2025q1 | keys | PASS | 0 | 103,029 NONDERIV_TRANS keys, 5,285 buys |
| 2025q1 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2025q1 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2025q1 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,285 buys; buys file: 5,285 |
| 2025q1 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2025q2 | hash | PASS | 0 | manifest SHA-256 64e7f81328933b1281bd8737961048d76d2ab3d5d1d2d7149a32ec061b0e3ff2 |
| 2025q2 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2025q2 | keys | PASS | 0 | 66,915 NONDERIV_TRANS keys, 6,297 buys |
| 2025q2 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2025q2 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2025q2 | buy_filter_purity | PASS | 0 | independent filter on raw: 6,297 buys; buys file: 6,297 |
| 2025q2 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2025q3 | hash | PASS | 0 | manifest SHA-256 9c57f272b7230500771f661bc1fe181527ed6b76a6f45d23a910c7fc7e9fcfa4 |
| 2025q3 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2025q3 | keys | PASS | 0 | 55,125 NONDERIV_TRANS keys, 4,788 buys |
| 2025q3 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2025q3 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2025q3 | buy_filter_purity | PASS | 0 | independent filter on raw: 4,788 buys; buys file: 4,788 |
| 2025q3 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2025q4 | hash | PASS | 0 | manifest SHA-256 6af26a68f5834eab96dff2c568530d9213638d3e6c9d1256e4f6c9f8af1d2d28 |
| 2025q4 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2025q4 | keys | PASS | 0 | 59,678 NONDERIV_TRANS keys, 5,313 buys |
| 2025q4 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2025q4 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2025q4 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,313 buys; buys file: 5,313 |
| 2025q4 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2026q1 | hash | PASS | 0 | manifest SHA-256 3dcb680593f5829bc951cb0969e858b60fc21a6835b094838218093a849592d6 |
| 2026q1 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2026q1 | keys | PASS | 0 | 103,733 NONDERIV_TRANS keys, 4,817 buys |
| 2026q1 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2026q1 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2026q1 | buy_filter_purity | PASS | 0 | independent filter on raw: 4,817 buys; buys file: 4,817 |
| 2026q1 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2026q2 | hash | PASS | 0 | manifest SHA-256 11f1b2bbbdcbe6347a34437c02d04202fda0eca1dbb023726e4b56504b802e27 |
| 2026q2 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2026q2 | keys | PASS | 0 | 78,328 NONDERIV_TRANS keys, 5,180 buys |
| 2026q2 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2026q2 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2026q2 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,180 buys; buys file: 5,180 |
| 2026q2 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |
| 2026q3 | hash | PASS | 0 | manifest SHA-256 a4e6a681cfcfa43a3d9e4ca9cfec1fd26a59d0a01eac7e9f7b5a0122092c90f3 |
| 2026q3 | required_columns | PASS | 0 | DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header |
| 2026q3 | keys | PASS | 0 | 59,885 NONDERIV_TRANS keys, 5,115 buys |
| 2026q3 | dates | PASS | 0 | promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE |
| 2026q3 | codes | PASS | 0 | promoted rows: SEC code list, A/D |
| 2026q3 | buy_filter_purity | PASS | 0 | independent filter on raw: 5,115 buys; buys file: 5,115 |
| 2026q3 | identity | PASS | 0 | ISSUERCIK and RPTOWNERCIK, numeric |

## Per-quarter funnel

| Quarter | Form 4 rows | Code P | Qualifying (PARSE) | Promoted | Rule 2 collapsed | Rule 1 | Rule 3 | Rule 4 | **Eligible** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023q2 | 68,493 | 8,238 | 7,964 | 7,964 | 64 | 178 | 457 | 602 | **6,663** |
| 2023q3 | 52,896 | 6,857 | 5,785 | 5,785 | 49 | 228 | 236 | 496 | **4,776** |
| 2023q4 | 57,574 | 7,265 | 6,240 | 6,240 | 55 | 165 | 203 | 681 | **5,136** |
| 2024q1 | 109,741 | 5,696 | 5,214 | 5,214 | 58 | 223 | 416 | 295 | **4,222** |
| 2024q2 | 69,302 | 5,560 | 5,444 | 5,444 | 59 | 181 | 109 | 443 | **4,652** |
| 2024q3 | 55,677 | 5,129 | 5,070 | 5,070 | 46 | 204 | 168 | 529 | **4,123** |
| 2024q4 | 63,585 | 6,111 | 5,983 | 5,983 | 78 | 230 | 568 | 308 | **4,799** |
| 2025q1 | 101,541 | 5,389 | 5,285 | 5,285 | 61 | 201 | 291 | 275 | **4,457** |
| 2025q2 | 66,719 | 6,399 | 6,297 | 6,297 | 53 | 174 | 275 | 440 | **5,355** |
| 2025q3 | 54,955 | 4,850 | 4,788 | 4,788 | 30 | 210 | 254 | 247 | **4,047** |
| 2025q4 | 59,517 | 5,426 | 5,313 | 5,313 | 24 | 182 | 268 | 306 | **4,533** |
| 2026q1 | 101,527 | 4,926 | 4,817 | 4,817 | 42 | 179 | 302 | 196 | **4,098** |
| 2026q2 | 78,181 | 5,311 | 5,180 | 5,180 | 33 | 344 | 289 | 321 | **4,193** |
| 2026q3 | 59,834 | 5,183 | 5,115 | 5,115 | 47 | 333 | 192 | 491 | **4,052** |
| **All** | **999,542** | **82,340** | **78,495** | **78,495** | **699** | **3,032** | **4,028** | **5,630** | **65,106** |

Eligible = cluster-detection inputs under `PRE_REGISTRATION.md` Rules 1–5 (counts only; no prices or outcomes). Rule 2 is applied first; each other exclusion is counted under the first rule that applies (1, then 3, then 4). Eligible buys: 65,106 at 4,146 issuers, from 38,320 filings (Rule 5: one filing = one insider). Cannot be STRONG (Rules 1 and 6): 4,404 (10b5-1 plan 4,404, unknown 0). Joint filings: 11,940.

## Amendments — all quarters

1,743 buys on 1,033 Form 4/A filings. Original = a Form 4 in any quarter of this run with the same issuer, the same set of reporting owners, filed on the 4/A's `DATE_OF_ORIG_SUB`.

| Original found | 4/A filings |
|---|---:|
| multiple | 7 |
| none_in_study | 168 |
| resolved_rule_2a | 9 |
| unique | 849 |

- Links to an original in an earlier quarter: 135.
- **Repeat buys (Rule 2: counted once, as the original): 699**, of which 128 repeat an original in an earlier quarter.
- `none_in_study`: the original was filed before the study period, or does not match on issuer, owners and date.

**4/A filings with several candidate originals that Rule 2a could not resolve: 7.** Each stays its own event (`amendment_match = multiple`). Rule 2a links a 4/A with several candidates only when exactly one candidate holds an identical buy (`resolved_rule_2a`).

| 4/A accession | Quarter | Issuer | DATE_OF_ORIG_SUB | Buys | Candidate originals |
|---|---|---|---|---:|---|
| 0001104659-24-084337 | 2024q3 | BRAINSTORM CELL THERAPEUTICS INC. | 2024-05-07 | 1 | 0001104659-24-057784, 0001104659-24-058218 |
| 0001104659-24-084339 | 2024q3 | BRAINSTORM CELL THERAPEUTICS INC. | 2024-05-07 | 1 | 0001104659-24-057784, 0001104659-24-058218 |
| 0001415889-25-007591 | 2025q1 | Solaris Energy Infrastructure, Inc. | 2025-03-07 | 1 | 0001415889-25-007343, 0001415889-25-007362 |
| 0001437749-23-016605 | 2023q2 | FIRST NATIONAL CORP /VA/ | 2023-05-24 | 1 | 0001437749-23-015653, 0001437749-23-015717 |
| 0001437749-24-037695 | 2024q4 | CONSUMERS BANCORP INC /OH/ | 2024-12-16 | 1 | 0001437749-24-037531, 0001437749-24-037615 |
| 0001464631-24-000006 | 2024q2 | Embassy Bancorp, Inc. | 2024-05-24 | 1 | 0001464631-24-000002, 0001464631-24-000003 |
| 0001486189-24-000048 | 2024q4 | Cardio Diagnostics Holdings, Inc. | 2024-09-09 | 1 | 0001486189-24-000044, 0001486189-24-000045 |


## Findings — 2023q2

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 68,493 |
| … code P | 8,238 |
| … qualifying buys (PARSE) | 7,964 |
| … promoted to verified | 7,964 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 19,860 |
| `code_C_conversion` | 902 |
| `code_D_disposition_to_issuer` | 1,083 |
| `code_F_tax_or_exercise_payment` | 9,093 |
| `code_G_gift` | 1,269 |
| `code_I_discretionary_16b3f` | 59 |
| `code_J_other` | 2,109 |
| `code_L_small_acquisition` | 81 |
| `code_M_option_exercise_16b3` | 9,851 |
| `code_S_sale` | 15,766 |
| `code_U_tender_change_of_control` | 53 |
| `code_W_will_or_descent` | 21 |
| `code_X_option_exercise_itm` | 104 |
| `code_Z_voting_trust` | 4 |
| `p_not_acquired` | 21 |
| `p_shares_missing_or_not_positive` | 7 |
| `p_price_missing_or_not_positive` | 245 |
| `trans_date_after_filing` | 1 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 178 |
| … private flag | 76 |
| … ESPP/DRIP flag | 102 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 262 |
| 10b5-1 plan buys that are also excluded by a flag | 4 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **7,786** |

### Amendments (4/A)

203 promoted buys come from 114 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `N/A` | 23 | 8 |
| `NONE` | 112 | 33 |
| `NA` | 2 | 1 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 7,939, `E` 25.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 1,042, of which 1,042 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 5 | 999 | 2,116 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 1,294 | 4,000 | 1,899 | 290 | 320 | 161 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

960 buys from 452 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 7,004, 2: 375, 3: 213, 4: 81, 5: 72, 6: 123, 7: 28, 8: 33, 9: 7, 10: 28.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 754 buys are priced below $1.00 and 79 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 11
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2023q3

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 52,896 |
| … code P | 6,857 |
| … qualifying buys (PARSE) | 5,785 |
| … promoted to verified | 5,785 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 9,397 |
| `code_C_conversion` | 882 |
| `code_D_disposition_to_issuer` | 1,427 |
| `code_E_expiration_short_derivative` | 1 |
| `code_F_tax_or_exercise_payment` | 6,861 |
| `code_G_gift` | 1,127 |
| `code_I_discretionary_16b3f` | 39 |
| `code_J_other` | 2,033 |
| `code_L_small_acquisition` | 110 |
| `code_M_option_exercise_16b3` | 7,416 |
| `code_O_option_exercise_otm` | 6 |
| `code_S_sale` | 16,577 |
| `code_U_tender_change_of_control` | 16 |
| `code_W_will_or_descent` | 14 |
| `code_X_option_exercise_itm` | 121 |
| `code_Z_voting_trust` | 12 |
| `p_not_acquired` | 10 |
| `p_shares_missing_or_not_positive` | 27 |
| `p_price_missing_or_not_positive` | 1,034 |
| `trans_date_after_filing` | 1 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 228 |
| … private flag | 122 |
| … ESPP/DRIP flag | 106 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 484 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **5,557** |

### Amendments (4/A)

107 promoted buys come from 62 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 188 | 38 |
| `N/A` | 16 | 8 |
| `NA` | 5 | 3 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,781, `E` 4.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 783, of which 783 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 3 | 5 | 388 | 3,212 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 823 | 3,074 | 1,378 | 249 | 192 | 69 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

1,216 buys from 516 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,569, 2: 729, 3: 148, 4: 76, 5: 45, 6: 99, 7: 27, 8: 52, 9: 4, 10: 36.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 588 buys are priced below $1.00 and 30 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 1
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2023q4

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 57,574 |
| … code P | 7,265 |
| … qualifying buys (PARSE) | 6,240 |
| … promoted to verified | 6,240 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 9,555 |
| `code_C_conversion` | 776 |
| `code_D_disposition_to_issuer` | 1,537 |
| `code_F_tax_or_exercise_payment` | 8,137 |
| `code_G_gift` | 2,329 |
| `code_I_discretionary_16b3f` | 37 |
| `code_J_other` | 1,662 |
| `code_L_small_acquisition` | 341 |
| `code_M_option_exercise_16b3` | 7,720 |
| `code_S_sale` | 17,912 |
| `code_U_tender_change_of_control` | 101 |
| `code_W_will_or_descent` | 20 |
| `code_X_option_exercise_itm` | 182 |
| `p_not_acquired` | 22 |
| `p_shares_missing_or_not_positive` | 25 |
| `p_price_missing_or_not_positive` | 978 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 168 |
| … private flag | 72 |
| … ESPP/DRIP flag | 96 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 245 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **6,072** |

### Amendments (4/A)

102 promoted buys come from 65 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `N/A` | 22 | 10 |
| `NONE` | 168 | 33 |
| `NA` | 2 | 2 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 6,224, `E` 16.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 684, of which 684 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 3 | 4 | 842 | 4,789 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 1,023 | 3,126 | 1,658 | 202 | 133 | 98 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

1,520 buys from 734 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,720, 2: 813, 3: 224, 4: 102, 5: 37, 6: 254, 7: 20, 8: 41, 10: 29.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 742 buys are priced below $1.00 and 49 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 5
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2024q1

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 109,741 |
| … code P | 5,696 |
| … qualifying buys (PARSE) | 5,214 |
| … promoted to verified | 5,214 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 25,488 |
| `code_C_conversion` | 934 |
| `code_D_disposition_to_issuer` | 1,855 |
| `code_E_expiration_short_derivative` | 1 |
| `code_F_tax_or_exercise_payment` | 27,496 |
| `code_G_gift` | 1,584 |
| `code_I_discretionary_16b3f` | 51 |
| `code_J_other` | 1,743 |
| `code_L_small_acquisition` | 27 |
| `code_M_option_exercise_16b3` | 17,629 |
| `code_S_sale` | 27,080 |
| `code_U_tender_change_of_control` | 52 |
| `code_W_will_or_descent` | 22 |
| `code_X_option_exercise_itm` | 76 |
| `code_Z_voting_trust` | 7 |
| `p_not_acquired` | 40 |
| `p_shares_missing_or_not_positive` | 7 |
| `p_price_missing_or_not_positive` | 432 |
| `trans_date_after_filing` | 3 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 227 |
| … private flag | 95 |
| … ESPP/DRIP flag | 132 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 501 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **4,987** |

### Amendments (4/A)

153 promoted buys come from 81 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 190 | 40 |
| `N/A` | 43 | 13 |
| `NA` | 2 | 1 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,209, `E` 5.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 881, of which 881 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 19 | 606 | 2,332 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 727 | 2,517 | 1,269 | 231 | 352 | 118 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

1,397 buys from 535 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 3,817, 2: 881, 3: 176, 4: 112, 5: 42, 6: 55, 7: 54, 8: 43, 9: 3, 10: 31.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 574 buys are priced below $1.00 and 174 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 14
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2024q2

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 69,302 |
| … code P | 5,560 |
| … qualifying buys (PARSE) | 5,444 |
| … promoted to verified | 5,444 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 19,052 |
| `code_C_conversion` | 680 |
| `code_D_disposition_to_issuer` | 1,364 |
| `code_F_tax_or_exercise_payment` | 9,205 |
| `code_G_gift` | 1,281 |
| `code_I_discretionary_16b3f` | 76 |
| `code_J_other` | 1,699 |
| `code_L_small_acquisition` | 77 |
| `code_M_option_exercise_16b3` | 10,071 |
| `code_O_option_exercise_otm` | 4 |
| `code_S_sale` | 20,096 |
| `code_U_tender_change_of_control` | 51 |
| `code_W_will_or_descent` | 21 |
| `code_X_option_exercise_itm` | 65 |
| `p_not_acquired` | 17 |
| `p_shares_missing_or_not_positive` | 25 |
| `p_price_missing_or_not_positive` | 72 |
| `trans_date_after_filing` | 2 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 195 |
| … private flag | 74 |
| … ESPP/DRIP flag | 121 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 254 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **5,249** |

### Amendments (4/A)

141 promoted buys come from 89 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 169 | 41 |
| `N/A` | 23 | 7 |
| `NA` | 4 | 2 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,411, `E` 33.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 586, of which 586 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 1 | 3 | 4 | 647 | 730,485 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 968 | 2,792 | 1,301 | 208 | 100 | 75 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

770 buys from 384 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,674, 2: 376, 3: 221, 4: 61, 5: 37, 6: 19, 7: 11, 8: 37, 9: 7, 10: 1.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 472 buys are priced below $1.00 and 40 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 17
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2024q3

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 55,677 |
| … code P | 5,129 |
| … qualifying buys (PARSE) | 5,070 |
| … promoted to verified | 5,070 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 9,243 |
| `code_C_conversion` | 966 |
| `code_D_disposition_to_issuer` | 1,267 |
| `code_F_tax_or_exercise_payment` | 7,014 |
| `code_G_gift` | 1,209 |
| `code_I_discretionary_16b3f` | 62 |
| `code_J_other` | 1,466 |
| `code_L_small_acquisition` | 294 |
| `code_M_option_exercise_16b3` | 7,741 |
| `code_O_option_exercise_otm` | 1 |
| `code_S_sale` | 21,053 |
| `code_U_tender_change_of_control` | 52 |
| `code_W_will_or_descent` | 6 |
| `code_X_option_exercise_itm` | 166 |
| `code_Z_voting_trust` | 8 |
| `p_not_acquired` | 6 |
| `p_shares_missing_or_not_positive` | 13 |
| `p_price_missing_or_not_positive` | 40 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 211 |
| … private flag | 112 |
| … ESPP/DRIP flag | 99 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 339 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **4,859** |

### Amendments (4/A)

119 promoted buys come from 75 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `N/A` | 27 | 11 |
| `NONE` | 144 | 35 |
| `NA` | 1 | 1 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,062, `E` 8.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 588, of which 588 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 3 | 5 | 283 | 1,777 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 760 | 2,547 | 1,342 | 217 | 170 | 34 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

999 buys from 413 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,071, 2: 494, 3: 152, 4: 45, 5: 41, 6: 207, 7: 38, 8: 1, 9: 17, 10: 4.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 592 buys are priced below $1.00 and 44 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 5
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2024q4

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 63,585 |
| … code P | 6,111 |
| … qualifying buys (PARSE) | 5,983 |
| … promoted to verified | 5,983 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 9,546 |
| `code_C_conversion` | 998 |
| `code_D_disposition_to_issuer` | 1,221 |
| `code_E_expiration_short_derivative` | 1 |
| `code_F_tax_or_exercise_payment` | 8,459 |
| `code_G_gift` | 2,239 |
| `code_I_discretionary_16b3f` | 66 |
| `code_J_other` | 1,831 |
| `code_L_small_acquisition` | 156 |
| `code_M_option_exercise_16b3` | 8,444 |
| `code_S_sale` | 24,412 |
| `code_U_tender_change_of_control` | 31 |
| `code_W_will_or_descent` | 6 |
| `code_X_option_exercise_itm` | 60 |
| `code_Z_voting_trust` | 4 |
| `p_not_acquired` | 21 |
| `p_shares_missing_or_not_positive` | 51 |
| `p_price_missing_or_not_positive` | 55 |
| `trans_date_after_filing` | 1 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 230 |
| … private flag | 139 |
| … ESPP/DRIP flag | 91 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 525 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **5,753** |

### Amendments (4/A)

135 promoted buys come from 63 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 182 | 42 |
| `N/A` | 29 | 10 |
| `NA` | 10 | 2 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,748, `E` 235.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 1,300, of which 1,300 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 31 | 4119 | 4,721 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 722 | 2,819 | 1,408 | 429 | 164 | 441 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

1,584 buys from 483 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,399, 2: 632, 3: 543, 4: 241, 5: 68, 6: 47, 7: 28, 8: 21, 9: 3, 10: 1.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 351 buys are priced below $1.00 and 28 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 3
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2025q1

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 101,541 |
| … code P | 5,389 |
| … qualifying buys (PARSE) | 5,285 |
| … promoted to verified | 5,285 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_missing` | 1 |
| `code_A_grant_award` | 24,985 |
| `code_C_conversion` | 794 |
| `code_D_disposition_to_issuer` | 1,862 |
| `code_F_tax_or_exercise_payment` | 27,339 |
| `code_G_gift` | 1,398 |
| `code_I_discretionary_16b3f` | 83 |
| `code_J_other` | 1,853 |
| `code_L_small_acquisition` | 47 |
| `code_M_option_exercise_16b3` | 15,985 |
| `code_O_option_exercise_otm` | 5 |
| `code_S_sale` | 21,625 |
| `code_U_tender_change_of_control` | 53 |
| `code_W_will_or_descent` | 16 |
| `code_X_option_exercise_itm` | 106 |
| `p_not_acquired` | 17 |
| `p_shares_missing_or_not_positive` | 30 |
| `p_price_missing_or_not_positive` | 57 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 204 |
| … private flag | 115 |
| … ESPP/DRIP flag | 89 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 450 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **5,081** |

### Amendments (4/A)

147 promoted buys come from 87 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 170 | 43 |
| `N/A` | 40 | 19 |
| `NA` | 2 | 1 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,256, `E` 29.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 754, of which 754 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 3 | 5 | 678 | 4,994 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 816 | 2,597 | 1,344 | 186 | 232 | 110 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

1,018 buys from 362 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,267, 2: 454, 3: 259, 4: 125, 5: 65, 6: 62, 7: 19, 8: 14, 9: 10, 10: 10.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 351 buys are priced below $1.00 and 16 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 10
- Unparseable dates: 0
- Code blank or not in SEC's list: 1
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2025q2

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 66,719 |
| … code P | 6,399 |
| … qualifying buys (PARSE) | 6,297 |
| … promoted to verified | 6,297 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 18,965 |
| `code_C_conversion` | 696 |
| `code_D_disposition_to_issuer` | 1,608 |
| `code_F_tax_or_exercise_payment` | 9,039 |
| `code_G_gift` | 1,238 |
| `code_I_discretionary_16b3f` | 35 |
| `code_J_other` | 1,796 |
| `code_L_small_acquisition` | 58 |
| `code_M_option_exercise_16b3` | 9,507 |
| `code_O_option_exercise_otm` | 1 |
| `code_S_sale` | 17,165 |
| `code_U_tender_change_of_control` | 109 |
| `code_W_will_or_descent` | 16 |
| `code_X_option_exercise_itm` | 87 |
| `p_not_acquired` | 29 |
| `p_shares_missing_or_not_positive` | 18 |
| `p_price_missing_or_not_positive` | 49 |
| `p_equity_swap` | 3 |
| `trans_date_after_filing` | 3 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 174 |
| … private flag | 100 |
| … ESPP/DRIP flag | 74 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 739 |
| 10b5-1 plan buys that are also excluded by a flag | 4 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **6,123** |

### Amendments (4/A)

127 promoted buys come from 73 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 143 | 39 |
| `N/A` | 46 | 13 |
| `NA` | 1 | 1 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 6,011, `E` 286.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 975, of which 975 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 9 | 236 | 2,025 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 870 | 3,145 | 1,519 | 445 | 281 | 37 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

1,152 buys from 467 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 5,145, 2: 659, 3: 172, 4: 152, 5: 65, 6: 42, 7: 34, 8: 24, 9: 2, 10: 2.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 554 buys are priced below $1.00 and 80 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 8
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2025q3

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 54,955 |
| … code P | 4,850 |
| … qualifying buys (PARSE) | 4,788 |
| … promoted to verified | 4,788 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 8,976 |
| `code_C_conversion` | 771 |
| `code_D_disposition_to_issuer` | 1,496 |
| `code_F_tax_or_exercise_payment` | 6,708 |
| `code_G_gift` | 1,219 |
| `code_I_discretionary_16b3f` | 26 |
| `code_J_other` | 1,540 |
| `code_L_small_acquisition` | 58 |
| `code_M_option_exercise_16b3` | 6,919 |
| `code_O_option_exercise_otm` | 1 |
| `code_S_sale` | 22,167 |
| `code_U_tender_change_of_control` | 128 |
| `code_W_will_or_descent` | 37 |
| `code_X_option_exercise_itm` | 51 |
| `code_Z_voting_trust` | 8 |
| `p_not_acquired` | 17 |
| `p_shares_missing_or_not_positive` | 3 |
| `p_price_missing_or_not_positive` | 42 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 211 |
| … private flag | 137 |
| … ESPP/DRIP flag | 74 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 321 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **4,577** |

### Amendments (4/A)

86 promoted buys come from 56 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 216 | 48 |
| `N/A` | 57 | 15 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 4,526, `E` 262.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 736, of which 736 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 14 | 291 | 7,306 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 735 | 2,345 | 1,108 | 329 | 236 | 35 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

550 buys from 252 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,238, 2: 188, 3: 64, 4: 87, 5: 36, 6: 85, 7: 9, 8: 65, 9: 1, 10: 15.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 272 buys are priced below $1.00 and 42 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 2
- Unparseable dates: 0
- Code blank or not in SEC's list: 0
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2025q4

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 59,517 |
| … code P | 5,426 |
| … qualifying buys (PARSE) | 5,313 |
| … promoted to verified | 5,313 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_missing` | 1 |
| `code_A_grant_award` | 8,938 |
| `code_C_conversion` | 756 |
| `code_D_disposition_to_issuer` | 1,374 |
| `code_E_expiration_short_derivative` | 2 |
| `code_F_tax_or_exercise_payment` | 8,096 |
| `code_G_gift` | 2,341 |
| `code_I_discretionary_16b3f` | 22 |
| `code_J_other` | 1,471 |
| `code_L_small_acquisition` | 292 |
| `code_M_option_exercise_16b3` | 8,141 |
| `code_S_sale` | 22,483 |
| `code_U_tender_change_of_control` | 66 |
| `code_W_will_or_descent` | 15 |
| `code_X_option_exercise_itm` | 93 |
| `p_not_acquired` | 29 |
| `p_shares_missing_or_not_positive` | 6 |
| `p_price_missing_or_not_positive` | 78 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 183 |
| … private flag | 103 |
| … ESPP/DRIP flag | 80 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 138 |
| 10b5-1 plan buys that are also excluded by a flag | 1 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **5,130** |

### Amendments (4/A)

91 promoted buys come from 43 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 186 | 49 |
| `N/A` | 51 | 16 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,231, `E` 82.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 810, of which 810 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 6 | 614 | 7,309 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 741 | 2,554 | 1,473 | 256 | 214 | 75 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

588 buys from 230 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,725, 2: 226, 3: 85, 4: 106, 5: 22, 6: 50, 7: 33, 8: 38, 9: 19, 10: 9.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 378 buys are priced below $1.00 and 32 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 1
- Unparseable dates: 0
- Code blank or not in SEC's list: 1
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2026q1

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 101,527 |
| … code P | 4,926 |
| … qualifying buys (PARSE) | 4,817 |
| … promoted to verified | 4,817 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_missing` | 3 |
| `code_A_grant_award` | 24,489 |
| `code_C_conversion` | 774 |
| `code_D_disposition_to_issuer` | 2,239 |
| `code_F_tax_or_exercise_payment` | 26,995 |
| `code_G_gift` | 1,361 |
| `code_I_discretionary_16b3f` | 30 |
| `code_J_other` | 1,498 |
| `code_L_small_acquisition` | 123 |
| `code_M_option_exercise_16b3` | 16,295 |
| `code_O_option_exercise_otm` | 1 |
| `code_S_sale` | 22,615 |
| `code_U_tender_change_of_control` | 66 |
| `code_W_will_or_descent` | 18 |
| `code_X_option_exercise_itm` | 93 |
| `code_Z_voting_trust` | 1 |
| `p_not_acquired` | 14 |
| `p_shares_missing_or_not_positive` | 16 |
| `p_price_missing_or_not_positive` | 79 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 180 |
| … private flag | 68 |
| … ESPP/DRIP flag | 112 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 188 |
| 10b5-1 plan buys that are also excluded by a flag | 0 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **4,637** |

### Amendments (4/A)

97 promoted buys come from 66 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `N/A` | 75 | 21 |
| `NONE` | 168 | 49 |
| `NA` | 2 | 2 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 4,802, `E` 15.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 829, of which 829 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 11 | 1007 | 8,767 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 688 | 2,241 | 1,299 | 229 | 201 | 159 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

549 buys from 235 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,268, 2: 201, 3: 67, 4: 94, 5: 46, 6: 49, 7: 37, 8: 24, 9: 19, 10: 12.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 254 buys are priced below $1.00 and 6 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 8
- Unparseable dates: 0
- Code blank or not in SEC's list: 3
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


## Findings — 2026q2

### Rows in / out

| Step | Rows |
|---|---:|
| Form 4 / 4-A rows (PARSE) | 78,181 |
| … code P | 5,311 |
| … qualifying buys (PARSE) | 5,180 |
| … promoted to verified | 5,180 |

Exclusions by reason (reason names carry the transaction code):

| Reason | Rows |
|---|---:|
| `code_missing` | 2 |
| `code_A_grant_award` | 19,209 |
| `code_C_conversion` | 880 |
| `code_D_disposition_to_issuer` | 1,710 |
| `code_F_tax_or_exercise_payment` | 9,357 |
| `code_G_gift` | 1,282 |
| `code_I_discretionary_16b3f` | 32 |
| `code_J_other` | 1,746 |
| `code_L_small_acquisition` | 54 |
| `code_M_option_exercise_16b3` | 10,778 |
| `code_O_option_exercise_otm` | 3 |
| `code_S_sale` | 27,598 |
| `code_U_tender_change_of_control` | 96 |
| `code_W_will_or_descent` | 14 |
| `code_X_option_exercise_itm` | 109 |
| `p_not_acquired` | 35 |
| `p_shares_missing_or_not_positive` | 14 |
| `p_price_missing_or_not_positive` | 82 |

### PRE_REGISTRATION.md Rule 1 (counts only)

| | Buys |
|---|---:|
| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | 345 |
| … private flag | 176 |
| … ESPP/DRIP flag | 169 |
| … both | 0 |
| 10b5-1 plan buys that may cluster but **cannot be STRONG** | 246 |
| 10b5-1 plan buys that are also excluded by a flag | 1 |
| `is_10b5_1 = unknown` (rule not yet registered) | 0 |
| **Eligible for cluster detection** | **4,835** |

### Amendments (4/A)

91 promoted buys come from 67 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

### Blank or placeholder trading symbols

| Symbol as filed | Buys | Issuers |
|---|---:|---:|
| `NONE` | 134 | 42 |
| `N/A` | 64 | 21 |

ENRICH cannot price these by symbol; they will need a `price_status` reason.

### Late filings and the TRANS_DATE → FILING_DATE lag

`TRANS_TIMELINESS` as filed: `<blank: on time>` 5,065, `E` 115.
Filed more than 2 business days after the trade (weekdays only, no holiday calendar, so this slightly overcounts): 862, of which 862 are not marked `L`.

| Calendar days | min | p25 | median | p75 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| lag | 0 | 1 | 2 | 4 | 7 | 254 | 7,294 |

| Lag bucket (days) | 0 | 1-2 | 3-5 | 6-30 | 31-365 | >365 |
|---|---:|---:|---:|---:|---:|---:|
| Buys | 774 | 2,294 | 1,472 | 321 | 279 | 40 |

Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing enters the backtest only when it became public.

### Joint filings

566 buys from 224 filings list more than one reporting owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. Owners per buy: 1: 4,614, 2: 194, 3: 82, 4: 94, 5: 86, 6: 43, 7: 41, 8: 9, 9: 8, 10: 9.

### Precision of shares and prices

The most decimals on any promoted price is 2, and on any share count 2. The spot-check shows the data set rounds the filed values to 2 decimals (half-up). That matters most for low prices: 387 buys are priced below $1.00 and 68 at $0.05 or less, where rounding can move price and `value_usd` by a large fraction. The data set is not corrected here.

### Form 4 rows that were not promoted (reported, not halted on)

- `TRANS_DATE` after `FILING_DATE`: 0
- Unparseable dates: 0
- Code blank or not in SEC's list: 2
- `TRANS_ACQUIRED_DISP_CD` not A or D: 0


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

144 promoted buys come from 92 Form 4/A filings. Matching to originals is across all quarters: see "Amendments — all quarters" below.

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

25 buys drawn at random (seed `16486067862572434945`, derived from the source ZIP hashes). Each filing's Form 4 XML was compared with the data set. **15 of 25 match exactly** on code, shares, price and date; **10** differ only because the data set rounds shares or price to 2 decimals; **0** differ in another way. Requests to SEC this run: 25 (1/s, logged in `data/raw/filings/request_log.jsonl`). Mismatches are listed, not corrected.

| # | Accession | Form | Issuer | Data set (code · shares · price · date) | Filing XML | Code | Shares | Price | Date | Result |
|---:|---|---|---|---|---|:-:|:-:|:-:|:-:|---|
| 1 | [0001761119-23-000003](https://www.sec.gov/Archives/edgar/data/786035/000176111923000003/0001761119-23-000003.txt) | 4 | LIBERTY ALL STAR GROWTH FUND INC. | P · 1000.0 · 5.27 · 2023-08-29 | P · 1000 · 5.27 · 2023-08-29 | ✓ | ✓ | ✓ | ✓ | match |
| 2 | [0000824142-25-000084](https://www.sec.gov/Archives/edgar/data/824142/000082414225000084/0000824142-25-000084.txt) | 4 | AAON, INC. | P · 1000.0 · 80.86 · 2025-03-05 | P · 1000 · 80.86 · 2025-03-05 | ✓ | ✓ | ✓ | ✓ | match |
| 3 | [0001104659-23-128118](https://www.sec.gov/Archives/edgar/data/770460/000110465923128118/0001104659-23-128118.txt) | 4 | PEOPLES FINANCIAL CORP /MS/ | P · 384.0 · 14.35 · 2023-12-20 | P · 384 · 14.3500 · 2023-12-20 | ✓ | ✓ | ✓ | ✓ | match |
| 4 | [0000950170-24-049153](https://www.sec.gov/Archives/edgar/data/1929561/000095017024049153/0000950170-24-049153.txt) | 4 | RXO, Inc. | P · 100000.0 · 19.79 · 2024-04-25 | P · 100000 · 19.79 · 2024-04-25 | ✓ | ✓ | ✓ | ✓ | match |
| 5 | [0001654954-24-002049](https://www.sec.gov/Archives/edgar/data/718413/000165495424002049/0001654954-24-002049.txt) | 4 | COMMUNITY BANCORP /VT | P · 280.0 · 17.35 · 2024-02-21 | P · 280.00 · 17.35 · 2024-02-21 | ✓ | ✓ | ✓ | ✓ | match |
| 6 | [0001225208-23-009811](https://www.sec.gov/Archives/edgar/data/33185/000122520823009811/0001225208-23-009811.txt) | 4 | EQUIFAX INC | P · 820.0 · 166.19 · 2023-10-26 | P · 820.0000 · 166.1941 · 2023-10-26 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 7 | [0001174947-23-000740](https://www.sec.gov/Archives/edgar/data/716605/000117494723000740/0001174947-23-000740.txt) | 4 | PENNS WOODS BANCORP INC | P · 597.0 · 22.21 · 2023-05-08 | P · 597 · 22.21 · 2023-05-08 | ✓ | ✓ | ✓ | ✓ | match |
| 8 | [0001166586-26-000002](https://www.sec.gov/Archives/edgar/data/1639723/000116658626000002/0001166586-26-000002.txt) | 4 | Navan, Inc. | P · 466058.0 · 16.27 · 2026-01-02 | P · 466058 · 16.27 · 2026-01-02 | ✓ | ✓ | ✓ | ✓ | match |
| 9 | [0001195734-24-000024](https://www.sec.gov/Archives/edgar/data/1195734/000119573424000024/0001195734-24-000024.txt) | 4 | POTBELLY CORP | P · 1000.0 · 11.65 · 2024-03-12 | P · 1000 · 11.65 · 2024-03-12 | ✓ | ✓ | ✓ | ✓ | match |
| 10 | [0001374339-26-000003](https://www.sec.gov/Archives/edgar/data/1374339/000137433926000003/0001374339-26-000003.txt) | 4 | ProMIS Neurosciences Inc. | P · 1000.0 · 21.89 · 2026-03-03 | P · 1000 · 21.89 · 2026-03-03 | ✓ | ✓ | ✓ | ✓ | match |
| 11 | [0001104659-24-111249](https://www.sec.gov/Archives/edgar/data/1538379/000110465924111249/0001104659-24-111249.txt) | 4 | Ibotta, Inc. | P · 309.0 · 71.17 · 2024-10-22 | P · 309 · 71.1723 · 2024-10-22 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 12 | [0001062993-25-015077](https://www.sec.gov/Archives/edgar/data/707605/000106299325015077/0001062993-25-015077.txt) | 4 | AMERISERV FINANCIAL INC /PA/ | P · 3000.0 · 3.04 · 2025-08-28 | P · 3000 · 3.04 · 2025-08-28 | ✓ | ✓ | ✓ | ✓ | match |
| 13 | [0001127602-23-026668](https://www.sec.gov/Archives/edgar/data/1409970/000112760223026668/0001127602-23-026668.txt) | 4 | LendingClub Corp | P · 10000.0 · 5.2 · 2023-10-31 | P · 10000 · 5.2003 · 2023-10-31 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 14 | [0000950170-25-034655](https://www.sec.gov/Archives/edgar/data/1500881/000095017025034655/0000950170-25-034655.txt) | 4 | enCore Energy Corp. | P · 35000.0 · 1.65 · 2025-03-04 | P · 35000 · 1.6484 · 2025-03-04 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 15 | [0001641172-25-003675](https://www.sec.gov/Archives/edgar/data/1574094/000164117225003675/0001641172-25-003675.txt) | 4 | RenovoRx, Inc. | P · 6500.0 · 0.79 · 2025-04-10 | P · 6500 · 0.79 · 2025-04-10 | ✓ | ✓ | ✓ | ✓ | match |
| 16 | [0001641172-25-005318](https://www.sec.gov/Archives/edgar/data/1200375/000164117225005318/0001641172-25-005318.txt) | 4 | CODEXIS, INC. | P · 25000.0 · 2.23 · 2025-04-15 | P · 25000 · 2.2288 · 2025-04-15 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 17 | [0001628280-26-006249](https://www.sec.gov/Archives/edgar/data/2065601/000162828026006249/0001628280-26-006249.txt) | 4 | Central Bancompany, Inc. | P · 40000.0 · 24.5 · 2026-02-06 | P · 40000 · 24.497 · 2026-02-06 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 18 | [0001062993-23-013757](https://www.sec.gov/Archives/edgar/data/1047862/000106299323013757/0001062993-23-013757.txt) | 4 | CONSOLIDATED EDISON INC | P · 0.98 · 92.95 · 2023-06-15 | P · 0.9760 · 92.95 · 2023-06-15 | ✓ | ✗ | ✓ | ✓ | rounding only |
| 19 | [0001207097-23-000293](https://www.sec.gov/Archives/edgar/data/919567/000120709723000293/0001207097-23-000293.txt) | 4 | RENN Fund, Inc. | P · 8.0 · 1.83 · 2023-10-04 | P · 8 · 1.83 · 2023-10-04 | ✓ | ✓ | ✓ | ✓ | match |
| 20 | [0001209191-23-047806](https://www.sec.gov/Archives/edgar/data/1604665/000120919123047806/0001209191-23-047806.txt) | 4 | Westlake Chemical Partners LP | P · 10000.0 · 22.74 · 2023-08-29 | P · 10000 · 22.738 · 2023-08-29 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 21 | [0001193125-26-394331](https://www.sec.gov/Archives/edgar/data/849146/000119312526394331/0001193125-26-394331.txt) | 4 | Lifevantage Corp | P · 976.0 · 6.22 · 2026-09-15 | P · 976 · 6.22 · 2026-09-15 | ✓ | ✓ | ✓ | ✓ | match |
| 22 | [0001209191-23-048246](https://www.sec.gov/Archives/edgar/data/1627282/000120919123048246/0001209191-23-048246.txt) | 4 | CaliberCos Inc. | P · 25000.0 · 1.5 · 2023-08-31 | P · 25000 · 1.4996 · 2023-08-31 | ✓ | ✓ | ✗ | ✓ | rounding only |
| 23 | [0001176334-24-000168](https://www.sec.gov/Archives/edgar/data/1176334/000117633424000168/0001176334-24-000168.txt) | 4 | MARTIN MIDSTREAM PARTNERS L.P. | P · 17.12 · 3.99 · 2024-11-18 | P · 17.1186 · 3.9874 · 2024-11-18 | ✓ | ✗ | ✗ | ✓ | rounding only |
| 24 | [0001214659-23-015748](https://www.sec.gov/Archives/edgar/data/1437491/000121465923015748/0001214659-23-015748.txt) | 4 | RiskOn International, Inc. | P · 1500.0 · 0.35 · 2023-11-27 | P · 1500 · 0.35 · 2023-11-27 | ✓ | ✓ | ✓ | ✓ | match |
| 25 | [0000945621-24-000768](https://www.sec.gov/Archives/edgar/data/1959353/000094562124000768/0000945621-24-000768.txt) | 4 | Oxford Park Income Fund, Inc. | P · 84360.3 · 28.45 · 2024-05-01 | P · 84360.3 · 28.45 · 2024-05-01 | ✓ | ✓ | ✓ | ✓ | match |
