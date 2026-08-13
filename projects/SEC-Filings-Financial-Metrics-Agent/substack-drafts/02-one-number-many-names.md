# One Number, Many Names
### The part of the project I thought would be easy, and wasn't

_Ash Shejwal · Mycroft Project · July 2026_

---

I assumed the hard part of a filings tool would be getting the data. It isn't. EDGAR actually hands you clean, structured XBRL through a perfectly decent API, and that piece took an afternoon. The trouble started the moment I tried to line two companies up next to each other.

One of them called its top line "Net Sales." Another called what was more or less the same thing "Revenue from Contracts with Customers." A third had gone and invented its own custom tag for it. Three labels, one idea, roughly — and my code had no business assuming they were interchangeable. If it guessed wrong, nothing would break. It would simply produce a clean, confident, wrong number, which is so much worse than a crash, because a crash at least tells you something is off.

That, it turns out, is the whole project in a single example. Building financial data you can trust isn't really about writing more code. It's about deciding when two things genuinely mean the same thing, and being able to show your work when someone questions you.

Here's where I landed. For each thing I care about — revenue, net income, total assets, and so on — I keep an ordered list of the tags a company might have used, best guess first. Revenue, for instance, tries the modern contracts-with-customers tag before falling back to older ones like plain "Revenues" or the legacy "SalesRevenueNet." The extractor walks that list, takes the first tag the company actually reports, and then does the thing I think matters most: it records which tag it used, on every value. The decision doesn't get buried somewhere in the logic. It rides along with the number, so anyone can look at it later and argue with me if they'd like to.

And when none of the tags match? I don't drop the metric, and I definitely don't invent one. It gets flagged as missing, with a note that this company is probably using a custom extension I haven't mapped yet. The gap becomes a visible to-do instead of a quiet hole in the data.

It sounds like a small thing. It's the difference between a dataset I could defend in front of a room and one I'm merely hoping is right. A single mismatched tag doesn't stay put; it bends a margin, drags a trend line, quietly poisons every comparison downstream of it. The big data vendors pay teams to get this exact thing right and then keep the method behind a paywall. Doing it out in the open, where you can check my reasoning, is most of what I think this project is for.

The lesson landed earlier than I expected and it has stuck with me: the numbers are almost never just numbers. Revenue wears different names. Filings get restated. Companies mint their own tags. The work was never in fetching the value. It was in earning the right to call two of them the same.
