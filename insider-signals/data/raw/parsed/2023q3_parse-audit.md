# PARSE audit — 2023q3

Source: SEC Insider Transactions Data Set 2023q3 (ZIP SHA-256 `26947559fbd710ca4fb007e2ff0481b13ebc3ca47153e77a9b0bc84db250a48e`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 53,078 | |
| Form 4 / 4-A rows | 52,896 | 100.0% |
| … with code P | 6,857 | 13.0% |
| … qualifying buys | 5,785 | 10.9% |

Rows by document type (all forms): 4: 52,145, 4/A: 751, 5: 180, 5/A: 2.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 9,397 |
| `code_C_conversion` | 882 |
| `code_D_disposition_to_issuer` | 1,427 |
| `code_E_expiration_short_derivative` | 1 |
| `code_F_tax_or_exercise_payment` | 6,861 |
| `code_G_gift` | 1,127 |
| `code_I_discretionary_16b3f` | 39 |
| `code_J_other` | 2,033 |
| `code_L_small_acquisition` | 110 |
| `code_M_option_exercise_16b3` | 7,416 |
| `code_O_option_exercise_otm` | 6 |
| `code_S_sale` | 16,577 |
| `code_U_tender_change_of_control` | 16 |
| `code_W_will_or_descent` | 14 |
| `code_X_option_exercise_itm` | 121 |
| `code_Z_voting_trust` | 12 |
| `p_not_acquired` | 10 |
| `p_shares_missing_or_not_positive` | 27 |
| `p_price_missing_or_not_positive` | 1,034 |
| `trans_date_after_filing` | 1 |
| **Total excluded** | **47,111** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 484 | 8.4% |
| No plan (AFF10B5ONE = 0/false) | 5,301 | 91.6% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 122 | 2.1% |
| ESPP or dividend reinvestment (footnote heuristic) | 106 | 1.8% |
| Joint filing (more than one reporting owner) | 1,216 | 21.0% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 4,672, `false` 629, `1` 477, `true` 7.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 398, no_plan 1. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 36, dividend reinvestment 73, IPO 16, PIPE 6, directed share program 11, from the issuer 12, private placement 35, privately negotiated 9, public offering 67, registered direct 1, rights offering 1, securities purchase agreement 12, subscription agreement 4, underwritten 30.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 467
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 6,330, `false` 526, `1` 1
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001062993-23-018574 | SOLENO THERAPEUTICS INC | public offering | Purchased in the Issuer's registered public offering scheduled to close on October 2, 2023. |
| 0001683168-23-006669 | PAM TRANSPORTATION SERVICES INC | privately negotiated | stock, individually, to the 2020 Lindsay Moroun Trust in a privately negotiated transaction. The reporting person serves as trustee of the 2020 Lindsay Moroun Trust. On August 3, |
| 0000950170-23-049696 | UNIVERSAL LOGISTICS HOLDINGS, INC. | privately negotiated | as decanted November 28, 2020 (the ""Swiftsure Trust""), in privately negotiated transactions." On August 3, 2023, the Reporting Person filed a Form 4 which reported a purchase pri |
| 0000950170-23-049696 | UNIVERSAL LOGISTICS HOLDINGS, INC. | privately negotiated | as decanted November 28, 2020 (the ""Swiftsure Trust""), in privately negotiated transactions." On August 3, 2023, the Reporting Person filed a Form 4 which reported a purchase pri |
| 0001213900-23-078953 | BYTE Acquisition Corp. | privately negotiated | (""Class A Shares""), either in the open market or through privately negotiated transactions, at a price no higher than the redemption price per share that would be payable to pub |
| 0000950170-23-049296 | Alpha Teknova, Inc. | private placement | Shares purchased in a private placement of Alpha Teknova, Inc. |
| 0000950170-23-049296 | Alpha Teknova, Inc. | private placement | Shares purchased in a private placement of Alpha Teknova, Inc. |
| 0001209191-23-050305 | RayzeBio, Inc. | public offering, IPO | The shares were purchased in the Issuer's initial public offering. |
| 0001209191-23-050305 | RayzeBio, Inc. | public offering, IPO | The shares were purchased in the Issuer's initial public offering. |
| 0001850902-23-000041 | Alpha Teknova, Inc. | private placement | Shares purchased in private placement of Alpha Teknova, Inc. |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0000074260-23-000088 | OLD REPUBLIC INTERNATIONAL CORP | dividend reinvestment | Trade executed by Dividend Reinvestment Plan. |
| 0000715579-23-000083 | ACNB CORP | dividend reinvestment | omatic reinvestment of dividends under the ACNB Corporation Dividend Reinvestment and Stock Purchase Plan, which are exempt from the reporting requirements of Section 16 of the Sec |
| 0000715579-23-000075 | ACNB CORP | dividend reinvestment | omatic reinvestment of dividends under the ACNB Corporation Dividend Reinvestment and Stock Purchase Plan, which are exempt from the reporting requirements of Section 16 of the Sec |
| 0001127602-23-024297 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for eac |
| 0001127602-23-024295 | KINGSWAY FINANCIAL SERVICES INC | ESPP | Plan, as amended and restated effective May 29, 2014 (the ""ESPP""). Pursuant to the ESPP, eligible employees may contribute an amount up to 5% of adjusted salary for eac |
