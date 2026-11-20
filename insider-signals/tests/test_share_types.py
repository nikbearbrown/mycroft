"""
SHARE TYPES (share_types.py): SECURITY_TITLE → in / out of scope for proposed Rule 10.

What is pinned here:
  - every in-scope type is in: common stock, ordinary shares, LP common units, depositary / ADR
    shares representing common or ordinary shares, shares of beneficial interest;
  - every out-of-scope type is out, with its reason: preferred, depositary for preferred
    (including titles that say only CUMULATIVE / PERPETUAL), notes, debentures, bonds, warrants,
    rights, options, convertible securities, foreign-exchange suffix, unclassifiable;
  - word boundaries: UNITED is not UNITS, CYANOTECH is not NOTE, BONDBLOXX is not BOND;
  - out-of-scope instruments win over COMMON (warrants / rights on common stock, 2330.TW);
  - listed misspellings of COMMON are common; an unlisted one is not;
  - the owner's 2026-11-13 decisions: depositary with unstated underlying and units that are not
    LP common units stay out; SUBORDINATE VOTING SHARES, REGISTERED SHARES and titles ending in
    STOCK are in; fund share classes (Class I, Z, Advisor, A1/A2/A3) stay out; a title naming
    only a company stays unclassifiable;
  - counting: both coverage figures, per quarter, and the Rule 9 mismatch count;
  - no return column is ever read; the CLI halts on an input hash that does not match.

No network. Titles are taken from the study's real SECURITY_TITLE values; counts are synthetic.
"""
from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import share_types as st  # noqa: E402


CASES = {
    # --- in scope ---
    "COMMON STOCK": ("in", "common"),
    "CLASS A COMMON STOCK, PAR VALUE $0.0001 PER SHARE": ("in", "common"),
    '"COMMON STOCK, PAR VALUE $0.001 PER SHARE (""COMMON STOCK"")"': ("in", "common"),
    "  common   stock ": ("in", "common"),
    "RESTRICTED COMMON STOCK": ("in", "common"),
    "UNITED STATES STEEL CORPORATION COMMON STOCK": ("in", "common"),
    "CYANOTECH CORPORATION COMMON STOCK": ("in", "common"),
    "ORDINARY SHARES": ("in", "ordinary"),
    "CLASS A ORDINARY SHARE, PAR VALUE US$0.0001": ("in", "ordinary"),
    "1CLASS A ORDINARY SHARES": ("in", "ordinary"),
    "COMMON UNITS": ("in", "lp_common_units"),
    "COMMON UNITS REPRESENTING LIMITED PARTNER INTERESTS": ("in", "lp_common_units"),
    "SUNOCOCORP COMMON UNITS": ("in", "lp_common_units"),
    "AMERICAN DEPOSITARY SHARES": ("in", "depositary_common"),
    "AMERICAN DEPOSITORY SHARES": ("in", "depositary_common"),
    "ADSS REPRESENTING CLASS B SHARES": ("in", "depositary_common"),
    "ADR": ("in", "depositary_common"),
    "ORDINARY SHARES (REPRESENTED BY AMERICAN DEPOSITARY SHARES)": ("in", "depositary_common"),
    "SHARES OF BENEFICIAL INTEREST": ("in", "beneficial_interest"),
    "CLASS I SHARES OF BENEFICIAL INTEREST": ("in", "beneficial_interest"),
    "COMMON SHARES OF BEN. INTEREST, PAR VALUE $0.01 PER SHARE": ("in", "beneficial_interest"),
    "COMMON SHARES OF BENEFICIAL OWNERSHIP": ("in", "beneficial_interest"),
    # --- misspellings of COMMON ---
    "CAMMON STOCK": ("in", "common"),
    "COMMOM STOCK PAR VALUE $0.01 PER SHARE": ("in", "common"),
    "COMMMON STOCK (CLASS A-3)": ("in", "common"),
    "COMMONSTOCK": ("in", "common"),
    "CMMON STOCK": ("in", "common"),
    "COMON STOCK": ("in", "common"),
    "COMMPN STOCK": ("in", "common"),
    "COMMN STOCK": ("in", "common"),
    "COMMONS STOCK": ("in", "common"),
    "COMMMON": ("in", "common"),
    "COMMUN SHARES": ("out", "share_class_not_named_common"),  # not on the list → not common
    "COMMUN STOCK": ("in", "share_equivalent_named"),  # not common, but ends in STOCK
    # --- out: preferred and depositary for preferred ---
    "SERIES B PREFERRED SHARES": ("out", "preferred"),
    "PREFERENCE SHARES - BBDC4": ("out", "preferred"),
    "6% SERIES A PREFERRED UNITS": ("out", "preferred"),
    "BLUEROCK HOMES TRUST, INC. SERIES A PREF STOCK": ("out", "preferred"),
    "DEPOSITARY SHARES FOR SERIES B PREFERRED STOCK": ("out", "depositary_preferred"),
    "DEP SHARES-INT IN 5.50% SER L NON-CUM PERP PREF STK": ("out", "depositary_preferred"),
    "DEPOSITARY SHARES - 8.375% B CUMULATIVE STOCK": ("out", "depositary_preferred"),
    "DEPOSITORY SHARES-NON-CUMMULATIVE PERPETUAL PREFERRED SER A": ("out", "depositary_preferred"),
    # --- out: debt, warrants, rights, options ---
    "5.65% SERIES WW SENIOR UNSECURED NOTES DUE MAY 22, 2031": ("out", "debt"),
    "CONVERTIBLE SUBORDINATED DEBENTURES": ("out", "debt"),
    "SERIES A BONDS": ("out", "debt"),
    "WARRANTS TO PURCHASE CLASS A COMMON STOCK": ("out", "warrants"),
    "RIGHTS TO ACQUIRE COMMON SHARES": ("out", "rights"),
    "STOCK APPRECIATION RIGHTS (2014)": ("out", "rights"),
    "OPTION (RIGHT TO BUY)": ("out", "options"),
    "STOCK OPTION (RIGHT TO BUY)": ("out", "options"),
    # --- out: foreign-exchange suffix (wins over COMMON) ---
    "COMMON SHARES (2330.TW)": ("out", "foreign_exchange_suffix"),
    # --- out: AI-reading reasons ---
    "DEPOSITARY SHARES": ("out", "depositary_underlying_unstated"),
    "SERIES B DEPOSITARY SHARES": ("out", "depositary_underlying_unstated"),
    "UNITS OF BENEFICIAL INTEREST": ("out", "units_not_lp_common"),
    "COMMON LIMITED LIABILITY COMPANY UNITS": ("out", "units_not_lp_common"),
    "COMMON UNITS OF LIMITED LIABILITY COMPANY INTERESTS": ("out", "units_not_lp_common"),
    "CLASS I LIMITED PARTNERSHIP UNITS": ("out", "units_not_lp_common"),
    "UNIT - SANB11": ("out", "units_not_lp_common"),
    # --- owner decision 2026-11-13 (call 3): named share equivalents in, fund classes out ---
    "SUBORDINATE VOTING SHARES": ("in", "share_equivalent_named"),
    "CLASS A SUBORDINATE VOTING SHARES": ("in", "share_equivalent_named"),
    "REGISTERED SHARES": ("in", "share_equivalent_named"),
    "FIRST FINANCIAL CORP STOCK": ("in", "share_equivalent_named"),
    "CLASS C CAPITAL STOCK": ("in", "share_equivalent_named"),
    "ENB FINANCIAL CORP STOCK.": ("in", "share_equivalent_named"),
    "CONVERTIBLE STOCK": ("out", "convertible"),   # owner 2026-11-13: convertibles are out
    "CONVERTIBLE COMMON STOCK": ("out", "convertible"),
    "SERIES A CONVERTIBLE PREFERRED STOCK": ("out", "preferred"),
    "CLASS B STOCK, $0.01 PAR VALUE": ("out", "share_class_not_named_common"),  # does not end in STOCK
    "SERIES A PREF STOCK": ("out", "preferred"),              # preferred wins over "ends in STOCK"
    "CLASS A SHARES": ("out", "share_class_not_named_common"),
    "CLASS I SHARES": ("out", "share_class_not_named_common"),
    "CLASS Z SHARES": ("out", "share_class_not_named_common"),
    "ADVISOR CLASS SHARES": ("out", "share_class_not_named_common"),
    "CLASS A1 SHARES": ("out", "share_class_not_named_common"),
    "STOCKHOLDER SHARES": ("out", "share_class_not_named_common"),  # STOCK as a word only
    # --- out: unclassifiable ---
    "GIORGIO R. SAUMAT": ("out", "unclassifiable"),
    "JCTC": ("out", "unclassifiable"),
    "CBRE GLOBAL REAL ESTATE INCOME FUND": ("out", "unclassifiable"),
    "BONDBLOXX": ("out", "unclassifiable"),
    "": ("out", "unclassifiable"),
}


class ClassifyTest(unittest.TestCase):
    def test_cases(self):
        for title, expected in CASES.items():
            with self.subTest(title=title):
                self.assertEqual(st.classify(title), expected)

    def test_every_reason_has_a_case(self):
        covered = {reason for _, reason in CASES.values()}
        self.assertEqual(covered, {r for r, _, _ in st.RULES})

    def test_decisions_are_in_or_out(self):
        self.assertEqual({d for _, d, _ in st.RULES}, {"in", "out"})
        self.assertEqual(set(st.OWNER_DECIDED_REASONS) - {r for r, _, _ in st.RULES}, set())


def row(title, quarter="2024q1", status="priced", check="ok"):
    return {"security_title": title, "source_quarter": quarter, "price_status": status,
            "filing_price_check": check}


class CountTest(unittest.TestCase):
    def setUp(self):
        self.s = st.count([
            row("COMMON STOCK"),
            row("COMMON STOCK", status="no_data", check=""),
            row("ORDINARY SHARES", quarter="2024q2"),
            row("SERIES B PREFERRED SHARES", status="price_mismatch_vs_filing", check="mismatch"),
            row("SERIES B PREFERRED SHARES", quarter="2024q2"),
        ])

    def test_totals(self):
        self.assertEqual((self.s["rows"], self.s["in_scope"], self.s["out_of_scope"]), (5, 3, 2))
        self.assertEqual(self.s["by_reason"]["preferred"]["rule9_mismatch"], 1)
        self.assertEqual(self.s["by_reason"]["preferred"]["priced"], 1)

    def test_both_coverage_figures(self):
        c = self.s["coverage"]
        self.assertEqual(c["current_all_buys"], {"priced": 3, "of": 5, "pct": 60.0})
        self.assertEqual(c["rule10_over_all_buys"], {"priced": 2, "of": 5, "pct": 40.0})
        self.assertEqual(c["rule10_over_in_scope"], {"priced": 2, "of": 3, "pct": 66.67})

    def test_by_quarter(self):
        q1, q2 = self.s["by_quarter"]["2024q1"], self.s["by_quarter"]["2024q2"]
        self.assertEqual((q1["buys"], q1["in_scope"], q1["priced_in_scope"]), (3, 2, 1))
        self.assertEqual((q1["pct_over_all_buys"], q1["pct_over_in_scope"]), (33.33, 50.0))
        self.assertEqual((q2["pct_over_all_buys"], q2["pct_over_in_scope"]), (50.0, 100.0))

    def test_examples_capped_at_ten(self):
        s = st.count([row(f"COMMON STOCK CLASS {i}") for i in range(30)])
        self.assertEqual(len(s["by_reason"]["common"]["examples"]), 10)


class NoReturnsTest(unittest.TestCase):
    def test_read_columns_exclude_prices_and_returns(self):
        import enrich
        numeric = {c for c in enrich.ENRICHED_COLUMNS
                   if any(k in c for k in ("return", "entry", "exit", "spy_", "close", "ratio",
                                            "split_factor"))}
        self.assertTrue(numeric)
        self.assertEqual(set(st.READ_COLUMNS) & numeric, set())
        self.assertEqual(set(st.READ_COLUMNS),
                         {"security_title", "source_quarter", "price_status", "filing_price_check"})

    def test_reader_yields_only_read_columns(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "e.csv"
            cols = list(st.READ_COLUMNS) + ["abnormal_return_21d", "entry_price"]
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, cols)
                w.writeheader()
                w.writerow({**row("COMMON STOCK"), "abnormal_return_21d": "0.1", "entry_price": "5"})
            rows = list(st.read_rows(p))
        self.assertEqual(set(rows[0]), set(st.READ_COLUMNS))

    def test_audit_has_no_return_figures(self):
        s = st.count([row("COMMON STOCK")])
        s.update(run_at="t", input="x", input_sha256="h", input_matches_enrich_summary=True)
        text = st.render_audit(s).lower()
        self.assertNotIn("abnormal", text)
        self.assertNotIn("stock_return", text)


class CliTest(unittest.TestCase):
    def _write(self, d, sha=None):
        p = Path(d) / "enriched_buys.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, st.READ_COLUMNS)
            w.writeheader()
            w.writerow(row("COMMON STOCK"))
            w.writerow(row("SERIES B PREFERRED SHARES", status="no_data", check=""))
        summ = Path(d) / "enrich_summary.json"
        summ.write_text(json.dumps({"enriched_buys_sha256": sha or st.sha256(p)}))
        return p, summ

    def test_writes_audit_and_summary(self):
        with tempfile.TemporaryDirectory() as d:
            p, summ = self._write(d)
            out = Path(d) / "out"
            with redirect_stdout(io.StringIO()):
                rc = st.main(["--input", str(p), "--enrich-summary", str(summ), "--out", str(out)])
            self.assertEqual(rc, 0)
            s = json.loads((out / "share_types_summary.json").read_text())
            self.assertEqual(s["rule10_status"], "proposed, not registered")
            self.assertEqual(s["coverage"]["rule10_over_in_scope"]["pct"], 100.0)
            self.assertEqual(s["coverage"]["rule10_over_all_buys"]["pct"], 50.0)
            self.assertIn("Proposal only", (out / "share_types-audit.md").read_text())

    def test_hash_mismatch_halts_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            p, summ = self._write(d, sha="0" * 64)
            out = Path(d) / "out"
            with redirect_stderr(io.StringIO()):
                rc = st.main(["--input", str(p), "--enrich-summary", str(summ), "--out", str(out)])
            self.assertEqual(rc, 1)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
