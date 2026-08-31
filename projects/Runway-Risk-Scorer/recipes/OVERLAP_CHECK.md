# Overlap check — runway-risk-scorer

Searched all 100 recipes in the Mycroft repo for existing runway or
financial-health work.

Verdict: No recipe computes vendor runway as a standalone, sourced, gated
artifact. The nearest is vendor-intelligence-brief.yaml, whose "Financial Agent"
lists runway among its concerns but treats it as one signal inside a broader
multi-agent brief — not a dedicated computed metric with a human gate.
funding-intelligence-agent.md ingests funding signals but does not score runway
risk.

Conclusion: the runway-risk-scorer fills a real gap — it is the only recipe that
takes validated funding signals and produces a dedicated, fully-sourced
runway-risk brief that halts at a human gate.
