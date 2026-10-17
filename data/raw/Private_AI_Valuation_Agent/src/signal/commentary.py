"""Quarterly commentary: the only prose an LLM writes in this project.

`plan.md`: "Prompt grounded strictly in computed numbers, with an explicit
instruction to state when coverage is thin rather than filling the gap." And:
"**Quarterly commentary** (LLM): labeled commentary, never a verified claim."

The model is handed a JSON block of already-computed figures and asked to
write about them. It is given no database access, no tools and no retrieval,
so there is no path by which it can introduce a number. Anything numeric in
its output that is not in the block it was given is a fabrication, and
`check_grounding` finds it.

--------------------------------------------------------------------------
Three backends, in order
--------------------------------------------------------------------------
    groq      plan.md's choice: llama-3.3-70b-versatile, free tier.
    ollama    a local 8B fallback. plan.md rejected local models for
              commentary on quality ("weaker prose"), not on correctness, so
              it is usable as a fallback and the signal records which model
              wrote the text.
    none      no backend reachable. The commentary is **refused**, with the
              reason recorded, and the signal is emitted without it.

The third is the important one. A quarterly note is the one artifact here
where an absent model could be papered over with a template, and a templated
paragraph that reads like analysis is worse than no paragraph: it would be
indistinguishable from model output in the signal, while carrying
`is_model_output: true`. So there is no template. Absent a model, the
`commentary` key says `refused` and says why.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Loaded here rather than relying on another module having done it. An
# earlier version read GROQ_API_KEY straight from os.environ and worked
# only because src.db.connect happened to be imported first.
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:  # noqa: BLE001 -- a missing .env is not an error here
    pass

# Preference order, not a single name. `plan.md` specifies
# `llama-3.3-70b-versatile`, and Groq has since retired it -- a run with a
# valid key failed with HTTP 404 "model does not exist or you do not have
# access to it". Hosted model names are not stable, so pinning one makes a
# vendor's deprecation schedule into an outage here.
#
# The list is ordered by capability for this task, which is prose over a table
# of figures. `GROQ_MODEL` overrides it outright. The chosen model is recorded
# in the signal's `commentary.model`, so a substitution is visible rather than
# silent.
GROQ_MODELS = (
    "llama-3.3-70b-versatile",   # plan.md's choice, kept first
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
)
OLLAMA_MODEL_DEFAULT = "llama3.1:8b"
MAX_WORDS = 320
MAX_ATTEMPTS = 3
# An empty note passes every content check trivially -- nothing to
# fabricate, nothing to rank, no placeholder -- and was accepted as a
# success once, reported as "0 words". Length is the fourth check.
MIN_WORDS = 60

SYSTEM_PROMPT = """\
You write one short quarterly note for a desk that tracks private company \
valuations derived from SEC fund filings.

You are given a JSON block of figures that have already been computed. These \
are the ONLY facts available to you.

Rules, in order of importance:

1. Use no number that is not in the JSON block. Do not estimate, round \
differently, annualise, extrapolate, or compute a new figure from two given \
ones. If a number you want is not there, say it is not available.
2. Where coverage is thin, say so plainly. Do not fill a gap with a general \
statement about the sector or about these companies. "Only two managers \
priced this company, which is too few to characterise" is a good sentence. \
Writing around the gap is not.
3. Never state or imply a company valuation or market capitalisation. The \
underlying data gives a fund's share count, never the company's shares \
outstanding, so no company-level value exists in it.
4. Never call anything verified. You are commentary; a human marks claims \
verified, citing a source.
5. Do NOT rank the companies. No "the highest", "the lowest", "the most", \
"the fewest", "the largest". Comparing ten rows across six fields is \
error-prone, and a wrong ranking reads exactly like a right one. Describe \
individual figures instead.
6. Never write the word null, or any other placeholder, into the prose. Where \
a figure is absent, say it is not available.
7. Describe what the figures show, not what it means for the sector, and not \
what anyone should do about it. No investment advice.
8. Write figures as digits, not words. "61 groups", never "sixty-one groups".
9. Two field names mean something specific, and misreading them is the most \
common error on this data. `median_days_to_half` is the number of days taken \
for HALF THE MANAGERS WHO EVENTUALLY ADOPTED a price level to have reported \
it. It is not a price halving, not a decay, not a half-life. `remark_rate` is \
the share of consecutive observations where the price CHANGED.

Write at most %d words of plain prose. No headings, no bullet points, no \
preamble, no sign-off.""" % MAX_WORDS


class CommentaryRefused(RuntimeError):
    """No backend was reachable, so no commentary was written."""


# --------------------------------------------------------------------------
# Backends
# --------------------------------------------------------------------------


def groq_model(timeout: int = 30) -> str:
    """The best model from GROQ_MODELS this account can actually reach.

    Resolved against the live `/models` list rather than assumed, because the
    alternative is what happened: a valid key, a retired model name, and a
    404 that reads like a credentials problem.

    `GROQ_MODEL` short-circuits this for a deliberate pin. If nothing in the
    preference list is available the first chat-capable model is returned, so
    the failure is "the prose is from a model you did not choose" -- visible
    in the signal -- rather than an outage.
    """
    import requests

    override = os.getenv("GROQ_MODEL")
    if override:
        return override

    response = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        timeout=timeout)
    response.raise_for_status()
    available = {m["id"] for m in response.json().get("data", [])}

    for candidate in GROQ_MODELS:
        if candidate in available:
            return candidate

    # Nothing preferred is reachable. Exclude the model families that cannot
    # write prose at all -- speech, and the prompt-safety classifiers --
    # rather than sending a quarterly note to Whisper.
    unusable = ("whisper", "orpheus", "prompt-guard", "tts", "guard")
    usable = sorted(m for m in available
                    if not any(bad in m.lower() for bad in unusable))
    if not usable:
        raise RuntimeError(
            "no chat-capable Groq model is available to this key. Available: "
            + ", ".join(sorted(available)))
    return usable[0]


def _groq(prompt: str, model: str | None = None, timeout: int = 60) -> str:
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"], timeout=timeout)
    reply = client.chat.completions.create(
        model=model or groq_model(),
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0.2,
        # Generous, because the reasoning models on Groq's current roster
        # spend this budget on a hidden channel before emitting any prose.
        # At 700 the real prompt returned an EMPTY note with
        # finish_reason="length": all of it went to reasoning.
        max_tokens=4000,
    )
    choice = reply.choices[0]
    text = (choice.message.content or "").strip()
    if not text:
        raise RuntimeError(
            f"the model returned no content (finish_reason="
            f"{choice.finish_reason!r}). On a reasoning model this usually "
            "means max_tokens was consumed before any prose was emitted.")
    return text


def _ollama(prompt: str, model: str | None = None, timeout: int = 180) -> str:
    import requests

    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    model = model or os.getenv("OLLAMA_MODEL", OLLAMA_MODEL_DEFAULT)
    response = requests.post(
        f"{host}/api/chat", timeout=timeout,
        json={"model": model, "stream": False,
              "options": {"temperature": 0.2},
              "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                           {"role": "user", "content": prompt}]})
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


def available_backends() -> list[str]:
    """Which backends could actually be called right now."""
    import requests

    found = []
    if os.getenv("GROQ_API_KEY"):
        found.append("groq")
    try:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        if requests.get(f"{host}/api/tags", timeout=3).status_code == 200:
            found.append("ollama")
    except Exception:                              # noqa: BLE001
        pass
    return found


# --------------------------------------------------------------------------
# Grounding
# --------------------------------------------------------------------------

_NUMBER = re.compile(r"-?\d[\d,]*\.?\d*")

# Number-words, because the check was blind to them. A Groq run wrote
# "Dispersion is measured across sixty-one groups" -- which happened to be
# correct, and would have passed identically if it had been wrong, since
# `_NUMBER` only sees digits. A model told to quote the figures it was given
# will sometimes spell them, and an unchecked figure is the whole problem.
_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
         "seventy": 70, "eighty": 80, "ninety": 90}
_WORD_NUMBER = re.compile(
    r"\b(" + "|".join(list(_TENS) + list(_UNITS)) + r")"
    r"(?:[\s‐-―-]+(" + "|".join(_UNITS) + r"))?\b", re.I)


def words_to_numbers(text: str) -> set[str]:
    """Figures a writer spelled out, as digit strings.

    Covers what a model actually writes on this data -- units, teens, tens and
    hyphenated compounds up to ninety-nine. Not a general English-number
    parser, and deliberately not: "one of the two" must not register as a
    claim, which is why a unit word followed by another unit word is skipped.
    """
    found = set()
    for tens, unit in _WORD_NUMBER.findall(text or ""):
        tens, unit = tens.lower(), (unit or "").lower()
        if tens in _TENS:
            found.add(str(_TENS[tens] + (_UNITS.get(unit, 0) if unit else 0)))
        elif not unit:
            found.add(str(_UNITS[tens]))
    return found

# Numbers a writer may use without them appearing in the facts: small counts
# and ordinals that belong to English rather than to the data ("one of the
# two", "a third manager"). Anything above this has to be grounded.
_FREE_SMALL_INTEGERS = set(range(0, 13))


def _numbers_in(text: str) -> set[str]:
    out = words_to_numbers(text)
    for raw in _NUMBER.findall(text or ""):
        cleaned = raw.replace(",", "").rstrip(".")
        if not cleaned or cleaned in {"-", "."}:
            continue
        out.add(cleaned)
    return out


def _numbers_in_facts(facts) -> set[str]:
    """Every number a model could legitimately quote, in several renderings.

    A model given 0.108 will write "10.8%", and given 259.1364 may write
    "259.14". Both are faithful. So each fact contributes its raw form plus
    the renderings a careful writer would produce; anything outside that set
    is a number the model made up.
    """
    out: set[str] = set()

    def add(value):
        if isinstance(value, bool) or value is None:
            return
        if isinstance(value, (int, float)):
            number = float(value)
            out.add(f"{number:g}")
            out.add(f"{number:.0f}")
            out.add(f"{number:.1f}")
            out.add(f"{number:.2f}")
            out.add(f"{number:.4f}".rstrip("0").rstrip("."))
            if abs(number) <= 1.0:                  # a rate, written as a %
                for digits in (0, 1, 2):
                    out.add(f"{number * 100:.{digits}f}")
            out.add(f"{int(number)}" if float(number).is_integer() else "")
        elif isinstance(value, str):
            out.update(_numbers_in(value))

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        else:
            add(node)

    walk(facts)
    out.discard("")
    return out


# "Databricks has the highest dispersion, with a maximum spread of 1.1186."
# A superlative plus a figure: the one comparative shape a model reliably
# produces and unreliably gets right.
# The explicit decimal group and the trailing guard matter: an earlier version
# captured "30." out of "30. The next" and "80," out of "80,2", and reported
# both as failed rankings. A check that cries wolf gets switched off.
_SUPERLATIVE = re.compile(
    r"\b(highest|lowest|most|fewest|largest|smallest|greatest|biggest)\b"
    r"[^;]{0,120}?(?<![\d.])(-?\d[\d,]*(?:\.\d+)?)(?!\d)(?!\.\d)", re.I)

_MAXIMISING = {"highest", "most", "largest", "greatest", "biggest"}

# Serialiser placeholders. A model shown `"median_spread": null` will happily
# write "a median spread of null", which describes an absent figure as if it
# were a value. Word-bounded so "nullify" and "annulment" are not hits.
_PLACEHOLDER = re.compile(r"\bnull\b|\bNaN\b|\bundefined\b|\bNone\b")


def _extreme_values(facts) -> tuple[set[str], set[str]]:
    """Per-field maxima and minima across the per-company rows.

    Rendered as strings the same way `_numbers_in_facts` renders them, so a
    model writing "0.9779" or "97.8%" is compared against the same value.
    """
    companies = (facts or {}).get("companies") or []
    fields: dict[str, list[float]] = {}

    def collect(prefix: str, node):
        if isinstance(node, dict):
            for key, value in node.items():
                collect(f"{prefix}.{key}", value)
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            fields.setdefault(prefix, []).append(float(node))

    for row in companies:
        collect("", row)

    def render(number: float) -> set[str]:
        out = {f"{number:g}", f"{number:.0f}", f"{number:.1f}", f"{number:.2f}",
               f"{number:.4f}".rstrip("0").rstrip(".")}
        if abs(number) <= 1.0:
            out |= {f"{number * 100:.{d}f}" for d in (0, 1, 2)}
        return out

    maxima: set[str] = set()
    minima: set[str] = set()
    for values in fields.values():
        if len(values) < 2:
            continue
        maxima |= render(max(values))
        minima |= render(min(values))
    return maxima, minima


def check_superlatives(text: str, facts) -> list[str]:
    """Superlative claims whose figure is not actually the extreme. Empty is good.

    This exists because of what the first real run produced. Grounding passed
    -- every number was one the model had been given -- and the prose still
    said "Anduril has the lowest number of marks, at 509" one sentence before
    saying "Figure AI has the lowest number of marks, at 31". Both numbers
    were real; the ranking was invented.

    An 8B model cannot reliably rank ten rows across six fields, which is why
    `plan.md` chose a 70B model for commentary. A check is better than a
    bigger model promise: it fails the same way on any model.

    What it cannot catch is a wrong comparative with no number attached, or a
    wrong gloss on a term. Those remain the human gate's job, and the note
    says every figure in it is model output rather than a verified claim.
    """
    maxima, minima = _extreme_values(facts)
    if not maxima and not minima:
        return []

    bad = []
    for word, raw in _SUPERLATIVE.findall(text or ""):
        token = raw.replace(",", "").rstrip(".")
        try:
            number = float(token)
        except ValueError:
            continue
        if number.is_integer() and int(number) in _FREE_SMALL_INTEGERS:
            continue
        wanted = maxima if word.lower() in _MAXIMISING else minima
        if token not in wanted and f"{number:g}" not in wanted:
            bad.append(f"{word} … {raw}")
    return sorted(set(bad))


def check_grounding(text: str, facts) -> list[str]:
    """Numbers in the prose that are not in the facts. Empty is good.

    This is the check that makes "the model never touches a number" testable
    rather than aspirational. It cannot catch a false *claim* in words -- that
    is what the human gate is for -- but a fabricated figure is exactly the
    failure mode of a model asked to write about data, and it is mechanical.
    """
    allowed = _numbers_in_facts(facts)
    ungrounded = []
    for token in _numbers_in(text):
        if token in allowed:
            continue
        try:
            number = float(token)
        except ValueError:
            continue
        if number.is_integer() and int(number) in _FREE_SMALL_INTEGERS:
            continue
        if f"{number:g}" in allowed or f"{number:.1f}" in allowed:
            continue
        ungrounded.append(token)
    return sorted(set(ungrounded))


# --------------------------------------------------------------------------
# The call
# --------------------------------------------------------------------------


def build_prompt(facts: dict) -> str:
    return (
        "Here are the computed figures for this quarter. Write the note.\n\n"
        "```json\n"
        + json.dumps(facts, indent=2, default=str)
        + "\n```\n"
    )


def write_commentary(facts: dict, *, backend: str | None = None,
                     call=None) -> dict:
    """Produce the `commentary` object for the signal, or refuse.

    `call` is an injection point for tests: a callable taking the prompt and
    returning text. Without it, the first available backend is used.

    The returned object always carries `is_model_output: true`, even when
    refused, because the key's meaning must not depend on whether a model
    happened to be reachable.
    """
    stamp = datetime.now(timezone.utc).isoformat(
        timespec="seconds").replace("+00:00", "Z")
    grounded_in = sorted(facts.keys()) if isinstance(facts, dict) else []

    if call is not None:
        model = backend or "injected"
    else:
        backends = available_backends()
        model = backend or (backends[0] if backends else None)
        # Record the resolved model id, not the backend name. "groq" does not
        # say which model wrote the prose, and the point of resolving one from
        # the live list is that a substitution stays visible in the signal.
        if model == "groq":
            try:
                chosen = groq_model()
            except Exception as exc:                     # noqa: BLE001
                return {
                    "text": "", "is_model_output": True, "model": "groq",
                    "generated_at": stamp, "grounded_in": grounded_in,
                    "refused": True,
                    "refusal_reason": f"could not resolve a Groq model: "
                                      f"{type(exc).__name__}: {exc}",
                }
            model = f"groq/{chosen}"
            call = lambda prompt: _groq(prompt, chosen)  # noqa: E731
        elif model == "ollama":
            chosen = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL_DEFAULT)
            model = f"ollama/{chosen}"
            call = lambda prompt: _ollama(prompt, chosen)  # noqa: E731
        else:
            return {
                "text": "",
                "is_model_output": True,
                "model": None,
                "generated_at": stamp,
                "grounded_in": grounded_in,
                "refused": True,
                "refusal_reason": (
                    "no commentary backend was reachable. GROQ_API_KEY is "
                    "unset and no Ollama server answered. No template was "
                    "substituted: a templated paragraph carrying "
                    "is_model_output would be indistinguishable from model "
                    "output while not being any."),
            }

    def refuse(reason: str, attempts: int = 1) -> dict:
        return {"text": "", "is_model_output": True, "model": model,
                "generated_at": stamp, "grounded_in": grounded_in,
                "refused": True,
                "refusal_reason": f"{reason} (after {attempts} attempt"
                                  f"{'s' if attempts > 1 else ''})"}

    # A bounded retry that hands the model its own failure. The checks below
    # produce a specific, mechanical complaint -- "0.9779 is not the highest
    # value of any field" -- which is exactly the kind of correction a model
    # can act on. Unbounded retries would be a way to keep rolling until the
    # checks happen to pass, so three is the limit and a fourth failure is a
    # refusal.
    prompt, problem, text = build_prompt(facts), None, ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            retry = (prompt if problem is None else
                     f"{prompt}\n\nYour previous draft was rejected: "
                     f"{problem}\n\nWrite it again, fixing that.")
            text = call(retry)
        except Exception as exc:                   # noqa: BLE001
            return refuse(f"{type(exc).__name__}: {exc}", attempt)

        ungrounded = check_grounding(text, facts)
        if ungrounded:
            problem = ("you used numbers that are not in the figures you were "
                       f"given: {', '.join(ungrounded)}")
            continue
        wrong_rankings = check_superlatives(text, facts)
        if wrong_rankings:
            problem = ("you claimed a superlative whose figure is not the "
                       f"extreme value of any field: {'; '.join(wrong_rankings)}"
                       ". Do not rank the companies at all")
            continue
        if _PLACEHOLDER.search(text):
            problem = ("you wrote a placeholder such as 'null' into the prose, "
                       "describing an absent figure as a value")
            continue
        # Length last. A draft that is both short and wrong should hear
        # about the wrong part, which is the actionable one -- an
        # earlier order told a model its 6-word draft was too short
        # while saying nothing about the fabricated figure in it.
        if len(text.split()) < MIN_WORDS:
            problem = (f"your draft was {len(text.split())} words; the note "
                       f"needs at least {MIN_WORDS}")
            continue
        return {"text": text, "is_model_output": True, "model": model,
                "generated_at": stamp, "grounded_in": grounded_in,
                "refused": False, "refusal_reason": None}

    return refuse(f"every draft failed its checks: {problem}", MAX_ATTEMPTS)

