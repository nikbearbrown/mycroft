# PARSE audit — 2024q2

Source: SEC Insider Transactions Data Set 2024q2 (ZIP SHA-256 `782abee663e466b243f953625ae319da93c3e896816007d5a375e558c94dc7c1`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 69,412 | |
| Form 4 / 4-A rows | 69,302 | 100.0% |
| … with code P | 5,560 | 8.0% |
| … qualifying buys | 5,444 | 7.9% |

Rows by document type (all forms): 4: 68,395, 4/A: 907, 5: 110.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **63,858** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 254 | 4.7% |
| No plan (AFF10B5ONE = 0/false) | 5,190 | 95.3% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 74 | 1.4% |
| ESPP or dividend reinvestment (footnote heuristic) | 121 | 2.2% |
| Joint filing (more than one reporting owner) | 770 | 14.1% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 4,146, `false` 1,044, `1` 217, `true` 37.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: no_plan 22, plan 131. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 25, dividend reinvestment 96, IPO 15, directed share program 7, from the issuer 13, private placement 20, public offering 27, registered direct 6, securities purchase agreement 14, subscription agreement 12, underwritten 13.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 269
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 4,618, `false` 942
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001104659-24-075270 | ClearSign Technologies Corp | securities purchase agreement | rein were issued to clirSPV LLC (""clirSPV"") pursuant to a Securities Purchase Agreement, dated as of June 24, 2024, as amended on June 26, 2024 (as amended, the ""Purchase Agreem |
| 0001079973-24-000893 | ProtoKinetix, Inc. | private placement | Shares purchased in private placement of the Company. |
| 0001079973-24-000893 | ProtoKinetix, Inc. | private placement | Shares purchased in private placement of the Company. |
| 0000950170-24-070675 | MSD Investment Corp. | subscription agreement | issuer in the form of a capital call. Under the terms of a subscription agreement between the reporting persons and the issuer, the reporting persons are required to fund drawdown |
| 0000950170-24-070639 | MSD Investment Corp. | subscription agreement | he issuer in the form of a capital call. Under the terms of subscription agreements between the reporting persons and the issuer, the reporting persons are required to fund drawdow |
| 0000950170-24-070639 | MSD Investment Corp. | subscription agreement | he issuer in the form of a capital call. Under the terms of subscription agreements between the reporting persons and the issuer, the reporting persons are required to fund drawdow |
| 0001193805-24-000755 | electroCore, Inc. | private placement | On June 5, 2024, pursuant to a private placement offering by the Issuer, the Reporting Person acquired 38,505 Units, each Unit consisting of (i) one share of the Issuer's Common St |
| 0001062993-24-011568 | Larimar Therapeutics, Inc. | underwritten | "Represents shares of common stock purchased in the underwritten offering of Larimar Therapeutics, Inc. (the ""Company"") at the offering price, which closed on February 16, 2024." |
| 0000950170-24-066676 | FTAI Aviation Ltd. | public offering, underwritten | shares purchased by the reporting person in an underwritten public offering by the issuer that closed on May 30, 2024. |
| 0001628280-24-025650 | Bowhead Specialty Holdings Inc. | public offering, IPO, directed share program | purchased as issuer-directed shares in the Issuer's initial public offering. |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001628280-24-030527 | Noble Corp plc | dividend reinvestment | ares acquired through inadvertent automatic enrollment in a dividend reinvestment program within the personal brokerage account of the Reporting Person. On the date of the transac |
| 0001156375-24-000136 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0001156375-24-000136 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. |
| 0001628280-24-029084 | Granite Ridge Resources, Inc. | dividend reinvestment | Shares acquired through automatic dividend reinvestment pursuant to the terms of a brokerage account. |
| 0001127602-24-018896 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for eac |
