"""
CONFIRMED: HSBC reports a 60% speed-up in unit testing and 5x faster
vulnerability patching, attributed to the coding-assistant rollout (case
study Sections 3.1/5.1).

CONSTRUCTED: This module does not attempt to reproduce those timing
figures — no real timing benchmark, code execution, or test framework runs
anywhere in this repository. It only confirms, structurally, that applying
a patch and running tests happens strictly after Gate approval, never
before — the fail-fast property this pipeline's tests verify directly.
"""


def apply_patch_and_test(draft_patch):
    return {
        "applied": True,
        "vulnerability_id": draft_patch.vulnerability_id,
        "tests_run": True,
        "tests_passed": True,
    }
