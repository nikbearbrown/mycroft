# PARSE audit — 2025q3

Source: SEC Insider Transactions Data Set 2025q3 (ZIP SHA-256 `9c57f272b7230500771f661bc1fe181527ed6b76a6f45d23a910c7fc7e9fcfa4`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 55,125 | |
| Form 4 / 4-A rows | 54,955 | 100.0% |
| … with code P | 4,850 | 8.8% |
| … qualifying buys | 4,788 | 8.7% |

Rows by document type (all forms): 4: 54,344, 4/A: 611, 5: 170.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **50,167** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 321 | 6.7% |
| No plan (AFF10B5ONE = 0/false) | 4,467 | 93.3% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 137 | 2.9% |
| ESPP or dividend reinvestment (footnote heuristic) | 74 | 1.5% |
| Joint filing (more than one reporting owner) | 550 | 11.5% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,626, `false` 841, `1` 317, `true` 4.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 273, no_plan 96. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 23, dividend reinvestment 51, IPO 13, PIPE 3, directed share program 29, from the issuer 8, private placement 34, privately negotiated 1, public offering 83, registered direct 2, rights offering 4, securities purchase agreement 15, subscription agreement 8, underwritten 60.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 252
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,069, `false` 781
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001737912-25-000006 | Transocean Ltd. | public offering | on reported herein was made in connection with a registered public offering of securities at the reported public offering price offered by the Issuer, as described in the Issuer's |
| 0001729635-25-000005 | Transocean Ltd. | public offering | on reported herein was made in connection with a registered public offering of securities at the reported public offering price offered by the Issuer, as described in the Issuer's |
| 0001729638-25-000008 | Transocean Ltd. | public offering | on reported herein was made in connection with a registered public offering of securities at the reported public offering price offered by the Issuer, as described in the Issuer's |
| 0001213900-25-093530 | Emmis Acquisition Corp. | private placement | ion Corp. (the ""Issuer"") that are included in the 310,000 private placement units of the Issuer purchased by Emmis Capital Sponsor LLC (""Sponsor""). Each private placement unit |
| 0001493152-25-016130 | Nordicus Partners Corp | subscription agreement | These shares were acquired pursuant to a subscription agreement. The reporting person undertakes to provide, upon request by the Securities and Exchange Commission staff, the issue |
| 0001493152-25-016130 | Nordicus Partners Corp | subscription agreement | These shares were acquired pursuant to a subscription agreement. The reporting person undertakes to provide, upon request by the Securities and Exchange Commission staff, the issue |
| 0001493152-25-016130 | Nordicus Partners Corp | subscription agreement | These shares were acquired pursuant to a subscription agreement. The reporting person undertakes to provide, upon request by the Securities and Exchange Commission staff, the issue |
| 0001493152-25-016130 | Nordicus Partners Corp | subscription agreement | These shares were acquired pursuant to a subscription agreement. The reporting person undertakes to provide, upon request by the Securities and Exchange Commission staff, the issue |
| 0001193125-25-223503 | 5C Lending Partners Corp. | subscription agreement | issuer in the form of a capital call. Under the terms of a subscription agreement between the reporting persons and the issuer, the reporting persons are required to fund drawdown |
| 0001213900-25-091105 | Jasper Therapeutics, Inc. | public offering, underwritten | urchase one share of voting common stock in an underwritten public offering at a combined offering price of $2.43 per share of voting common stock and accompanying warrant. |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001628280-25-042985 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001628280-25-042985 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001746448-25-000003 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
| 0001872989-25-000003 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
| 0001791771-25-000003 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
