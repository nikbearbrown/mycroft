# Trust Before Intelligence
### The least glamorous part of the pipeline is the part I keep coming back to

_Ash Shejwal · Mycroft Project · July 2026_

---

When I tell people I'm building an AI system for SEC filings, they picture the model doing something clever. Most of what I actually did this week was duller than that, and I've made my peace with it. I spent it making sure that when the system says a company earned some amount in revenue, that number really is revenue, from the right filing, for the right period, before anything remotely "intelligent" gets near it.

There's a reason I put things in that order. A large language model is very convincing, and that's sort of the problem. It can hand you a revenue figure that was quietly pulled from a restated filing, or mapped off the wrong XBRL tag, or shifted by a quarter, and then describe that figure in fluent, confident prose. If the input is wrong, the fluency doesn't rescue you. It just makes the mistake harder to doubt.

So the agent is deliberately slow to get clever. Retrieval, extraction, the validation checks: all of it is plain, deterministic code. A short rule that asks whether assets equal liabilities plus equity will catch an impossible balance sheet far more reliably than any amount of probabilistic reasoning, and it does it the same way every single time. I'd take that over something impressive.

A few habits fall out of this, none of which will ever show up in a demo. Every number I extract carries its receipts: the exact tag it came from, the accession number, the form, the period, the date filed, and a link back to the document itself. If I can't trace it, I don't trust it, and I don't think anyone reading it should either. I also keep EDGAR's raw response exactly as it arrived, so any figure can be rebuilt later from the same source I was looking at. It's not exciting. It's the whole point.

The first working version already runs against live filings. For Microsoft it pulls a couple thousand data points across sixteen years, reports FY2025 revenue of about $281.7 billion from the correct tag, and its balance sheet actually balances, down to the dollar. Not because the code is smart — there's no model in that path at all — but because something bothered to check.

I want to be clear that none of this is an argument against AI. It's an argument about when to reach for it. Once the numbers underneath are solid, the layers I'm genuinely excited about — summarizing the narrative sections, pulling in context, flagging strange movements from one year to the next — become worth doing, because they're standing on something that holds. Put them first and you've just built a very articulate way to be wrong.

I didn't set out to make an AI that reasons like an analyst. I set out to make the collecting-and-checking fast and honest, so that the people using it — a student, a reporter, someone just trying to get through a 10-K — can spend their time on the part that actually needs a person.
