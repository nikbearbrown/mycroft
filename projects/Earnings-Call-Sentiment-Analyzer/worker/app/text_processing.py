from __future__ import annotations

from dataclasses import dataclass
import re


SECTION_PREPARED = "PREPARED_REMARKS"
SECTION_QA = "Q_AND_A"
SECTION_GUIDANCE = "GUIDANCE"
SECTION_FINANCIAL = "FINANCIAL_RESULTS"
SECTION_UNKNOWN = "UNKNOWN"

SPEAKER_HEADER = re.compile(
    r"^(?P<name>[A-Z][A-Za-z.'’\-]+(?:\s+[A-Z][A-Za-z.'’\-]+){0,4})"
    r"\s*(?:[-–—,|]\s*(?P<title>[^:]{2,100}))?\s*:\s*(?P<body>.*)$"
)
SPEAKER_DASH_HEADER = re.compile(
    r"^(?P<name>[A-Z][A-Za-z.'’\-]+(?:\s+[A-Z][A-Za-z.'’\-]+){0,4})"
    r"\s+[-–—|]\s+(?P<title>[A-Za-z][A-Za-z &/\-]{2,100})$"
)
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")
TIMESTAMP_LINE = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")
TIMESTAMPED_SPEAKER = re.compile(
    r"^(?P<name>Operator|Unknown Analyst|[A-Z][A-Za-z.'’\-]+"
    r"(?:\s+[A-Z][A-Za-z.'’\-]+){1,4})\s+\d{1,2}:\d{2}(?::\d{2})?$"
)
NAME_ONLY = re.compile(
    r"^(?:Operator|Unknown Analyst|[A-Z][A-Za-z.'’\-]+"
    r"(?:\s+[A-Z][A-Za-z.'’\-]+){1,4})$"
)
ROSTER_ENTRY = re.compile(
    r"^(?P<name>[A-Z][A-Za-z.'’\-]+(?:\s+[A-Z][A-Za-z.'’\-]+){1,4})"
    r"\s+(?P<role>executive|analyst)$",
    re.IGNORECASE,
)
TRANSCRIPT_START_MARKERS = {"presentation", "call transcript"}
ANNOUNCED_ANALYST = re.compile(
    r"\b(?:first|next)?\s*question comes from\s+"
    r"(?P<name>[A-Za-z][A-Za-z.'’\-]+(?:\s+[A-Za-z][A-Za-z.'’\-]+){1,3}?)"
    r"(?=\s+(?:with|from|of)\b|[.,]|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedChunk:
    section_name: str
    speaker_name: str | None
    speaker_role: str
    chunk_text: str
    chunk_order: int


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\ue000-\uf8ff]", "", text)
    text = re.sub(r"[\t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_section(line: str, current: str) -> str:
    normalized = re.sub(r"[^a-z0-9&]+", " ", line.lower()).strip()
    normalized = re.sub(r"^(?:section|part)(?: \d+)? ", "", normalized)
    if re.fullmatch(r"(?:questions? (?:and|&) answers?|q\s*(?:and|&)\s*a)(?: session| section)?", normalized):
        return SECTION_QA
    if re.fullmatch(r"(?:prepared|opening|management) remarks(?: section)?", normalized):
        return SECTION_PREPARED
    if re.fullmatch(r"(?:financial (?:results|performance)|quarterly results)(?: section)?", normalized):
        return SECTION_FINANCIAL
    if re.fullmatch(
        r"(?:(?:forward looking )?(?:guidance|outlook)|guidance and outlook|outlook and guidance)(?: section)?",
        normalized,
    ):
        return SECTION_GUIDANCE
    return current


def infer_speaker_role(name: str | None, title: str | None, section: str) -> str:
    value = f"{name or ''} {title or ''}".lower()
    if "operator" in value:
        return "OPERATOR"
    if re.search(r"\b(chief executive officer|ceo|president and ceo)\b", value):
        return "CEO"
    if re.search(r"\b(chief financial officer|cfo|finance chief)\b", value):
        return "CFO"
    if any(term in value for term in ("analyst", "research", "securities", "capital markets", "bank")):
        return "ANALYST"
    if name and section == SECTION_QA and not title:
        return "UNKNOWN"
    if name or title:
        return "OTHER"
    return "UNKNOWN"


def _speaker_from_line(line: str) -> tuple[str, str | None, str] | None:
    match = TIMESTAMPED_SPEAKER.match(line)
    if match:
        name = match.group("name")
        return name, "Operator" if name == "Operator" else None, ""
    match = SPEAKER_HEADER.match(line)
    if match:
        return match.group("name"), match.group("title"), match.group("body").strip()
    match = SPEAKER_DASH_HEADER.match(line)
    if match:
        return match.group("name"), match.group("title"), ""
    if line.lower().rstrip(":") == "operator":
        return "Operator", "Operator", ""
    return None


def _speaker_candidate(line: str) -> str | None:
    candidate = line.lstrip("*• ").strip()
    return candidate if NAME_ONLY.fullmatch(candidate) else None


def _next_nonempty(lines: list[str], start: int, limit: int = 3) -> list[str]:
    values: list[str] = []
    for line in lines[start:]:
        line = line.strip()
        if not line:
            continue
        values.append(line)
        if len(values) == limit:
            break
    return values


def _looks_like_role(line: str) -> bool:
    normalized = line.lower()
    role_terms = (
        "chief executive officer",
        "chief financial officer",
        "ceo",
        "cfo",
        "investor relations",
        "analyst at",
        "equity research",
        "president and",
        "executive vice president",
        "evp and",
    )
    return len(line) <= 140 and any(term in normalized for term in role_terms)


def _build_speaker_directory(lines: list[str], text: str) -> dict[str, str | None]:
    directory: dict[str, str | None] = {
        "Operator": "Operator",
        "Unknown Analyst": "Analyst",
    }

    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        roster_match = ROSTER_ENTRY.fullmatch(line)
        if roster_match:
            role = "Analyst" if roster_match.group("role").lower() == "analyst" else "Executive"
            directory[roster_match.group("name")] = role

        structured = _speaker_from_line(line)
        if structured:
            name, title, _body = structured
            directory[name] = title or directory.get(name)
            following = _next_nonempty(lines, index + 1)
            if not title and following and _looks_like_role(following[0]):
                directory[name] = following[0]

        candidate = _speaker_candidate(line)
        if not candidate:
            continue
        following = _next_nonempty(lines, index + 1)
        timestamp_index = next(
            (position for position, value in enumerate(following) if TIMESTAMP_LINE.fullmatch(value)),
            None,
        )
        if timestamp_index is not None:
            title_lines = following[:timestamp_index]
            directory[candidate] = " ".join(title_lines) if title_lines else directory.get(candidate)

    compact_text = re.sub(r"\s+", " ", text)
    title_patterns = (
        ("chief executive officer", "Chief Executive Officer"),
        ("president and ceo", "President and CEO"),
        ("chief financial officer", "Chief Financial Officer"),
        ("evp and cfo", "EVP and CFO"),
        ("investor relations", "Investor Relations"),
    )
    for name, existing_title in list(directory.items()):
        if existing_title not in (None, "Executive"):
            continue
        surname = name.split()[-1]
        best_title: str | None = None
        best_distance: int | None = None
        for match in re.finditer(rf"\b{re.escape(surname)}\b", compact_text, re.IGNORECASE):
            context = compact_text[match.end() : match.end() + 180].lower()
            for phrase, title in title_patterns:
                distance = context.find(phrase)
                if distance >= 0 and (best_distance is None or distance < best_distance):
                    best_title = title
                    best_distance = distance
        if best_title:
            directory[name] = best_title

    return directory


def _spoken_section_transition(line: str, current: str) -> str:
    normalized = re.sub(r"\s+", " ", line.lower())
    qa_phrases = (
        "we will now begin the question-and-answer session",
        "we will now begin the question and answer session",
        "we will now open the call to questions",
        "please open the line for questions",
        "we will now take questions",
    )
    return SECTION_QA if any(phrase in normalized for phrase in qa_phrases) else current


def _announced_analyst(line: str) -> str | None:
    match = ANNOUNCED_ANALYST.search(line)
    if not match:
        return None
    return " ".join(
        word[:1].upper() + word[1:] if word.islower() else word
        for word in match.group("name").split()
    )


def _split_sentences(paragraph: str) -> list[str]:
    sentences = [part.strip() for part in SENTENCE_BOUNDARY.split(paragraph) if part.strip()]
    expanded: list[str] = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) <= 180:
            expanded.append(sentence)
            continue
        for start in range(0, len(words), 180):
            expanded.append(" ".join(words[start : start + 180]))
    return expanded


def _chunk_paragraph(paragraph: str) -> list[str]:
    sentences = _split_sentences(paragraph)
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for sentence in sentences:
        if current and (len(current) == 3 or current_length + len(sentence) > 1200):
            chunks.append(" ".join(current))
            current = []
            current_length = 0
        current.append(sentence)
        current_length += len(sentence) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks


def parse_transcript(raw_text: str) -> list[ParsedChunk]:
    text = clean_text(raw_text)
    lines = text.split("\n")
    speaker_directory = _build_speaker_directory(lines, text)
    has_start_marker = any(
        re.sub(r"[^a-z]+", " ", line.lower()).strip() in TRANSCRIPT_START_MARKERS
        for line in lines
    )
    in_transcript = not has_start_marker
    section = SECTION_UNKNOWN
    speaker_name: str | None = None
    speaker_title: str | None = None
    announced_analyst_name: str | None = None
    paragraph_lines: list[str] = []
    parsed: list[tuple[str, str | None, str, str]] = []

    def flush() -> None:
        if not paragraph_lines:
            return
        paragraph = " ".join(paragraph_lines).strip()
        paragraph_lines.clear()
        if not paragraph:
            return
        role = infer_speaker_role(speaker_name, speaker_title, section)
        for chunk_text in _chunk_paragraph(paragraph):
            parsed.append((section, speaker_name, role, chunk_text))

    for line in lines:
        line = line.strip()
        if not line:
            flush()
            continue

        normalized_line = re.sub(r"[^a-z]+", " ", line.lower()).strip()
        if normalized_line in TRANSCRIPT_START_MARKERS:
            flush()
            in_transcript = True
            section = SECTION_PREPARED
            speaker_name = None
            speaker_title = None
            continue
        if not in_transcript:
            continue
        if normalized_line == "participants":
            flush()
            break
        if normalized_line in {"skip to participants", "read less", "executives", "analysts"} or line in {"*", "* "}:
            continue

        next_section = detect_section(line, section)
        if next_section != section:
            flush()
            section = next_section
            continue

        speaker = _speaker_from_line(line)
        if speaker:
            flush()
            speaker_name, speaker_title, body = speaker
            speaker_title = speaker_title or speaker_directory.get(speaker_name)
            if body:
                paragraph_lines.append(body)
            continue


        candidate = _speaker_candidate(line)
        if candidate and candidate in speaker_directory:
            flush()
            if candidate == "Unknown Analyst" and announced_analyst_name:
                speaker_name = announced_analyst_name
                speaker_title = "Analyst"
                speaker_directory[speaker_name] = speaker_title
            else:
                speaker_name = candidate
                speaker_title = speaker_directory[candidate]
            continue

        if TIMESTAMP_LINE.fullmatch(line):
            continue

        if speaker_name and not paragraph_lines and _looks_like_role(line):
            speaker_title = line
            speaker_directory[speaker_name] = line
            continue

        spoken_section = _spoken_section_transition(line, section)
        if spoken_section != section:
            flush()
            section = spoken_section

        announced_analyst = _announced_analyst(line)
        if announced_analyst:
            announced_analyst_name = announced_analyst
            speaker_directory[announced_analyst_name] = "Analyst"

        paragraph_lines.append(line)

    flush()
    return [
        ParsedChunk(section_name, name, role, chunk_text, index)
        for index, (section_name, name, role, chunk_text) in enumerate(parsed)
    ]
