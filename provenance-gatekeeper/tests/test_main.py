import pytest
from app.main import parse_financial_number, evaluate_variance

# --- UNIT TESTS: Regex Normalization ---
def test_parse_financial_number_valid():
    assert parse_financial_number("$5,000,000.00") == 5000000.0
    assert parse_financial_number("5.0M") == 5000000.0
    assert parse_financial_number("exactly 5 million") == 5000000.0
    assert parse_financial_number("10k") == 10000.0
    assert parse_financial_number("-2.5b") == -2500000000.0

def test_parse_financial_number_invalid():
    assert parse_financial_number("null") is None
    assert parse_financial_number("N/A") is None
    assert parse_financial_number("DROP TABLE logs;") is None
    assert parse_financial_number("No financial data present") is None

# --- UNIT TESTS: Evaluation Logic ---
def test_evaluate_variance_passes():
    result = evaluate_variance(claim="$5.0M", ledger_truth="5000000")
    assert result["verdict"] == "PASS"

def test_evaluate_variance_fails_magnitude():
    result = evaluate_variance(claim="4.5M", ledger_truth="5000000")
    assert result["verdict"] == "FAIL"
    assert result["variance_type"] == "Magnitude Error"

def test_evaluate_variance_fails_injection():
    result = evaluate_variance(claim="DROP TABLE logs;", ledger_truth="5000000")
    assert result["verdict"] == "FAIL"
    assert result["variance_type"] == "Data Type Error"