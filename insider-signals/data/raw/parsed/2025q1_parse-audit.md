# PARSE audit — 2025q1

Source: SEC Insider Transactions Data Set 2025q1 (ZIP SHA-256 `37f6b4287df129b88acf0782498540640d055b1c893320877e329945b534a8c2`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 103,029 | |
| Form 4 / 4-A rows | 101,541 | 100.0% |
| … with code P | 5,389 | 5.3% |
| … qualifying buys | 5,285 | 5.2% |

Rows by document type (all forms): 4: 100,210, 4/A: 1,331, 5: 1,460, 5/A: 28.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **96,256** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 450 | 8.5% |
| No plan (AFF10B5ONE = 0/false) | 4,835 | 91.5% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 115 | 2.2% |
| ESPP or dividend reinvestment (footnote heuristic) | 89 | 1.7% |
| Joint filing (more than one reporting owner) | 1,018 | 19.3% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,794, `false` 1,041, `true` 246, `1` 204.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 390, no_plan 2. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 36, dividend reinvestment 53, IPO 19, PIPE 1, directed share program 18, from the issuer 9, private placement 33, privately negotiated 3, public offering 41, registered direct 10, securities purchase agreement 29, subscription agreement 6, underwritten 20.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 293
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,421, `false` 968
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001434728-25-000102 | Global Water Resources, Inc. | public offering | The purchase of common stock pursuant to public offering on March 27, 2025, offered at the public offering price of $10.00 per share. |
| 0001434728-25-000101 | Global Water Resources, Inc. | public offering | The purchase of common stock pursuant to public offering on March 27, 2025, offered at the public offering price of $10.00 per share. |
| 0000950170-25-047130 | F&G Annuities & Life, Inc. | public offering, underwritten | 500,000 shares in F&G Annuities & Life, Inc.'s underwritten public offering, which closed on March 24, 2025. |
| 0000950170-25-047104 | Surrozen, Inc./DE | private placement | , LP (""TCG Opportunity III LP"") purchased in the Issuer's private placement on March 24, 2025 (the ""2025 Private Placement"")." |
| 0000950170-25-047104 | Surrozen, Inc./DE | private placement | , LP (""TCG Opportunity III LP"") purchased in the Issuer's private placement on March 24, 2025 (the ""2025 Private Placement"")." |
| 0000950170-25-047104 | Surrozen, Inc./DE | private placement | , LP (""TCG Opportunity III LP"") purchased in the Issuer's private placement on March 24, 2025 (the ""2025 Private Placement"")." |
| 0001079973-25-000529 | Oncology Institute, Inc. | private placement, securities purchase agreement | e of the securities to the reporting person pursuant to the Private Placement was approved by the Company's board of directors and was deemed an exempt transaction pursuant to Rule |
| 0001079973-25-000527 | Oncology Institute, Inc. | private placement, securities purchase agreement | "Represents securities purchased in a private placement transaction directly from the Company pursuant to a Securities Purchase Agreement, dated March 24, 2025 (the ""Private Place |
| 0001079973-25-000525 | Oncology Institute, Inc. | private placement, securities purchase agreement | "Represents securities purchased in a private placement transaction directly from the Company pursuant to a Securities Purchase Agreement, dated March 24, 2025 (the ""Private Place |
| 0001079973-25-000523 | Oncology Institute, Inc. | private placement, securities purchase agreement | e of the securities to the reporting person pursuant to the Private Placement was approved by the Company's board of directors and was deemed an exempt transaction pursuant to Rule |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001127602-25-010662 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for eac |
| 0001415889-25-009209 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
| 0001156375-25-000090 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001156375-25-000088 | CME GROUP INC. | dividend reinvestment | number of shares acquired on January 16, 2025 pursuant to a dividend reinvestment plan administered by the reporting person's broker. Subsequent to the purchase and the filing of |
| 0001156375-25-000088 | CME GROUP INC. | dividend reinvestment | number of shares acquired on January 16, 2025 pursuant to a dividend reinvestment plan administered by the reporting person's broker. Subsequent to the purchase and the filing of |
