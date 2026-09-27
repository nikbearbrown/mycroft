"""
CONFIRMED: HSBC's own language describes engineers using coding assistants,
or "vibe coding assistants," to draft and revise code faster (case study
Section 3.1).

CONSTRUCTED [DEV]: This is a deterministic, canned-response stand-in for a
real coding-assistant/LLM call. No external API, model, or credentials are
used anywhere in this repository. HSBC has not disclosed what tool, model,
or provider underlies its own coding assistants (case study Section 6.1),
so this stub does not attempt to imitate one — it only produces a fixed,
inspectable output so the rest of the pipeline has something to operate on.
"""

from .models import DraftPatch


def draft_patch(report):
    diff = (
        f"--- a/{report.file_path}\n"
        f"+++ b/{report.file_path}\n"
        f"@@ illustrative patch for {report.id} @@\n"
    )
    notes = f"Draft patch generated for vulnerability {report.id}: {report.description}"
    return DraftPatch(vulnerability_id=report.id, diff=diff, assistant_notes=notes)
