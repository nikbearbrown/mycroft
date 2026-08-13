# PASS, FAIL, or UNKNOWN
### On building something that's allowed to say "I'm not sure"

_Ash Shejwal · Mycroft Project · July 2026_

---

A program that crashes is at least honest about it. You know something went wrong. The failure I actually lose sleep over is the quiet one: the system that hands you a wrong number in the same clean formatting as a right one and lets you go on believing it.

That's the failure that does real damage in finance, because a figure looks authoritative whether or not the data under it is any good. So I decided fairly early that checking the numbers would get as much of my attention as pulling them, and that every check would be allowed three answers instead of the usual two. Pass, fail, or "I don't know."

The third answer is the one I'm most attached to, and honestly it took me a while to get comfortable letting the system say it. Most validation is built to pass or fail and nothing in between. But a lot of the time neither is true, because the data I'd need to actually judge a period simply isn't there. If I quietly call that a pass, I've manufactured confidence out of thin air. If I call it a failure, I'm crying wolf. "Unknown" says the only honest thing available, which is that I can't tell yet, and it keeps that uncertainty out in the open instead of smoothing it away.

Two checks are running so far. The first is just the accounting identity: assets should equal liabilities plus equity. When all three are present for a period, it compares them with a small tolerance for rounding. Across Microsoft's filings, every period that had the full set balanced exactly. The ones missing a piece came back "unknown" rather than a false pass, and there were more of those than I'd assumed there would be, which is itself something worth knowing.

The second one checks that a margin can't come out above 100% of revenue. That rule exists because of a specific number I tripped over early on: a sample floating around the ecosystem reported a 310% gross margin. Not just wrong, impossible. And nothing downstream had flagged it, because a polished dashboard doesn't care whether its inputs make any sense. A rule of about three lines catches it on sight. Neither of these checks needs a model, and both are more trustworthy than one would be.

There's a larger idea underneath all of this, and it's more or less the reason I'm doing the project at all. Automating something makes it faster; it doesn't make it correct. Skip the checking and all you've really done is speed up the rate at which you produce mistakes, wrapped in the same tidy formatting as everything that's true.

So I've been trying to build something that's honest about its own limits. Next up are a few more checks — unit consistency, handling restatements, cross-checking subtotals against their parts — each with the same three possible answers. I'm not chasing a system that's always certain. I'd settle for one that's always straight with you about how certain it really is.
