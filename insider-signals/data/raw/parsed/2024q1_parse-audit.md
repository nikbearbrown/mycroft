# PARSE audit — 2024q1

Source: SEC Insider Transactions Data Set 2024q1 (ZIP SHA-256 `8e9bb34335416829a88e4ca7d09bb8aaceca689da9718fef22c298d6f18c9b04`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 111,404 | |
| Form 4 / 4-A rows | 109,741 | 100.0% |
| … with code P | 5,696 | 5.2% |
| … qualifying buys | 5,214 | 4.8% |

Rows by document type (all forms): 4: 108,212, 4/A: 1,529, 5: 1,634, 5/A: 29.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **104,527** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 501 | 9.6% |
| No plan (AFF10B5ONE = 0/false) | 4,713 | 90.4% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 95 | 1.8% |
| ESPP or dividend reinvestment (footnote heuristic) | 132 | 2.5% |
| Joint filing (more than one reporting owner) | 1,397 | 26.8% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,750, `false` 963, `1` 477, `true` 24.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 350, no_plan 1. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 50, dividend reinvestment 95, IPO 20, directed share program 3, from the issuer 17, private placement 8, privately negotiated 1, public offering 47, registered direct 10, rights offering 2, securities purchase agreement 25, subscription agreement 3, underwritten 28.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 399
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,991, `false` 705
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001213900-24-028125 | Agrify Corp | public offering | 8 per share of common stock in connection with the issuer's public offering that closed on February 28, 2024. |
| 0001213900-24-028125 | Agrify Corp | public offering | 8 per share of common stock in connection with the issuer's public offering that closed on February 28, 2024. |
| 0000950170-24-038089 | Nkarta, Inc. | public offering, underwritten | Reports the purchase of shares in the underwritten public offering of common stock of the Issuer. |
| 0000950170-24-038089 | Nkarta, Inc. | public offering, underwritten | Reports the purchase of shares in the underwritten public offering of common stock of the Issuer. |
| 0000950170-24-036131 | COMSTOCK RESOURCES INC | subscription agreement | he closing of the transactions contemplated by that certain Subscription Agreement, dated March 20, 2024, by and among the Company, Arkoma and Williston." |
| 0000950170-24-035469 | Astera Labs, Inc. | public offering, IPO, directed share program | ected share program in connection with the Issuer's initial public offering. |
| 0000950170-24-035423 | Astera Labs, Inc. | public offering, IPO, directed share program | ected share program in connection with the Issuer's initial public offering. |
| 0000950170-24-035422 | Astera Labs, Inc. | public offering, IPO, directed share program | ected share program in connection with the Issuer's initial public offering. |
| 0001912571-24-000002 | System1, Inc. | privately negotiated | Lone Star Friends Trust purchased 880,281 shares in a privately negotiated arm's length transaction from another existing holder of the Issuer's Class A common stock in a transacti |
| 0001731122-24-000450 | Landsea Homes Corp | public offering, underwritten | ock through participation as an investor in an underwritten public offering by Landsea Holdings Corporation, the issuer's largest stockholder, at the offering price of $11.60 per s |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001156375-24-000065 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0001156375-24-000065 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0000715579-24-000044 | ACNB CORP | dividend reinvestment | omatic reinvestment of dividends under the ACNB Corporation Dividend Reinvestment and Stock Purchase Plan, which are exempt from the reporting requirements of Section 16 of the Sec |
| 0000715579-24-000039 | ACNB CORP | dividend reinvestment | omatic reinvestment of dividends under the ACNB Corporation Dividend Reinvestment and Stock Purchase Plan, which are exempt from the reporting requirements of Section 16 of the Sec |
| 0001628280-24-012047 | PHINIA INC. | dividend reinvestment | early reporting of shares acquired pursuant to an automatic dividend reinvestment feature of the reporting person's brokerage account. |
