# PARSE audit — 2024q3

Source: SEC Insider Transactions Data Set 2024q3 (ZIP SHA-256 `8b55b4ffd91e56770fc0e71f9b73e6886f3c60fac8b7266e4b3e5586d2857910`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 55,881 | |
| Form 4 / 4-A rows | 55,677 | 100.0% |
| … with code P | 5,129 | 9.2% |
| … qualifying buys | 5,070 | 9.1% |

Rows by document type (all forms): 4: 54,934, 4/A: 743, 5: 200, 5/A: 4.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **50,607** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 339 | 6.7% |
| No plan (AFF10B5ONE = 0/false) | 4,731 | 93.3% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 112 | 2.2% |
| ESPP or dividend reinvestment (footnote heuristic) | 99 | 2.0% |
| Joint filing (more than one reporting owner) | 999 | 19.7% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,685, `false` 1,046, `1` 303, `true` 36.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 256, no_plan 15. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 43, dividend reinvestment 63, IPO 38, directed share program 26, from the issuer 9, private placement 12, privately negotiated 2, public offering 70, registered direct 5, rights offering 1, securities purchase agreement 8, subscription agreement 1, underwritten 38.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 173
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,275, `false` 854
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001569187-24-000147 | Armada Hoffler Properties, Inc. | public offering, underwritten | es were purchased from the underwriters in the underwritten public offering that closed on September 27, 2024. |
| 0001569187-24-000146 | Armada Hoffler Properties, Inc. | public offering, underwritten | es were purchased from the underwriters in the underwritten public offering that closed on September 27, 2024. |
| 0001569187-24-000145 | Armada Hoffler Properties, Inc. | public offering, underwritten | es were purchased from the underwriters in the underwritten public offering that closed on September 27, 2024. |
| 0001569187-24-000144 | Armada Hoffler Properties, Inc. | public offering, underwritten | es were purchased from the underwriters in the underwritten public offering that closed on September 27, 2024. |
| 0001569187-24-000143 | Armada Hoffler Properties, Inc. | public offering, underwritten | es were purchased from the underwriters in the underwritten public offering that closed on September 27, 2024. |
| 0001569187-24-000142 | Armada Hoffler Properties, Inc. | public offering, underwritten | es were purchased from the underwriters in the underwritten public offering that closed on September 27, 2024. |
| 0001569187-24-000141 | Armada Hoffler Properties, Inc. | public offering, underwritten | es were purchased from the underwriters in the underwritten public offering that closed on September 27, 2024. |
| 0001412665-24-000150 | MidWestOne Financial Group, Inc. | public offering, underwritten | Represents shares purchased by the reporting person at the public offering price of $25.00 per share in connection with the issuer's underwritten public offering of common stock, w |
| 0001412665-24-000149 | MidWestOne Financial Group, Inc. | public offering, underwritten | Represents shares purchased by the reporting person at the public offering price of $25.00 per share in connection with the issuer's underwritten public offering of common stock, w |
| 0001412665-24-000148 | MidWestOne Financial Group, Inc. | public offering, underwritten | Represents shares purchased by the reporting person at the public offering price of $25.00 per share in connection with the issuer's underwritten public offering of common stock, w |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001156375-24-000184 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0001156375-24-000184 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0000074260-24-000131 | OLD REPUBLIC INTERNATIONAL CORP | dividend reinvestment | Trade executed pursuant to Dividend Reinvestment Plan. |
| 0001437749-24-029592 | MIDDLEFIELD BANC CORP | dividend reinvestment | Includes shares acquired under MBCN Dividend Reinvestment Plan |
| 0001562180-24-006855 | UNITED FIRE GROUP INC | dividend reinvestment | Shares were acquired pursuant to a dividend reinvestment program offered through a personal brokerage account. |
