# 97. Fundamental Themes

## Appendix: Friction, Phase Gates, and Accountable Finance Work

Mycroft Finance Recipe Engine rests on one claim: AI made finance execution cheaper, but it did not make finance judgment cheaper. The repo's recipes, logs, reports, and gates exist to preserve that distinction.

## Theme 1: Friction Protects Judgment

Good finance work contains useful friction: source checks, version checks, control totals, threshold reviews, owner confirmations, and release gates. These are not administrative annoyances. They are the mechanism that keeps fluent output from becoming false confidence.

## Theme 2: Phase Gates Are the Boundary

A phase gate is the point where AI assistance stops and accountable human work begins:

- AI may compute a variance; a human explains it.
- AI may match subledger records; a human signs off.
- AI may flag a liquidity threshold breach; treasury decides what to do.
- AI may assemble control evidence; audit/control humans conclude.
- AI may compare contract terms to billing setup; accounting decides policy treatment.

The gate is not mistrust of AI. It is respect for the human responsibility on the other side.

![The phase gate shown across five recipe families — variance, reconciliation, liquidity, control evidence, and contract-versus-billing — with AI preparation on one side and accountable human judgment on the other.](images/97-fundamental-themes-fig-01.png)
*Figure 97.1 — The phase gate across five recipe families*

## Theme 3: Provenance Beats Polish

A rough table with source paths, caveats, and owners is more useful than a smooth paragraph that cannot be traced. In finance, polish without provenance is a risk multiplier.

## Theme 4: Two Customers

Every recipe has two customers. The agent needs schemas, steps, logs, and stop conditions. The finance human needs purpose, evidence, caveats, owners, decisions, and gates. One artifact cannot serve both.

## Theme 5: Humans Plus AI

AI helps with extraction, normalization, comparison, matching, flagging, formatting, and drafting. Humans handle materiality, interpretation, accounting treatment, cash action, control conclusion, release, and accountability.

![Division of labor between AI and humans — AI on extraction, normalization, comparison, matching, flagging, formatting, and drafting; humans on materiality, interpretation, accounting treatment, cash action, control conclusion, release, and accountability.](images/97-fundamental-themes-fig-02.png)
*Figure 97.2 — Humans plus AI: division of labor*

## Practitioner Doctrine

1. Treat generated finance text as an artifact, not evidence.
2. Never explain a variance without a driver or owner.
3. Never confuse parser success with finance adequacy.
4. Never let the recipe set materiality silently.
5. Never automate journal posting, payment release, filing, public disclosure, or investor communication.
6. Keep logs for agents and reports for humans.
7. Preserve unresolved items where reviewers can see them.
8. Make every gate testable.
9. Reward honest blockers over hidden risk.
10. Use AI to make finance judgment more available, not less necessary.

---

## Prompts

### Figure 97.1 — The phase gate across five recipe families
**Files:** images/97-fundamental-themes-fig-01.svg
**Prompt:** Five stacked recipe families — variance, reconciliation, liquidity, control evidence, contract-vs-billing — each crossing a single shared gate line that separates AI preparation from accountable human judgment. The gate is the loudest mark. Ink on white, one red accent.

### Figure 97.2 — Humans plus AI: division of labor
**Files:** images/97-fundamental-themes-fig-02.svg
**Prompt:** A two-column division of labor — AI tasks (extraction, normalization, comparison, matching, flagging, formatting, drafting) against human tasks (materiality, interpretation, accounting treatment, cash action, control conclusion, release, accountability). Neutral on the AI side, red-accented on the human side. Flat, ink on white.
