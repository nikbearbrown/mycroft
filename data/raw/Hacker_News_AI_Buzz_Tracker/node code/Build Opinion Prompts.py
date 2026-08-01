# n8n code node: Build Opinion Prompts  (Week 9 — one Groq request body per entity)
# NOTE: response_format is intentionally OMITTED. Groq's json_object validator
# returns HTTP 400 (json_validate_failed) when llama-3.3-70b mis-escapes quote-
# heavy text under constrained decoding — which is what broke every entity. We
# parse leniently downstream (Attach Opinions) instead, and ask for paraphrased
# highlights (not verbatim quotes) to keep the output valid.
SENTIMENTS = ["positive", "negative", "mixed", "neutral"]

def build(_items):
    out = []
    for it in _items:
        j = it["json"]
        lines = [f"{i}. {c}" for i, c in enumerate(j["comments"], 1)]
        block = "\n".join(lines) if lines else "(no comments)"
        system = ("You are a technical-community analyst for an AI-sector attention "
            "tracker. You read verbatim Hacker News comment text about one entity and "
            "summarize the community's OPINION, grounded only in what commenters wrote. "
            "Never invent a fact, quote, or event not present in the comments. Reply "
            "with a single valid JSON object only -- no markdown code fences, no text "
            "before or after the object.")
        user = (f"Entity: {j['entity']} (ticker {j.get('ticker')})\n"
            f"Top-level Hacker News comments on this entity's top stories:\n{block}\n\n"
            'Return a JSON object with exactly these keys: "summary" (2-3 sentences, '
            f'grounded), "sentiment" (one of {SENTIMENTS}), "themes" (<=5 short strings), '
            '"notableOpinions" (<=3 short paraphrased highlights of what commenters said, '
            'each under 120 characters -- do NOT copy punctuation-heavy text verbatim; '
            'paraphrase so the JSON stays valid).')
        body = {"model": "llama-3.3-70b-versatile", "temperature": 0.3, "max_tokens": 1000,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        out.append({"json": {"entity": j["entity"], "row": j["row"], "groqBody": body,
                               "commentsAnalyzed": j["commentsAnalyzed"]}})
    return out


return build(_items)
