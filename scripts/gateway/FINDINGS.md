## 9. What the first judged run showed

Three runs on 2026-09-24 -- a 2-fixture smoke (13:29), the full 8 (13:43), and
a 4-fixture re-run after the validator fix (14:00). 14 comparisons, 28 judging
calls, on `summarization` and `rag_answer` only: the tasks where no answer key
can exist. cheap wrote answer A, mid wrote answer B, strong judged, each pair
both ways round.

| result | count |
|---|---|
| tie | 10 |
| mid won | 1 |
| cheap won | 0 |
| inconsistent (verdict flipped when the answers swapped) | 3 |
| unparsed | 0 |

**Judging costs more than answering.** An answer cost $0.000086 on average; a
comparison cost $0.000420 in judging -- 2.4x the cost of producing the two
answers it compares, plus two strong-tier calls of latency. That ratio is the
argument for keeping the judge offline, and it is why a "route by judged
quality" design would be more expensive than always using the strong model.

**Three of 28 answers failed their check over a bracket glyph.** The mid tier
wrote its citation as 【0】 rather than [0], and `cites_context` saw no
citation at all. The answers were correct and cited the right passage. In the
request path each one is an escalation to a dearer tier bought by punctuation
-- the same class of defect as the `verdict_with_quote` false alarms in
section 7, found the same way: by reading what the models actually wrote.
`cites_context` now translates fullwidth brackets before matching, and the
out-of-range check is unchanged, so widening what counts as a bracket did not
widen what counts as a valid passage.

**The judge's disagreements are about degree, not direction.** All three
inconsistent results were `tie` one way round and a winner the other. Not once
did it pick A in one order and B in the other. And all 28 replies were a bare
FIRST / SECOND / TIE at a 256-token budget -- nothing unparseable, no
reasoning leaking into the verdict.

**The same pair judged twice does not give the same verdict.** rag-001 came
back `tie` at 13:29 and `inconsistent` at 13:43 and 14:00. rag-003 came back
`b` at 13:43 and `tie` at 14:00. The models rewrite their answers each run, so
a single sweep is one sample, not a measurement.

**On open prose, mid bought nothing measurable over cheap.** Ten ties, one mid
win, no cheap win. Read this as a hypothesis with evidence behind it, not a
result: the verdicts are model judgments no human has checked yet, the sample
is 8 fixtures, and the answers are one or two sentences long. Sprint 6 is what
decides whether these verdicts can be quoted at all.

### Consequences

- The judge never runs in the request path, and no routing decision reads a
  verdict. It costs more than the work it grades.
- Sprint 6 must hand-score these same pairs blind and measure agreement. Until
  then, no quality number from the judge belongs in a report.
- Sprint 7 needs several runs per fixture, not one: the answers, and therefore
  the verdicts, change between runs.
- A check that rejects a correct answer over formatting is a cost bug, not a
  cosmetic one. Both found so far (quote spans, citation brackets) were
  invisible until someone read the raw answers.