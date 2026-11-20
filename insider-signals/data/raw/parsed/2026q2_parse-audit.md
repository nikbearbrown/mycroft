# PARSE audit — 2026q2

Source: SEC Insider Transactions Data Set 2026q2 (ZIP SHA-256 `11f1b2bbbdcbe6347a34437c02d04202fda0eca1dbb023726e4b56504b802e27`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 78,328 | |
| Form 4 / 4-A rows | 78,181 | 100.0% |
| … with code P | 5,311 | 6.8% |
| … qualifying buys | 5,180 | 6.6% |

Rows by document type (all forms): 4: 77,257, 4/A: 924, 5: 145, 5/A: 2.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **73,001** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 247 | 4.8% |
| No plan (AFF10B5ONE = 0/false) | 4,933 | 95.2% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 176 | 3.4% |
| ESPP or dividend reinvestment (footnote heuristic) | 169 | 3.3% |
| Joint filing (more than one reporting owner) | 566 | 10.9% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,987, `false` 946, `1` 126, `true` 121.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 146, no_plan 36. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 109, dividend reinvestment 60, IPO 92, PIPE 1, directed share program 64, from the issuer 8, private placement 51, privately negotiated 4, public offering 113, registered direct 3, rights offering 5, securities purchase agreement 15, subscription agreement 12, underwritten 25.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 315
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,285, `false` 1,026
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001267959-26-000003 | CalciMedica, Inc. | securities purchase agreement, from the issuer | The securities were acquired from the Issuer pursuant to a Securities Purchase Agreement dated June 23, 2026, with a closing date of June 25, 2026. The Securities Purchase Agreemen |
| 0001104659-26-078260 | DPC Holdings Ltd | private placement, public offering, IPO, from the issuer | dinary shares acquired from the Issuer in connection with a private placement occurring concurrently with the Issuer's initial public offering. |
| 0001104659-26-078260 | DPC Holdings Ltd | public offering, IPO, directed share program | e program conducted in connection with the Issuer's initial public offering and consists of (i) shares purchased under the Director Share Program pursuant to the DPC Holdings Limit |
| 0001104659-26-078258 | DPC Holdings Ltd | public offering, IPO, directed share program | e program conducted in connection with the Issuer's initial public offering and consists of shares acquired to reinvest in the Issuer using after-tax proceeds from the Management I |
| 0001104659-26-078256 | DPC Holdings Ltd | public offering, IPO, directed share program | e program conducted in connection with the Issuer's initial public offering and consists of shares purchased under the Director Share Program pursuant to the DPC Holdings Limited 2 |
| 0001104659-26-078255 | DPC Holdings Ltd | public offering, IPO, directed share program | e program conducted in connection with the Issuer's initial public offering and consists of shares acquired to reinvest in the Issuer using after-tax proceeds from the Management I |
| 0001104659-26-078254 | DPC Holdings Ltd | public offering, IPO, directed share program | e program conducted in connection with the Issuer's initial public offering and consists of shares purchased under the Director Share Program pursuant to the DPC Holdings Limited 2 |
| 0001104659-26-078253 | DPC Holdings Ltd | public offering, IPO, directed share program | e program conducted in connection with the Issuer's initial public offering and consists of shares purchased under the Director Share Program pursuant to the DPC Holdings Limited 2 |
| 0001104659-26-078250 | DPC Holdings Ltd | private placement, public offering, IPO, from the issuer | dinary shares acquired from the Issuer in connection with a private placement occurring concurrently with the Issuer's initial public offering. |
| 0001104659-26-078250 | DPC Holdings Ltd | public offering, IPO, directed share program | e program conducted in connection with the Issuer's initial public offering and consists of (i) shares purchased under the Director Share Program pursuant to the DPC Holdings Limit |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001212852-26-000003 | CME GROUP INC. | dividend reinvestment | epresents shares acquired pursuant to a broker-administered dividend reinvestment plan. |
| 0001212852-26-000003 | CME GROUP INC. | dividend reinvestment | epresents shares acquired pursuant to a broker-administered dividend reinvestment plan. |
| 0000752642-26-000072 | UMH PROPERTIES, INC. | dividend reinvestment | Purchase of shares through the Dividend Reinvestment and Stock Purchase Plan on 6/15/2026. |
| 0001746448-26-000005 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
| 0002081604-26-000006 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
