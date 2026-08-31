"""
WHAT THIS FILE DOES: Generic spy/mock assertion helpers shared by both
pipelines' test suites. Contains no domain content and describes nothing
about Assistant or Debrief specifically — it is shared INFRASTRUCTURE, not
shared NARRATIVE, per the logged design decision distinguishing the two.
Mock data fixtures (the corpus, the transcripts) remain separate per
pipeline; this file is the one deliberate exception to that separation.
"""

from unittest.mock import MagicMock


def make_spy(return_value=None):
    """Returns a MagicMock configured to return a fixed value, for use in
    monkeypatching a module-level function and later asserting whether it
    was called."""
    spy = MagicMock(return_value=return_value)
    return spy


def assert_never_called(spy: MagicMock, label: str = ""):
    assert not spy.called, f"Expected {label or spy} to never be called, but it was."


def assert_called_once(spy: MagicMock, label: str = ""):
    assert spy.call_count == 1, f"Expected {label or spy} to be called exactly once, got {spy.call_count}."
