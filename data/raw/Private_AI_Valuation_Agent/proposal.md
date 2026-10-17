# Private AI Valuation Agent — proposal

## The problem

Most of the AI sector's value sits in companies you cannot buy and cannot see into — OpenAI,
Anthropic, xAI, Databricks, Anduril. No ticker, no earnings call, no 10-K. The numbers that do
circulate come from press reports of funding rounds, which are announcements rather than
disclosures, and which say nothing between rounds.

But US registered funds must disclose **every** portfolio position on SEC Form N-PORT,
including private ones, with a dollar value and a share count. Divide one by the other and you
have a price per share for a company with no public price — filed, dated, and attributable to
a named fund.

## What this project builds

An open, reproducible price history for a frozen cohort of private AI companies, derived
entirely from SEC filings, with every number traceable to the filing that produced it.

Its most distinctive output is **propagation**: how long a new valuation takes to travel across
independent fund managers. That measurement is possible only because fund fiscal quarter-ends
are staggered across the calendar, so the same company is priced by different managers on
different dates, and the spread between them is observable.

## Scope, and the honest version of it

**Supported** — arithmetic on disclosed figures:

- price per share, per fund, per security, per period
- re-mark versus carry-forward (a zero change and a carry-forward are different facts)
- cross-manager dispersion within a window, with a minimum-holders threshold
- propagation lag around repricing events
- exposure: who holds what, at what percent of fund net assets
- entry date and cost, from the Reg S-X 12-12 restricted-securities footnote
- offering dates and amounts, from Form D, joined on a human-affirmed issuer identity

**Not supported, structurally:**

- **Company valuation.** N-PORT gives the *fund's* share count, never the company's shares
  outstanding. Every alternative was checked and rejected: Form D carries no share count or
  price; Delaware franchise filings give authorized and issued shares per-document for a fee,
  not fully diluted and not by series; secondary marketplaces are paywalled and are themselves
  estimates, which makes the whole thing circular; and the 1940 Act affiliate threshold never
  triggers at OpenAI or Anthropic scale. **This project does not publish company valuations**,
  and the signal contract refuses ten field names by name to keep it that way.
- **Anything timely.** Verified lag is ~55–60 days from fiscal period end to filing, and the
  bulk data sets lag those by up to another ~90. Structurally unsuitable as a trading signal,
  and every output says so.
- **Complete coverage.** Some exposure sits in opaque SPVs that disclose no underlying — the
  project reports the count rather than pretending the gap is not there.

## Prior art, stated up front

It would be false to call this an underused source, and this proposal says so before anyone
else has to.

**Commercially exploited.** [Caplight](https://framer.caplight.com/solutions/investors) holds
20,000+ investment fund marks across 370 late-stage companies and explicitly markets tracking
how BlackRock, Fidelity, Franklin Templeton and Lincoln Financial value their stakes. Notice,
Sacra, Forge and Nasdaq Private Market operate in adjacent space.

**Academically mature.**

- Agarwal, Barber, Cheng, Hameed & Yasuda, "Private Company Valuations by Mutual Funds,"
  *Review of Finance* 27(2), 2023.
- Gornall & Strebulaev, "Squaring Venture Capital Valuations with Reality," *JFE*, 2020.
- Chernenko, Lerner & Zeng, "Mutual Funds as Venture Capitalists? Evidence from Unicorns," *RFS*.
- Kwon, Lowry & Qian, "Mutual Fund Investments in Private Firms," *JFE*.

Gornall & Strebulaev in particular is not merely cited here but **reproduced**: funds write up
*all* share classes to the latest round price, which is why this project measures dispersion at
company level while recording the class, rather than within-class only.

**What does not exist** is an open, reproducible, continuously-updated, AI-cohort-specific
artifact. No public repository parses N-PORT for private-company marks; the GitHub "unicorn
dataset" projects are static Crunchbase scrapes, not filings-derived.

**The contribution is open infrastructure, not discovery.** Claiming novelty of the data source
would not survive a literature review, and this project does not claim it.

## What was actually measured

Four findings, two of which contradict the plan's own expectations — recorded as such rather
than quietly adjusted.

| | measured | expected |
|---|---|---|
| Consecutive observations unchanged | **25.0%** | 30–40% |
| Same-date spread across managers, median | **10.8%** | "they mostly don't disagree" |
| A new price level reaching half its holders | **30 days** | not quantified |
| Fund entry dates landing on a filed round date | **10 of 18** | not anticipated |

The last is the one worth the most. An issuer files Form D because it sold securities; a fund
files N-CSR because it owns them. Neither cites the other, so their agreement to the day is
evidence rather than arithmetic.

## Method, in one paragraph

Bulk SEC data sets are downloaded and converted to Parquet; DuckDB filters ~10–15M holding rows
a quarter down to the private layer; a frozen set of name patterns narrows that to a candidate
universe; a deterministic matcher resolves holdings to companies and share classes, escalating
only genuine ambiguity to a human through a checkpointed review queue that survives a restart;
prices are computed once at ingest under one null rule; a split detector quarantines suspected
splits rather than auto-adjusting them; and the resulting panel is measured, published as a
versioned JSON signal, and served read-only over MCP.

## Why the design is shaped the way it is

**Machines verify conformance; humans verify adequacy.** The matcher proposes and a named
reviewer decides. 1,269 of 5,806 holdings carry a human decision. No gate clears itself, and
the MCP server deliberately exposes no tool that could record one.

**Never invent a number.** Every figure traces report → log → script → recipe → source. Where a
figure is withheld it is carried as an explicit reason rather than a missing key, so a consumer
can tell "we did not publish this" from "there was nothing to publish".

**Refuse rather than approximate.** The split detector blocks a change series instead of
guessing a factor. The commentary refuses to write a note rather than substituting a template.
The signal refuses a valuation field rather than leaving one for someone to fill from
elsewhere.

## Cost

Zero. Free SEC bulk data, a local Postgres or a Supabase free tier, a local Ollama model for
entity-resolution adjudication, and a free Groq tier for quarterly commentary. No paid service
and no key beyond the free tier.
