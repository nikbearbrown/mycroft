# Research Notes: Chapter 05 - News, Sentiment, and Market Awareness

**Source:** TIKTOC.md chapter entry  
**Notes file:** 05-news-sentiment-and-market-awareness_notes.md  
**Corresponding chapter:** chapters/05-chapter-05.md  
**Generated:** 2026-06-06

---

## Chapter summary (from TIKTOC.md)

Capability built: Use news and sentiment workflows without treating volume as truth. The reader studies news monitoring, AI news sentiment, social sentiment, and retail investor anxiety workflows. The chapter emphasizes timestamps, source quality, duplication, sentiment uncertainty, and narrative drift. Whole task: Design a bounded news/sentiment run for one AI company or subsector. Assessment: Source list, time window, output contract, and verification sample.

---

## A. Conceptual foundations

### Sentiment as noisy measurement
Sentiment analysis converts text into labels or scores, but it is not a direct measure of truth, investor conviction, or future returns. It is a noisy proxy for tone in a bounded corpus. The quality of the corpus matters: source mix, duplicates, bots, syndication, publication time, and selection bias can dominate the score.

**Common misconception:** More mentions means stronger evidence. More mentions can mean syndication, outrage, spam, or one repeated story.

**Worked example:** A news workflow finds 200 negative AI-safety mentions about Company X in 24 hours. Verification sample: deduplicate URLs, identify original sources, classify source authority, inspect 20 items manually, and separate event news from commentary.

**Source(s):** FINRA AI fraud warning for manipulated media/social risk, https://www.finra.org/investors/insights/artificial-intelligence-and-investment-fraud; local `recipes/n8n-ai-news-sentiment-agent.md`, `recipes/n8n-social-sentiment-agent.md`, `recipes/n8n-retail-investor-anxiety-index.md`.

### Narrative drift
Market narratives change as new information enters public discussion. A Mycroft news workflow should preserve timestamps and avoid summarizing a moving narrative as a settled conclusion. Use "as of" language and compare time windows.

**Common misconception:** The latest story is the most important story. Sometimes it is a restatement or low-quality reaction.

**Worked example:** Compare sentiment before and after an earnings call, but keep the source sets separate: official release, transcript, analyst coverage, mainstream news, social commentary.

**Source(s):** Local `recipes/n8n-earnings-call-intelligence-agent.md`; `_lib_The_Signal_and_the_Noise...`; `_lib_Calling_Bullshit...`.

---

## B. Domain examples and cases

### Case 1: AI-generated deepfakes and manipulated content
FINRA/SEC/NASAA warn that AI can create fake videos, cloned voices, and misleading images. A sentiment workflow must treat social evidence as vulnerable to manipulation and require source-quality checks.

### Case 2: Retail investor anxiety index
The Mycroft `n8n-retail-investor-anxiety-index.md` recipe can teach the difference between a behavioral signal and a recommendation. Anxiety may explain attention or risk perception; it does not tell the reader what to trade.

### Failure case: Viral volume
A viral thread can overwhelm a sentiment dashboard without adding new facts. The chapter should show duplicate clustering and original-source recovery.

---

## C. Connections and dependencies

**Prerequisites (what reader must already know):**
- Data contract - source, date, duplicate, and generated-score status.
- Recipe-readiness - source window and output contract before execution.

**Unlocks (what this chapter makes possible):**
- Chapter 8 - comparison needs comparable source windows.
- Chapter 10 - portfolio intelligence can include sentiment only as a caveated signal.

**Adjacent chapter connections:**
- Chapter 4: provenance tells where the text corpus came from.
- Chapter 6: filings provide slower, more authoritative contrast to news velocity.

---

## D. Current state of the field

**Settled:**
- Sentiment outputs are corpus-dependent and require sampling/validation.

**Contested or emerging:**
- The predictive value of social and news sentiment varies across market regimes and can decay when widely exploited.

**Key references:**
1. FINRA/SEC/NASAA AI investment fraud warning - manipulated-content risk.
2. Mycroft news/sentiment recipes - local workflow family.
3. Nate Silver, "The Signal and the Noise" - forecasting and noisy signal framing.
4. Bergstrom and West, "Calling Bullshit" - data skepticism teaching frame.
5. NIST AI RMF - monitoring and risk controls.

**Recent developments (last 3 years):**
- Generative AI has made realistic media manipulation cheaper, raising the verification burden for social and news signals.

---

## E. Teaching considerations

**Where students get stuck:**
- They read a sentiment score as a fact rather than an estimate from a sampled corpus.

**Analogies and framings that work:**
- Sentiment is a weather vane, not a map. It tells you which way public language is blowing in a sampled place.

**Exercises that build the target recipe:**
- Design a one-week news/sentiment run with source tiers, duplicate rules, and a 10-item manual verification sample. Bloom's level: Create.

---
