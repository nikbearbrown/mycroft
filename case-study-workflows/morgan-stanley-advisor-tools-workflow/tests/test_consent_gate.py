import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from debrief.consent_gate import check_consent


def test_consent_true_clears():
    result = check_consent(True)
    assert result.cleared is True


def test_consent_false_does_not_clear():
    result = check_consent(False)
    assert result.cleared is False


def test_consent_none_does_not_clear():
    result = check_consent(None)
    assert result.cleared is False


if __name__ == "__main__":
    test_consent_true_clears()
    test_consent_false_does_not_clear()
    test_consent_none_does_not_clear()
    print("test_consent_gate.py: all tests passed")
