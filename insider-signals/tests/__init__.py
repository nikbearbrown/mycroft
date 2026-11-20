"""
Tests for insider-signals. Same conventions as verification-layer/tests/:

  - stdlib `unittest` only: no pytest, no network, no live model;
  - small trimmed fixtures in tests/fixtures/ (e.g. a few rows of a real quarter's
    SUBMISSION / REPORTINGOWNER / NONDERIV_TRANS, with their source accession numbers);
  - each test file opens with a docstring saying what it pins and why.

Run from insider-signals/:  python -m unittest discover -s tests
"""
