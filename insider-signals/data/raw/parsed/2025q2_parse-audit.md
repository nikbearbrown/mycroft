# PARSE audit — 2025q2

Source: SEC Insider Transactions Data Set 2025q2 (ZIP SHA-256 `64e7f81328933b1281bd8737961048d76d2ab3d5d1d2d7149a32ec061b0e3ff2`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 66,915 | |
| Form 4 / 4-A rows | 66,719 | 100.0% |
| … with code P | 6,399 | 9.6% |
| … qualifying buys | 6,297 | 9.4% |

Rows by document type (all forms): 4: 65,709, 4/A: 1,010, 5: 173, 5/A: 23.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 18,965 |
| `code_C_conversion` | 696 |
| `code_D_disposition_to_issuer` | 1,608 |
| `code_F_tax_or_exercise_payment` | 9,039 |
| `code_G_gift` | 1,238 |
| `code_I_discretionary_16b3f` | 35 |
| `code_J_other` | 1,796 |
| `code_L_small_acquisition` | 58 |
| `code_M_option_exercise_16b3` | 9,507 |
| `code_O_option_exercise_otm` | 1 |
| `code_S_sale` | 17,165 |
| `code_U_tender_change_of_control` | 109 |
| `code_W_will_or_descent` | 16 |
| `code_X_option_exercise_itm` | 87 |
| `p_not_acquired` | 29 |
| `p_shares_missing_or_not_positive` | 18 |
| `p_price_missing_or_not_positive` | 49 |
| `p_equity_swap` | 3 |
| `trans_date_after_filing` | 3 |
| **Total excluded** | **60,422** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 743 | 11.8% |
| No plan (AFF10B5ONE = 0/false) | 5,554 | 88.2% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 100 | 1.6% |
| ESPP or dividend reinvestment (footnote heuristic) | 74 | 1.2% |
| Joint filing (more than one reporting owner) | 1,152 | 18.3% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 4,529, `false` 1,025, `1` 727, `true` 16.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: no_plan 5, plan 612. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 22, dividend reinvestment 52, IPO 11, PIPE 3, directed share program 12, from the issuer 11, private placement 36, privately negotiated 7, public offering 33, rights offering 3, securities purchase agreement 11, subscription agreement 5, underwritten 24.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 297
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 5,554, `false` 842, `1` 3
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0000950170-25-091829 | Kymera Therapeutics, Inc. | underwritten | f Kymera Therapeutics, Inc. (the ""Issuer"") pursuant to an underwritten offering that closed on June 30, 2025." |
| 0000950170-25-091829 | Kymera Therapeutics, Inc. | underwritten | f Kymera Therapeutics, Inc. (the ""Issuer"") pursuant to an underwritten offering that closed on June 30, 2025." |
| 0000950170-25-091735 | 5C Lending Partners Corp. | subscription agreement | issuer in the form of a capital call. Under the terms of a subscription agreement between the reporting persons and the issuer, the reporting persons are required to fund drawdown |
| 0001104659-25-063993 | ACTUATE THERAPEUTICS, INC. | private placement, securities purchase agreement, from the issuer | LP (""Bios 2024 Co-Invest"") purchased from the Issuer in a private placement 71,428 shares of common stock, par value $0.000001 per share (the ""Common Stock""), and warrants to p |
| 0001104659-25-063992 | ACTUATE THERAPEUTICS, INC. | private placement, securities purchase agreement, from the issuer | LP (""Bios 2024 Co-Invest"") purchased from the Issuer in a private placement 71,428 shares of common stock, par value $0.000001 per share (the ""Common Stock""), and warrants to p |
| 0001104659-25-063991 | ACTUATE THERAPEUTICS, INC. | private placement, securities purchase agreement, from the issuer | LP (""Bios 2024 Co-Invest"") purchased from the Issuer in a private placement 71,428 shares of common stock, par value $0.000001 per share (the ""Common Stock""), and warrants to p |
| 0001213900-25-059081 | Cantor Equity Partners III, Inc. | private placement | Cantor EP Holdings III, LLC (the ""Sponsor"") pursuant to a private placement shares purchase agreement, dated June 25, 2025, by and between the Sponsor and the issuer." |
| 0000950170-25-090878 | Churchill Capital Corp X/Cayman | private placement | "Represents shares underlying the private placement units (each unit consisting of one Class A ordinary share and one-quarter of one warrant, each whole warrant exercisable to purc |
| 0001213900-25-058680 | Bit Digital, Inc | public offering, underwritten | the reporting person expects to acquire in an underwritten public offering at a purchase price of $2.00 per share. The underwritten public offering is expected to close on June 27 |
| 0001104659-25-063044 | NETLIST INC | securities purchase agreement | per share and accompanying warrant pursuant to that certain Securities Purchase Agreement, dated as of June 24, 2025, by and among the Issuer and the investors signatory thereto. |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001156375-25-000139 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001156375-25-000139 | CME GROUP INC. | dividend reinvestment | Reflects shares that were acquired pursuant to a dividend reinvestment plan administered by the reporting person's broker. Actual amounts of fractional shares owned may vary slight |
| 0001754011-25-000006 | Capital Bancorp Inc | dividend reinvestment | The purchased shares are pursuant to a broker's dividend reinvestment program that qualifies for small acquisition reporting under Rule 16a-6. |
| 0001628280-25-031980 | PHINIA INC. | dividend reinvestment | Reflects shares acquired pursuant to an automatic dividend reinvestment feature of the reporting person's brokerage account. |
| 0001628280-25-031876 | Granite Ridge Resources, Inc. | dividend reinvestment | Shares acquired through automatic dividend reinvestment pursuant to the terms of a brokerage account. |
