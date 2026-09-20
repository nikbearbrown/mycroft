# Final narration transcript — 03:00 cut

This is the original Mycroft narration used in the final composition. It is
transcribed from the supplied `mp3/beat-*.mp3` assets and synchronized by
measured audio duration at 24 fps. `B10b` is not played in this 03:00 cut;
its authentic evidence is retained visually in Scene 9.

| Time | Beat | Narration |
|---|---|---|
| 00:00–00:14 | B00 | Hi, I’m Dhrumil Shah. I built Mycroft ThesisGuard, an evidence-first review layer for investment research. In the next three minutes: what it does, what the numbers actually showed, and where it refuses to answer. |
| 00:14–00:26 | B01 | Investors buy for a reason. Then the facts move, and the reason quietly gets rewritten. A growth story becomes a value story. Nobody logs the change. That is thesis drift. |
| 00:26–00:35 | B02 | So this is not a buy-or-sell engine. It is a review layer. It asks one question: is your original thesis still supported by the evidence? |
| 00:35–00:44 | B03 | Start with validated market data. One hundred eighty-four thousand rows. One hundred twenty tickers. Every price checked before a model ever sees it. |
| 00:44–00:56 | B04 | Then features that only use what was knowable at the time. Returns. Volatility. Drawdowns. Sector-relative moves. No future data leaks backward into the inputs. |
| 00:56–01:05 | B05 | Split it by time, never at random. Seventy percent to train, fifteen to validate, fifteen held back. Labels that cross a boundary get purged. |
| 01:05–01:12 | B06 | Five models compete. And the plain baseline is allowed to win, because complexity should have to earn its place. |
| 01:12–01:27 | B07 | Logistic regression won. Holdout ROC AUC: zero point five one five eight. Barely above a coin flip. That is the finding, not a failure. Short-horizon price direction was not reliably predictable from this data. |
| 01:27–01:36 | B08 | Feature drift came back moderate. Don’t bury a number like that. Treat uncertainty as a governance signal, not a footnote you hope nobody reads. |
| 01:36–01:52 | B08b | Here’s the part I care about most. The bias agent will not diagnose your psychology from a price chart. Confirmation bias, sunk-cost thinking, overconfidence: real risks, but prices are not evidence of them. So it says so, and names what is missing. |
| 01:52–02:03 | B09 | Then five agents review each company. Capture the thesis. Retrieve the evidence. Detect contradiction. Check for bias. And hand the decision to a human. |
| 02:03–02:14 | B10 | One hundred twenty reports. Six hundred trace events. Zero automated decisions. The gate is the point: the system organizes evidence, it does not act. |
| 02:14–02:23 | B11 | And where evidence is missing, it stops. No thesis on file, no filings, no decision history, so it returns a placeholder, not a verdict. |
| 02:23–02:33 | B12 | So the loop is: validate the data, engineer causal features, split by time, evaluate honestly, monitor drift, review the evidence, then a person decides. |
| 02:33–02:45 | B12b | You can run this on your own thinking today, without any of my code. Write down the claim. Write down what would change your mind. Date your evidence. And when you cannot find a source, stop, and say so. |
| 02:45–02:57 | B13 | The strongest result here isn’t a trading signal. It’s a system that shows its evidence, names its uncertainty, and leaves the judgment where it belongs. Mycroft ThesisGuard. |
| 02:57–03:00 | — | Silent title hold: “Evidence first. Uncertainty visible. Judgment human.” |

This transcript is original Mycroft-specific narration. It does not reproduce
the supplied reference video’s narration or script.

The B12 phrase “then a person decides” describes the **human-owned review
stage**, not a decision that the supplied run completed. The visible Scene 09
label is therefore “Human review,” consistent with `human_decisions_created:
0` and the recorded awaiting-human boundary.
