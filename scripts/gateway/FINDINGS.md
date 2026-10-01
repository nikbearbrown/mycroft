## 10. What the scorer check showed

Sprint 6. 32 pairs — 8 open-ended fixtures, 4 independently generated answer
pairs each — scored twice: once by the strong-model judge from section 9, once
by a human who could not see which tier wrote which answer, could not see the
judge's verdict, and was shown the two answers in a seeded random order so that
the human's own position bias could be measured the same way the judge's was.

|  | picked cheap | picked mid | tie |
|---|---|---|---|
| human | 11 | 16 | 5 |
| judge | 0 | 0 | 28 |

Four further pairs got no verdict at all: the judge contradicted itself when the
answers were swapped.

**Cohen's kappa is 0.00.** Raw agreement was 18%, which is exactly what chance
predicts given the two distributions. Per task type: `rag_answer` 27% raw, kappa
0.00; `summarization` 8% raw, kappa 0.00. Not weak agreement -- none.

**The judge never once picked a winner; the human picked one on 27 of 32.** A
rater that uses a single category has no discrimination to measure, so there is
nothing here to calibrate or tune toward. The judge is not a weak instrument for
these tasks, it is not an instrument.

**Section 9's main conclusion is withdrawn.** "On open-ended work, mid bought
nothing measurable over cheap -- 10 ties, 1 mid win, 0 cheap wins" was a
property of the instrument, not of the models. A human reading the same kind of
pairs saw a difference in 27 of 32 and favoured mid 16 to 11. Section 9 stays as
written, because the record is append-only; this section supersedes its
conclusion.

**The human showed no detectable order bias**: 13 picks for the first answer
shown, 14 for the second. The judge flipped its verdict on 4 pairs when the
order changed. Of the two raters, the one that cannot scale is the one whose
judgments are stable.

**Caveat, from the human's own notes.** Three notes read "more detailed", "well
detailed", "more clearer". The mid tier writes longer answers, so some of the
16-11 split may be a preference for thoroughness rather than for correctness.
This is a confound to watch in Sprint 7, not a reason to discount a kappa of
zero.

**Scope.** 32 pairs over 8 distinct fixtures. Four samples of one fixture are
four observations of the same task, not four tasks, so the effective coverage
is 8.

### Consequences

- The pairwise judge is retired as a quality measure for `summarization` and
  `rag_answer`. No number it produced may be quoted as a quality figure.
- Sprint 7's baseline reports judged quality for no prose task. Those two task
  types carry cost, latency and check-pass rate only, with quality recorded as
  unmeasured.
- Sprint 8's ship / don't-ship decision rests on the four task types that have
  an answer key, plus cost and latency everywhere. If that is not enough to
  decide, the honest outcome is "undecidable on the available evidence".
- The next cheap experiment is to remove TIE from the judge's options and force
  a choice, then re-measure. It separates two diagnoses that look identical from
  the outside: a judge that cannot tell these answers apart, and a judge that
  can but takes the safe option. One prompt change, 32 pairs, about two cents.
- Blind, independent scoring found this one week after the number was produced.
  The same discipline applied to section 9 at the time would have caught it
  immediately; the lesson is to run the check in the same sprint as the claim.