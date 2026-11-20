# PARSE audit — 2024q4

Source: SEC Insider Transactions Data Set 2024q4 (ZIP SHA-256 `44763a00aa8a2077747bc015f12c6a4c09ba7cae4a2d031bf24398f9db9e52f3`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 63,647 | |
| Form 4 / 4-A rows | 63,585 | 100.0% |
| … with code P | 6,111 | 9.6% |
| … qualifying buys | 5,983 | 9.4% |

Rows by document type (all forms): 4: 62,964, 4/A: 621, 5: 62.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

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
| **Total excluded** | **57,602** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 525 | 8.8% |
| No plan (AFF10B5ONE = 0/false) | 5,458 | 91.2% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 139 | 2.3% |
| ESPP or dividend reinvestment (footnote heuristic) | 91 | 1.5% |
| Joint filing (more than one reporting owner) | 1,584 | 26.5% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,924, `false` 1,534, `1` 519, `true` 6.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 454, no_plan 5. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 31, dividend reinvestment 66, IPO 25, PIPE 1, directed share program 8, from the issuer 15, private placement 23, privately negotiated 2, public offering 48, registered direct 10, rights offering 17, securities purchase agreement 23, subscription agreement 12, underwritten 22.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 273
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 5,239, `false` 872
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001104659-24-132975 | Rain Enhancement Technologies Holdco, Inc. | private placement, subscription agreement | er share, at a price of approximately $11.39 per share in a private placement pursuant to a Subscription Agreement dated as of December 23, 2024, by and among the Reporting Person |
| 0001104659-24-132190 | Quoin Pharmaceuticals, Ltd. | public offering | and a Series G Warrant to purchase one ADS in the Issuer's public offering which closed on December 23, 2024, at a combined public offering price of $0.45. The Series F Warrants a |
| 0001104659-24-132188 | Quoin Pharmaceuticals, Ltd. | public offering | and a Series G Warrant to purchase one ADS in the Issuer's public offering which closed on December 23, 2024, at a combined public offering price of $0.45. The Series F Warrants a |
| 0001104659-24-132187 | Quoin Pharmaceuticals, Ltd. | public offering | and a Series G Warrant to purchase one ADS in the Issuer's public offering which closed on December 23, 2024, at a combined public offering price of $0.45. The Series F Warrants a |
| 0001104659-24-132185 | Quoin Pharmaceuticals, Ltd. | public offering | and a Series G Warrant to purchase one ADS in the Issuer's public offering which closed on December 23, 2024, at a combined public offering price of $0.45. The Series F Warrants a |
| 0001493152-24-052101 | Anebulo Pharmaceuticals, Inc. | private placement | he shares were issued to 22NW Fund, LP in connection with a private placement offering of the Issuer. |
| 0001104659-24-131704 | Marker Therapeutics, Inc. | securities purchase agreement, from the issuer | Acquired from the Issuer on December 23, 2024 pursuant to a Securities Purchase Agreement dated December 19, 2024. |
| 0000950170-24-140372 | 5C Lending Partners Corp. | subscription agreement | ""LMHC"") may be deemed to beneficially own pursuant to the Subscription Agreements, dated October 23, 2024 (the ""Subscription Agreements""), entered into by each of the Subsidiar |
| 0000950170-24-139757 | RumbleOn, Inc. | private placement, rights offering | f Class B Common Stock of the issuer pursuant to a backstop private placement of the issuer, whereby Partners, as previously agreed to, purchased the shares of Class B Common Stock |
| 0002005814-24-000019 | F&M BANK CORP | from the issuer | Shares acquired from the issuer with proceeds of a quarterly retainer. |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001156375-24-000204 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001156375-24-000204 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0000074260-24-000144 | OLD REPUBLIC INTERNATIONAL CORP | dividend reinvestment | Trade executed pursuant to Dividend Reinvestment Plan. |
| 0001127602-24-029632 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for eac |
| 0001127602-24-029631 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP"").? Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for each regular |
