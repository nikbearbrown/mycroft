# PARSE audit — 2026q1

Source: SEC Insider Transactions Data Set 2026q1 (ZIP SHA-256 `3dcb680593f5829bc951cb0969e858b60fc21a6835b094838218093a849592d6`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 103,733 | |
| Form 4 / 4-A rows | 101,527 | 100.0% |
| … with code P | 4,926 | 4.9% |
| … qualifying buys | 4,817 | 4.7% |

Rows by document type (all forms): 4: 100,341, 4/A: 1,186, 5: 2,168, 5/A: 38.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

| Reason | Rows |
|---|---:|
| `code_missing` | 3 |
| `code_A_grant_award` | 24,489 |
| `code_C_conversion` | 774 |
| `code_D_disposition_to_issuer` | 2,239 |
| `code_F_tax_or_exercise_payment` | 26,995 |
| `code_G_gift` | 1,361 |
| `code_I_discretionary_16b3f` | 30 |
| `code_J_other` | 1,498 |
| `code_L_small_acquisition` | 123 |
| `code_M_option_exercise_16b3` | 16,295 |
| `code_O_option_exercise_otm` | 1 |
| `code_S_sale` | 22,615 |
| `code_U_tender_change_of_control` | 66 |
| `code_W_will_or_descent` | 18 |
| `code_X_option_exercise_itm` | 93 |
| `code_Z_voting_trust` | 1 |
| `p_not_acquired` | 14 |
| `p_shares_missing_or_not_positive` | 16 |
| `p_price_missing_or_not_positive` | 79 |
| **Total excluded** | **96,710** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 188 | 3.9% |
| No plan (AFF10B5ONE = 0/false) | 4,629 | 96.1% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 68 | 1.4% |
| ESPP or dividend reinvestment (footnote heuristic) | 112 | 2.3% |
| Joint filing (more than one reporting owner) | 549 | 11.4% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 3,560, `false` 1,069, `true` 111, `1` 77.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 142, no_plan 3. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 27, dividend reinvestment 86, IPO 10, PIPE 2, directed share program 1, from the issuer 9, private placement 23, privately negotiated 3, public offering 17, registered direct 1, rights offering 1, securities purchase agreement 6, subscription agreement 12, underwritten 19.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 185
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 3,820, `false` 1,106
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001104659-26-037865 | Zenas BioPharma, Inc. | public offering, underwritten | Acquired in an underwritten public offering, pursuant to which Zenas BioPharma, Inc. sold shares of common stock at a purchase price of $20.00 per share. |
| 0001700225-26-000003 | TALPHERA, INC. | securities purchase agreement, PIPE | On March 31, 2025, Talphera (the ""Issuer"") entered into a securities purchase agreement with the Reporting Person and certain other institutional investors (the ""PIPE""). The |
| 0001213900-26-034272 | Horizon Quantum Holdings Ltd. | subscription agreement | any, and Horizon Quantum Computing Pte. Ltd. entered into a subscription agreement with Penchant Family Holdings LLC, whereby the Company, upon the closing of the Company's busines |
| 0001104659-26-033952 | Janus Living, Inc. | underwritten, IPO | Represents shares purchased from the underwriters in the IPO. |
| 0001104659-26-033948 | Janus Living, Inc. | underwritten, IPO | Represents shares purchased from the underwriters in the IPO. |
| 0001104659-26-033941 | Janus Living, Inc. | underwritten, IPO | Represents shares purchased from the underwriters in the IPO. |
| 0001104659-26-033940 | Janus Living, Inc. | underwritten, IPO | Represents shares purchased from the underwriters in the IPO. |
| 0001104659-26-033939 | Janus Living, Inc. | public offering, underwritten, IPO | res purchased from the underwriters in the Issuer's initial public offering of Class A-1 Common Stock (""IPO"")." |
| 0001104659-26-033937 | Janus Living, Inc. | public offering, underwritten, IPO | res purchased from the underwriters in the Issuer's initial public offering of Class A-1 Common Stock (""IPO"")." |
| 0001193125-26-122177 | 5C Lending Partners Corp. | subscription agreement | issuer in the form of a capital call. Under the terms of a subscription agreement between the reporting persons and the issuer, the reporting persons are required to fund drawdown |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001072627-26-000020 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for each regular |
| 0001072627-26-000019 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for each regular |
| 0001628280-26-022028 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001628280-26-022028 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001379195-26-000002 | GERMAN AMERICAN BANCORP, INC. | dividend reinvestment | hares of common stock through participation in the Issuer's Dividend Reinvestment and Stock Purchase Plan (the ""Dividend Reinvestment Plan"")." |
