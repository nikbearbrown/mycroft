"""
CONFIRMED: HSBC's own language describes engineers using coding assistants to
identify and patch vulnerabilities faster (case study Section 3.1).

CONSTRUCTED [DEV]: HSBC does not disclose what fields a vulnerability report
must contain, what triggers the initial flag, or any validation logic. This
function requires only the minimal fields needed for the rest of this
illustrative pipeline to run. An implementer connecting this to a real
scanner should replace this with whatever schema that scanner actually
emits — this is a customization point, not a documented HSBC mechanism.
"""


def validate_vulnerability_report(report):
    if not report.id or not report.file_path or not report.description:
        raise ValueError("incomplete_vulnerability_report")
    return report
