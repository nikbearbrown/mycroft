# PARSE audit — 2023q4

Source: SEC Insider Transactions Data Set 2023q4 (ZIP SHA-256 `be19822ad9116ea6c1a55303b1f2e23864f21101e42d2da0455a6ff2b33e1a9e`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 57,852 | |
| Form 4 / 4-A rows | 57,574 | 100.0% |
| … with code P | 7,265 | 12.6% |
| … qualifying buys | 6,240 | 10.8% |

Rows by document type (all forms): 4: 56,818, 4/A: 756, 5: 222, 5/A: 56.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **51,334** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 245 | 3.9% |
| No plan (AFF10B5ONE = 0/false) | 5,995 | 96.1% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 72 | 1.2% |
| ESPP or dividend reinvestment (footnote heuristic) | 96 | 1.5% |
| Joint filing (more than one reporting owner) | 1,520 | 24.4% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 5,248, `false` 747, `1` 186, `true` 59.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 178, no_plan 2. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 29, dividend reinvestment 72, IPO 4, PIPE 3, from the issuer 3, private placement 21, privately negotiated 2, public offering 29, registered direct 9, rights offering 3, securities purchase agreement 13, subscription agreement 2, underwritten 24.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 1,074
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 6,701, `false` 563, `1` 1
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001209191-23-059892 | Astra Space, Inc. | privately negotiated | These shares were purchased in a privately negotiated transaction from an individual affiliated with ACME, LLC and not in the public market. The negotiated purchase price reflects |
| 0001079973-23-001824 | ProtoKinetix, Inc. | private placement | Shares purchased in private placement of the Company. |
| 0001178913-23-003988 | Entera Bio Ltd. | securities purchase agreement | "The Reporting Person entered into a Securities Purchase Agreement with the Issuer on December 20, 2023, pursuant to which, on December 22, 2023, the Reporting Person acquired an a |
| 0001178913-23-003971 | Entera Bio Ltd. | securities purchase agreement | "The Reporting Person entered into a Securities Purchase Agreement with the Issuer on December 20, 2023, pursuant to which, on December 22, 2023, the Reporting Person acquired an a |
| 0001104659-23-129312 | Chavant Capital Acquisition Corp. | private placement, subscription agreement, PIPE | ach ordinary share of Chavant (""Ordinary Share"") and each private placement warrant, exercisable to purchase one Ordinary Share for $11.50 per share, subject to certain adjustmen |
| 0001104659-23-129186 | Cyclacel Pharmaceuticals, Inc. | private placement, securities purchase agreement | hased unregistered shares of the Issuer's common stock in a private placement, pursuant to a Securities Purchase Agreement between the Reporting Person and the Issuer. |
| 0001104659-23-129185 | Cyclacel Pharmaceuticals, Inc. | private placement, securities purchase agreement | hased unregistered shares of the Issuer's common stock in a private placement, pursuant to a Securities Purchase Agreement between the Reporting Person and the Issuer. |
| 0001477932-23-009286 | SinglePoint Inc. | public offering, underwritten | urchased from the underwriters in the Issuer's underwritten public offering that closed on December 19, 2023. |
| 0001912571-23-000005 | System1, Inc. | privately negotiated | Lone Star Friends Trust purchased 880,000 shares in a privately negotiated arm's length transaction from another existing holder of the Issuer's Class A common stock in a transacti |
| 0001104659-23-126932 | Liquidia Corp | public offering, underwritten | es of common stock purchased by the Reporting Person at the public offering price in connection with the Issuer's underwritten public offering of common stock, which closed on Dece |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001156375-23-000203 | CME GROUP INC. | dividend reinvestment | 1. Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0001156375-23-000203 | CME GROUP INC. | dividend reinvestment | 1. Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0000074260-23-000108 | OLD REPUBLIC INTERNATIONAL CORP | dividend reinvestment | Trade executed pursuant to Dividend Reinvestment Plan. |
| 0001209191-23-059455 | DoubleVerify Holdings, Inc. | ESPP | Pursuant to the DoubleVerify Holdings, Inc. 2021 Employee Stock Purchase Plan (ESPP), the purchase price per share reported reflects a discount of 15% of the lesser of the share pr |
| 0000715579-23-000105 | ACNB CORP | dividend reinvestment | omatic reinvestment of dividends under the ACNB Corporation Dividend Reinvestment and Stock Purchase Plan, which are exempt from the reporting requirements of Section 16 of the Sec |
