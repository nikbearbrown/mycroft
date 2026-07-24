# Investment Research Desk (Your Own Mycroft)

This desk separates what evidence can establish from what only a human can decide.
Theses (e.g. NVDA) are broken into claims tagged taste, needs-a-source, or unsupported,
each with the evidence that would be required to check it (see theses/NVDA.md).
CANNOT-KNOW.md holds the human-only inputs no model or market data can supply: loss
tolerance, holding horizon, position sizing, and reaction plans for a sudden drop.
Evidence and signals are gathered and logged separately from judgment, and book
tracks decisions actually made. No claim here is "verified" and no trade is placed
by this repo's tooling — those calls stay with a human.

## Table of Contents

- [theses/](theses/) — extracted claims per ticker, tagged and matched to the evidence needed (see theses/NVDA.md)
- [evidence/](evidence/) — sourced material gathered to check claims
- [signals/](signals/) — market/options signals under review
- [book/](book/) — human decisions and trade records
- [CANNOT-KNOW.md](CANNOT-KNOW.md) — human-only inputs: risk tolerance, time horizon, position sizing, drawdown plan
- [CLAUDE.md](CLAUDE.md) — assistant operating rule for this desk
