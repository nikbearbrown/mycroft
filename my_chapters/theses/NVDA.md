**. Extracted Claims**

1. "NVDA is a screaming buy right now."  
2. "Nvidia owns 90% of the AI chip market."  
3. "That moat is unbreakable — nobody can catch CUDA."  
4. "Data center revenue is growing triple digits year over year."  
5. "\[Data center revenue growth\] shows no sign of slowing."  
6. "Management is world-class."  
7. "Jensen is the best CEO in tech."  
8. "The stock is actually cheap when you look at it on a growth-adjusted basis."  
9. "A PEG under 1 is a steal." (implies PEG is currently under 1\)  
10. "The options market is screaming bullish."  
11. "Calls are way more expensive than puts."  
12. "Institutions are loading up."  
13. "There's easy upside to $250 by year end."  
14. "The only risk is if you don't own it."

**2–3. Table**

| \# | Claim | Tag | Reason | Evidence-needed |
| :---- | :---- | :---- | :---- | :---- |
| 1 | NVDA is a screaming buy right now | taste | Pure recommendation, not a factual claim | — |
| 2 | Owns 90% of the AI chip market | needs-a-source | Specific market-share number stated as fact, no source given, and "AI chip market" isn't a standardized category (GPU-only? incl. ASICs/TPUs?) | Cannot verify at all until "90% of what" is defined: unit share or revenue share? GPUs only, or all AI chips including TPUs/ASICs? |
| 3 | Moat is unbreakable — nobody can catch CUDA | unsupported | "Unbreakable" is an absolute, unfalsifiable claim about the future; no evidence trail possible for a permanence claim | Not settleable by a single document — closest proxies are developer-ecosystem surveys, competitor capex on alternative software stacks (ROCm, Triton, TensorRT alternatives), and customer concentration/multi-sourcing disclosures in customers' own 10-Ks |
| 4 | Data center revenue growing triple digits YoY | Needs-a-source | This is a specific, filed number that either matches the last reported quarter or doesn't | NVDA's most recent 10-Q/10-K, Data Center segment revenue line, YoY % calculated directly from it |
| 5 | Shows no sign of slowing | unsupported | Forward-looking assertion with no data cited; sequential deceleration or guidance commentary could contradict this | Sequential (QoQ) growth rate trend over last 3-4 quarters \+ forward guidance language in the most recent earnings call/press release |
| 6 | Management is world-class | taste | Qualitative judgment, not falsifiable | — |
| 7 | Jensen is the best CEO in tech | taste | Superlative opinion | — |
| 8 | Stock is cheap on a growth-adjusted basis | taste | "Cheap" is a valuation judgment even when hung on a metric | — |
| 9 | PEG under 1 | needs-a-source | Specific number implied, no calculation shown, and PEG depends entirely on which forward EPS estimate and which growth period (1yr fwd vs 5yr) you use | Current NVDA trailing/forward P/E from filings or a quote source, divided by consensus long-term EPS growth estimate — need to know which growth figure (analyst consensus vs. historical) is being used |
| 10 | Options market is screaming bullish | unsupported | Vague characterization with no metric attached | Put/call ratio and implied volatility skew for a specific NVDA expiration, sourced from the options chain |
| 11 | Calls way more expensive than puts | needs-a-source | This is really an IV-skew claim; "more expensive" needs a specific strike/expiration comparison to mean anything (calls and puts at different strikes aren't comparable) | NVDA options chain: compare IV of equidistant OTM calls vs. OTM puts at the same expiration (e.g. 30-day, 25-delta each side) |
| 12 | Institutions are loading up | unsupported | No timeframe, no filing referenced, no definition of "institutions" | Structurally unverifiable in the present tense — 13F filings are always \~45 days old, so they can never confirm what institutions are doing "right now." Do not chase this; treat as permanently unsupported. |
| 13 | Easy upside to $250 by year end | unsupported | Price target with no valuation model, timeframe rationale, or multiple assumption shown | Would need the underlying model — e.g. assumed forward EPS × assumed multiple, or DCF assumptions — none of which is given here |
| 14 | The only risk is if you don't own it | unsupported | This is rhetorical, not a claim about risk (dismisses real risks like valuation compression, competition, export controls, capex digestion at hyperscaler customers) | Not a fact to verify — flag as an unfalsifiable framing device rather than an omitted-risk item to source |

**NEEDS HUMAN**

* **Claim 2 (90% market share):** I don't know what specific market/metric this figure is meant to represent (unit share of AI accelerators? revenue share? data center GPU only?) — you'll need to pin down which stat is actually being cited.  
* **Claim 4 (triple-digit growth):** I don't know which quarter this thesis is referring to — "triple digits YoY" was true in some past quarters and not others, so you need to check it against the specific period the thesis-writer had in mind.  
* **Claim 9 (PEG \< 1):** I can't tell which growth rate or EPS estimate is being used to get this number — could be cherry-picked from a specific analyst or a specific timeframe.  
* **Claim 11 (calls more expensive than puts):** I don't know if this means IV skew, raw premium, or volume/OI — these are three different things and the thesis conflates them.  
* **Claim 13 ($250 by year end):** No model, multiple, or EPS assumption is given, so there's no way to identify what evidence would even confirm or deny this — it's a bare assertion.


---

## Exercise 5 — Validation (human-run gate)

Checklist run against the table above:
1. Correctness — PASS. No claim is tagged "verified"; nothing false claims to be verified.
2. Completeness — PASS. All 14 claims extracted, including the smuggled price target and the buried "buy."
3. Scope — PASS. No rating, target, or buy/sell opinion was added by the model.
4. Signal vs noise — PASS. The "calls more expensive than puts" claim was flagged needs-a-source, not narrated as real.
5. Owner test — PASS. Each needs-a-source claim names specific evidence; "institutions loading up" marked structurally unverifiable.
6. Failure-mode check — PASS. All confident-but-unfounded sentences quarantined as taste/unsupported.

Result: all six PASS → table filed, proceed.

## AI Use Disclosure
Claude split the NVDA thesis into 14 distinct claims and proposed a tag for each; I used its
output as a first-draft audit and corrected it by hand, downgrading the "triple-digit growth"
claim from verified to needs-a-source and marking "institutions are loading up" as structurally
unverifiable. The AI could not determine which claims are truly verified (that needs me to open
the actual filing and options chain), whether the options signal is real positioning or retail
noise, or whether I could defend this trade — those required my judgment.