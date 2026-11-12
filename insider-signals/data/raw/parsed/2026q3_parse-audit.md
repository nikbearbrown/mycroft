# PARSE audit — 2026q3

Source: SEC Insider Transactions Data Set 2026q3 (ZIP SHA-256 `a4e6a681cfcfa43a3d9e4ca9cfec1fd26a59d0a01eac7e9f7b5a0122092c90f3`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 59,885 | |
| Form 4 / 4-A rows | 59,834 | 100.0% |
| … with code P | 5,183 | 8.7% |
| … qualifying buys | 5,115 | 8.5% |

Rows by document type (all forms): 4: 58,855, 4/A: 979, 5: 51.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **54,719** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 136 | 2.7% |
| No plan (AFF10B5ONE = 0/false) | 4,979 | 97.3% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 135 | 2.6% |
| ESPP or dividend reinvestment (footnote heuristic) | 201 | 3.9% |
| Joint filing (more than one reporting owner) | 686 | 13.4% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,878, `false` 1,101, `1` 80, `true` 56.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 106. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 130, dividend reinvestment 71, IPO 42, PIPE 7, directed share program 11, from the issuer 4, private placement 50, privately negotiated 2, public offering 61, securities purchase agreement 27, subscription agreement 12, underwritten 20.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 225
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,017, `false` 1,165, `1` 1
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0000947871-26-000912 | ADARx Pharmaceuticals, Inc. | public offering, IPO | the Issuer's Common Stock purchased in the Issuer's initial public offering. |
| 0000947871-26-000911 | ADARx Pharmaceuticals, Inc. | public offering, IPO | the Issuer's Common Stock purchased in the Issuer's initial public offering. |
| 0000947871-26-000911 | ADARx Pharmaceuticals, Inc. | public offering, IPO | the Issuer's Common Stock purchased in the Issuer's initial public offering. |
| 0000947871-26-000911 | ADARx Pharmaceuticals, Inc. | public offering, IPO | the Issuer's Common Stock purchased in the Issuer's initial public offering. |
| 0000947871-26-000910 | ADARx Pharmaceuticals, Inc. | public offering, IPO | the Issuer's Common Stock purchased in the Issuer's initial public offering. |
| 0000947871-26-000910 | ADARx Pharmaceuticals, Inc. | public offering, IPO | the Issuer's Common Stock purchased in the Issuer's initial public offering. |
| 0000947871-26-000910 | ADARx Pharmaceuticals, Inc. | public offering, IPO | the Issuer's Common Stock purchased in the Issuer's initial public offering. |
| 0001493152-26-044992 | LIBERTY STAR URANIUM & METALS CORP. | private placement | ber 28, 2026 the reporting person acquired share units in a private placement purchase including 1 share and 1/2 warrant (right to buy) per share. Price is set by an average VWAP 4 |
| 0001193125-26-407271 | Heritage Global Inc. | privately negotiated | reported shares were purchased by Inductive Capital LP in a privately negotiated transaction from Ross Dove, Chief Executive Officer and a director of the Issuer, at a price of $1. |
| 0001437749-26-031181 | Harvard Apparatus Regenerative Technology, Inc. | private placement, securities purchase agreement | rchased 361,905 shares of common stock of the Issuer in the Private Placement for an aggregate cash purchase price of $380,000, or $1.05 per share, pursuant to a Securities Purchas |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001072627-26-000056 | KINGSWAY Corp | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for each regular |
| 0001072627-26-000055 | KINGSWAY Corp | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for each regular |
| 0001628280-26-063755 | Finward Bancorp | dividend reinvestment | Shares acquired from the Dividend Reinvestment Plan |
| 0001628280-26-063748 | Finward Bancorp | dividend reinvestment | Shares acquired from the Dividend Reinvestment Plan |
| 0001628280-26-063746 | Finward Bancorp | dividend reinvestment | Shares acquired from the Dividend Reinvestment Plan |
