# PARSE audit — 2025q4

Source: SEC Insider Transactions Data Set 2025q4 (ZIP SHA-256 `6af26a68f5834eab96dff2c568530d9213638d3e6c9d1256e4f6c9f8af1d2d28`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 59,678 | |
| Form 4 / 4-A rows | 59,517 | 100.0% |
| … with code P | 5,426 | 9.1% |
| … qualifying buys | 5,313 | 8.9% |

Rows by document type (all forms): 4: 58,999, 4/A: 518, 5: 151, 5/A: 10.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **54,204** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 139 | 2.6% |
| No plan (AFF10B5ONE = 0/false) | 5,174 | 97.4% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 103 | 1.9% |
| ESPP or dividend reinvestment (footnote heuristic) | 80 | 1.5% |
| Joint filing (more than one reporting owner) | 588 | 11.1% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 4,285, `false` 889, `1` 110, `true` 29.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 74, no_plan 6. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 39, dividend reinvestment 41, IPO 29, PIPE 1, directed share program 24, from the issuer 4, private placement 18, privately negotiated 4, public offering 40, registered direct 4, rights offering 6, securities purchase agreement 18, subscription agreement 4, underwritten 19.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 173
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,538, `false` 888
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001878313-25-000073 | MAIA Biotechnology, Inc. | securities purchase agreement | The common stock was purchased pursuant to a Securities Purchase Agreement and were issued under the Issuer's 2021 Equity Incentive Plan on December 22, 2025. |
| 0001878313-25-000071 | MAIA Biotechnology, Inc. | securities purchase agreement | The common stock was purchased pursuant to a Securities Purchase Agreement and were issued under the Issuer's 2021 Equity Incentive Plan on December 22, 2025. |
| 0001878313-25-000069 | MAIA Biotechnology, Inc. | securities purchase agreement | The common stock was purchased pursuant to a Securities Purchase Agreement and were issued under the Issuer's 2021 Equity Incentive Plan on December 22, 2025 |
| 0001193125-25-328997 | Medline Inc. | IPO | purchased 12,586,206 shares of Class A Common Stock in the IPO." |
| 0001193125-25-328814 | Medline Inc. | public offering, IPO | Class A Common Stock of the Issuer acquired in the initial public offering of Class A Common Stock of the Issuer at the initial public offering price and on the same terms as the |
| 0001193125-25-328813 | Medline Inc. | public offering, IPO | Class A Common Stock of the Issuer acquired in the initial public offering of Class A Common Stock of the Issuer at the initial public offering price and on the same terms as the |
| 0001193125-25-328813 | Medline Inc. | public offering, IPO | Class A Common Stock of the Issuer acquired in the initial public offering of Class A Common Stock of the Issuer at the initial public offering price and on the same terms as the |
| 0001193125-25-328764 | Andersen Group Inc. | public offering, IPO, directed share program | ected share program in connection with the Issuer's initial public offering of Class A common stock. |
| 0001193125-25-328754 | Andersen Group Inc. | public offering, IPO, directed share program | ected share program in connection with the Issuer's initial public offering of Class A common stock. |
| 0001193125-25-328741 | Andersen Group Inc. | public offering, IPO, directed share program | ected share program in connection with the Issuer's initial public offering of Class A common stock. |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001072627-25-000049 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for eac |
| 0001072627-25-000048 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for eac |
| 0001628280-25-057530 | Granite Ridge Resources, Inc. | dividend reinvestment | Shares acquired through automatic dividend reinvestment pursuant to the terms of a brokerage account. |
| 0001791771-25-000006 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
| 0001872989-25-000005 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
