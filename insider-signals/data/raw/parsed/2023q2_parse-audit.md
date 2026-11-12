# PARSE audit — 2023q2

Source: SEC Insider Transactions Data Set 2023q2 (ZIP SHA-256 `7e636787231ae0f00accf5c3627298402dedd1aefffd7c50fb48292e5d3a8fbb`). Produced by `parse.py`. This audit reports what was found. It does not say pass, and nothing here has entered `data/verified/`.

## Funnel

| Step | Rows | Share of Form 4 rows |
|---|---:|---:|
| Non-derivative transaction rows, all forms | 68,588 | |
| Form 4 / 4-A rows | 68,493 | 100.0% |
| … with code P | 8,238 | 12.0% |
| … qualifying buys | 7,964 | 11.6% |

Rows by document type (all forms): 4: 67,342, 4/A: 1,151, 5: 91, 5/A: 4.

## Exclusions by reason (Form 4 / 4-A rows)

Each excluded row has exactly one reason: the first check it fails, in this order.

| Reason | Rows |
|---|---:|
| `code_A_grant_award` | 19,860 |
| `code_C_conversion` | 902 |
| `code_D_disposition_to_issuer` | 1,083 |
| `code_F_tax_or_exercise_payment` | 9,093 |
| `code_G_gift` | 1,269 |
| `code_I_discretionary_16b3f` | 59 |
| `code_J_other` | 2,109 |
| `code_L_small_acquisition` | 81 |
| `code_M_option_exercise_16b3` | 9,851 |
| `code_S_sale` | 15,766 |
| `code_U_tender_change_of_control` | 53 |
| `code_W_will_or_descent` | 21 |
| `code_X_option_exercise_itm` | 104 |
| `code_Z_voting_trust` | 4 |
| `p_not_acquired` | 21 |
| `p_shares_missing_or_not_positive` | 7 |
| `p_price_missing_or_not_positive` | 245 |
| `trans_date_after_filing` | 1 |
| **Total excluded** | **60,529** |

## Flags on qualifying buys (flagged, not excluded)

| Flag | Buys | Share of qualifying |
|---|---:|---:|
| 10b5-1 plan (AFF10B5ONE = 1/true) | 266 | 3.3% |
| No plan (AFF10B5ONE = 0/false) | 7,698 | 96.7% |
| Unknown (AFF10B5ONE blank or unrecognized) | 0 | 0.0% |
| Likely private / issuer purchase (footnote heuristic) | 76 | 1.0% |
| ESPP or dividend reinvestment (footnote heuristic) | 102 | 1.3% |
| Joint filing (more than one reporting owner) | 960 | 12.1% |

Raw `AFF10B5ONE` values on qualifying buys: `0` 6,944, `false` 754, `1` 239, `true` 27.
Footnotes mentioning "10b5-1" on qualifying buys, by normalized flag: plan 172, no_plan 54. This is a finding only and does not change the flag.

Footnote phrases matched: ESPP 25, dividend reinvestment 78, IPO 14, PIPE 5, directed share program 11, from the issuer 4, private placement 20, public offering 40, registered direct 2, securities purchase agreement 21, subscription agreement 5, underwritten 17.

Flags read only footnotes on the transaction's own fields (date, shares, price, code, security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a `[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are excluded is undecided. Review the samples below.

## Context

- Form 4 code P rows in the derivative table (excluded by design, not counted above): 374
- Form 4 rows whose accession has no reporting owner: 0
- Non-derivative rows with no matching submission: 0
- `EQUITY_SWAP_INVOLVED` raw values on code P rows: `0` 7,663, `false` 575
- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: none
- `AFF10B5ONE` column present: True

## Samples for review — likely private / issuer purchases (first 10)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001493152-23-023195 | Progressive Care Inc. | securities purchase agreement | On May 5, 2023, the Issuer entered into a Securities Purchase Agreement with NextPlat Corp, whereby NextPlat Corp. agreed to purchase 455,000 units of securities, consisting of one |
| 0001493152-23-023194 | Progressive Care Inc. | securities purchase agreement | On May 5, 2023, the Issuer entered into a Securities Purchase Agreement with NextPlat Corp, whereby NextPlat Corp. agreed to purchase 455,000 units of securities, consisting of one |
| 0001209191-23-040091 | IGM Biosciences, Inc. | public offering, underwritten | The shares were purchased pursuant to an underwritten public offering of the Issuer's securities. |
| 0001104659-23-074791 | Lucid Group, Inc. | private placement, subscription agreement, public offering, underwritten, from the issuer | m the Issuer 265,693,703 shares of Issuer common stock in a private placement for an aggregate purchase price of approximately $1.8 billion in a private placement pursuant to a sub |
| 0001829126-23-004338 | Rubicon Technologies, Inc. | private placement | e Issuer at a per share purchase price of $0.4164 through a private placement transaction. |
| 0001062993-23-013773 | SusGlobal Energy Corp. | private placement | Mr. Rintoul subscribed to the shares in a private placement with the Issuer. |
| 0001493152-23-021689 | LIBERTY STAR URANIUM & METALS CORP. | private placement | une 12,2023, the reporting person acquired share units in a private placement purchase including I share and 1/2 warrant (right to buy) per share. Price is set by an average VWAP 4 |
| 0001209191-23-037307 | Movano Inc. | public offering | son purchased 35,000 shares of Common Stock in the Issuer's public offering at a purchase price of $1.00 per share. |
| 0001209191-23-037306 | Movano Inc. | public offering | son purchased 25,000 shares of Common Stock in the Issuer's public offering at a purchase price of $1.00 per share. |
| 0001209191-23-037304 | Movano Inc. | public offering | son purchased 20,000 shares of Common Stock in the Issuer's public offering at a purchase price of $1.00 per share. |

## Samples for review — ESPP / dividend reinvestment (first 5)

| Accession | Issuer | Matched | Footnote snippet |
|---|---|---|---|
| 0001156375-23-000116 | CME GROUP INC. | dividend reinvestment | Acquisition of shares under a broker-administered dividend reinvestment plan. |
| 0001156375-23-000116 | CME GROUP INC. | dividend reinvestment | Acquisition of shares under a broker-administered dividend reinvestment plan. |
| 0000074260-23-000058 | OLD REPUBLIC INTERNATIONAL CORP | dividend reinvestment | Trade executed pursuant to Dividend Reinvestment Plan. |
| 0000074260-23-000058 | OLD REPUBLIC INTERNATIONAL CORP | dividend reinvestment | Trade executed pursuant to Dividend Reinvestment Plan. |
| 0001821850-23-000052 | Sunlight Financial Holdings Inc. | ESPP | payroll deductions under Sunlight Financial Holdings Inc.'s employee stock purchase plan. |
