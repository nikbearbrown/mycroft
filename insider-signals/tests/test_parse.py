"""
PARSE (parse.py): the buy filter, transaction-code classification, normalization, and flags.

What is pinned here:
  - every Form 4 / 4-A row gets exactly one class, and qualifying buys + exclusions add up to
    the Form 4 row count; other forms (here a Form 5) are counted but not output;
  - the buy filter: code P, acquired (A), shares > 0, price > 0, no equity swap. Each failure
    gets its own reason, in the documented order; derivative-table P rows are context only;
  - AFF10B5ONE: 1/true → plan, 0/false → no_plan, blank and unrecognized → unknown, and a
    footnote mentioning 10b5-1 never changes that;
  - RPTOWNER_RELATIONSHIP splits on commas, case-insensitively; unknown tokens are reported;
  - a joint filing stays one row per transaction, with all owners attached;
  - private-placement and ESPP footnotes flag a buy but never exclude it;
  - the downloaded header is authoritative: missing required columns halt, reordered or extra
    columns are fine, and a missing AFF10B5ONE column makes every buy "unknown";
  - provenance: an extracted folder that does not match manifest.json halts;
  - outputs: CSV, summary JSON and audit are written; the audit names no reporting owner.

No network. The fixture (tests/fixtures/parse_sample/) is synthetic rows under the real
2026 Q3 headers; see tests/fixtures/README.md.
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ingest  # noqa: E402
import parse  # noqa: E402

SAMPLE = Path(__file__).resolve().parent / "fixtures" / "parse_sample"


def by_sk(rows):
    return {r["nonderiv_trans_sk"]: r for r in rows}


class TestHelpers(unittest.TestCase):
    def test_aff10b5one(self):
        for raw, want in [("1", "plan"), ("true", "plan"), ("TRUE", "plan"), (" 1 ", "plan"),
                          ("0", "no_plan"), ("false", "no_plan"),
                          ("", "unknown"), (None, "unknown"), ("weird", "unknown")]:
            self.assertEqual(parse.norm_aff10b5one(raw), want, raw)

    def test_relationship_split(self):
        self.assertEqual(parse.split_relationship("Director,Officer"), (["director", "officer"], []))
        self.assertEqual(parse.split_relationship("TenPercentOwner"), (["ten_percent_owner"], []))
        self.assertEqual(parse.split_relationship(" DIRECTOR , other "), (["director", "other"], []))
        self.assertEqual(parse.split_relationship("Officer, Trustee"), (["officer"], ["Trustee"]))
        self.assertEqual(parse.split_relationship(""), ([], []))
        self.assertEqual(parse.split_relationship("Director,director"), (["director"], []))

    def test_iso_date(self):
        self.assertEqual(parse.iso_date("05-AUG-2026"), "2026-08-05")
        self.assertEqual(parse.iso_date("5-Aug-2026"), "2026-08-05")
        self.assertEqual(parse.iso_date(""), "")
        self.assertEqual(parse.iso_date("2026-08-05"), "")

    def test_footnote_ids(self):
        row = {"A_FN": "F2, F3", "B_FN": "F3", "C_FN": ""}
        self.assertEqual(parse.footnote_ids(row, ["A_FN", "B_FN", "C_FN"]), ["F2", "F3"])

    def base(self, **kw):
        row = {"TRANS_CODE": "P", "TRANS_ACQUIRED_DISP_CD": "A", "TRANS_SHARES": "10",
               "TRANS_PRICEPERSHARE": "1.5", "EQUITY_SWAP_INVOLVED": "0"}
        row.update(kw)
        return row

    def test_classify_order(self):
        self.assertEqual(parse.classify(self.base()), parse.QUALIFYING)
        self.assertEqual(parse.classify(self.base(TRANS_CODE="")), "code_missing")
        self.assertEqual(parse.classify(self.base(TRANS_CODE="K")), "code_unrecognized")
        self.assertEqual(parse.classify(self.base(TRANS_CODE="F")), "code_F_tax_or_exercise_payment")
        self.assertEqual(parse.classify(self.base(TRANS_CODE="p")), parse.QUALIFYING)
        self.assertEqual(parse.classify(self.base(TRANS_ACQUIRED_DISP_CD="D")), "p_not_acquired")
        # a row failing several checks gets the first one
        self.assertEqual(parse.classify(self.base(TRANS_ACQUIRED_DISP_CD="D", TRANS_SHARES="0")),
                         "p_not_acquired")
        for bad in ("0", "-5", "", "abc", "NaN"):
            self.assertEqual(parse.classify(self.base(TRANS_SHARES=bad)),
                             "p_shares_missing_or_not_positive", bad)
            self.assertEqual(parse.classify(self.base(TRANS_PRICEPERSHARE=bad)),
                             "p_price_missing_or_not_positive", bad)
        for swap in ("1", "true"):
            self.assertEqual(parse.classify(self.base(EQUITY_SWAP_INVOLVED=swap)), "p_equity_swap")
        for no_swap in ("0", "false", ""):
            self.assertEqual(parse.classify(self.base(EQUITY_SWAP_INVOLVED=no_swap)), parse.QUALIFYING)

    def test_every_sec_code_has_a_reason(self):
        for code in parse.TRANS_CODES:
            reason = parse.classify(self.base(TRANS_CODE=code))
            self.assertTrue(reason == parse.QUALIFYING or reason in parse.REASONS, code)

    def test_flags(self):
        self.assertEqual(parse.match_flags(["Bought in the company's IPO."]), (["IPO"], []))
        self.assertEqual(parse.match_flags(["Acquired under the ESPP."]), ([], ["ESPP"]))
        self.assertEqual(parse.match_flags(["Weighted average price."]), ([], []))
        self.assertEqual(parse.match_flags(["Purchased from the Company in a private placement"]),
                         (["private placement", "from the issuer"], []))


class TestParseSample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.summary = parse.parse_folder(SAMPLE, "2026q3")
        cls.rows_by_sk = by_sk(cls.rows)

    def test_funnel(self):
        self.assertEqual(self.summary["funnel"], {"nonderiv_rows_total": 17, "form4_rows": 16,
                                                  "form4_code_p_rows": 11, "qualifying_buys": 6})
        self.assertEqual(self.summary["nonderiv_rows_by_document_type"], {"4": 13, "4/A": 3, "5": 1})

    def test_every_row_accounted_for(self):
        s = self.summary
        self.assertEqual(s["funnel"]["qualifying_buys"] + sum(s["exclusions_by_reason"].values()),
                         s["funnel"]["form4_rows"])
        self.assertEqual(len(self.rows), s["funnel"]["form4_rows"])
        self.assertNotIn("9", self.rows_by_sk)              # the Form 5 row is not output

    def test_exclusions_by_reason(self):
        self.assertEqual(self.summary["exclusions_by_reason"], {
            "code_missing": 1, "code_unrecognized": 1,
            "code_A_grant_award": 1, "code_M_option_exercise_16b3": 1, "code_S_sale": 1,
            "p_not_acquired": 1, "p_shares_missing_or_not_positive": 2,
            "p_price_missing_or_not_positive": 1, "p_equity_swap": 1,
        })

    def test_qualifying_rows(self):
        q = sorted(sk for sk, r in self.rows_by_sk.items() if r["buy_class"] == parse.QUALIFYING)
        self.assertEqual(q, sorted(["1", "3", "7", "11", "14", "17"]))
        self.assertEqual(self.rows_by_sk["1"]["value_usd"], "1050.0")
        self.assertEqual(self.rows_by_sk["2"]["value_usd"], "")   # only buys get a value

    def test_10b5_1(self):
        self.assertEqual(self.summary["qualifying_buys_by_is_10b5_1"],
                         {"plan": 2, "no_plan": 2, "unknown": 2})
        r = self.rows_by_sk
        self.assertEqual((r["1"]["is_10b5_1"], r["7"]["is_10b5_1"]), ("plan", "plan"))
        self.assertEqual((r["3"]["is_10b5_1"], r["11"]["is_10b5_1"]), ("no_plan", "no_plan"))
        self.assertEqual((r["14"]["is_10b5_1"], r["17"]["is_10b5_1"]), ("unknown", "unknown"))
        # the footnote says 10b5-1, but the flag still follows AFF10B5ONE ('weird' → unknown)
        self.assertEqual(r["14"]["footnote_mentions_10b5_1"], "true")
        self.assertEqual(self.summary["qualifying_buys_footnote_mentions_10b5_1_by_is_10b5_1"],
                         {"unknown": 1})

    def test_flags_mark_but_do_not_exclude(self):
        r = self.rows_by_sk
        self.assertEqual(r["3"]["private_purchase_flag"], "true")
        self.assertEqual(r["3"]["buy_class"], parse.QUALIFYING)
        self.assertEqual(r["11"]["espp_or_drip_flag"], "true")
        self.assertEqual(r["11"]["private_purchase_flag"], "false")
        self.assertEqual(r["11"]["footnote_ids"], "F1;F2")
        flags = self.summary["qualifying_buy_flags"]
        self.assertEqual((flags["private_purchase_flag"], flags["espp_or_drip_flag"]), (1, 1))

    def test_joint_filing_is_one_row_with_all_owners(self):
        r = self.rows_by_sk["7"]
        self.assertEqual(r["owner_count"], 2)
        owners = json.loads(r["owners"])
        self.assertEqual([o["cik"] for o in owners], ["8000004", "8000005"])
        self.assertEqual(r["relationships"], "director;other")
        self.assertEqual(sum(1 for x in self.rows if x["nonderiv_trans_sk"] == "7"), 1)
        self.assertEqual(self.summary["qualifying_buy_flags"]["joint_filing"], 1)

    def test_relationships_and_context(self):
        self.assertEqual(self.rows_by_sk["1"]["relationships"], "director;officer")
        self.assertEqual(json.loads(self.rows_by_sk["10"]["owners"])[0]["relationship"], ["director"])
        ctx = self.summary["context"]
        self.assertEqual(ctx["unrecognized_relationship_tokens"], {"Trustee": 1})
        self.assertEqual(ctx["form4_derivative_table_code_p_rows"], 1)   # Form 5 P not counted

    def test_dates_and_identity(self):
        r = self.rows_by_sk["1"]
        self.assertEqual((r["filing_date"], r["trans_date"]), ("2026-08-05", "2026-08-03"))
        self.assertEqual((r["issuer_cik"], r["ticker_as_filed"]), ("9000001", "EX1"))


class TestHeaders(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.folder = self.tmp / "2026q3"
        shutil.copytree(SAMPLE, self.folder)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rewrite(self, table, fn):
        path = self.folder / f"{table}.tsv"
        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))
        rows = fn(rows)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh, delimiter="\t", quoting=csv.QUOTE_NONE, lineterminator="\n").writerows(rows)

    def drop_column(self, table, col):
        def fn(rows):
            i = rows[0].index(col)
            return [r[:i] + r[i + 1:] for r in rows]
        self.rewrite(table, fn)

    def test_missing_required_column_halts(self):
        self.drop_column("NONDERIV_TRANS", "TRANS_CODE")
        with self.assertRaises(parse.ParseError) as cm:
            parse.parse_folder(self.folder, "2026q3")
        self.assertIn("TRANS_CODE", str(cm.exception))

    def test_reordered_and_extra_columns_are_fine(self):
        def reverse_and_add(rows):
            return [list(reversed(r)) + (["NEW_COL"] if i == 0 else ["x"]) for i, r in enumerate(rows)]
        self.rewrite("NONDERIV_TRANS", reverse_and_add)
        _, summary = parse.parse_folder(self.folder, "2026q3")
        self.assertEqual(summary["funnel"]["qualifying_buys"], 6)

    def test_missing_aff10b5one_makes_every_buy_unknown(self):
        self.drop_column("SUBMISSION", "AFF10B5ONE")
        _, summary = parse.parse_folder(self.folder, "2026q3")
        self.assertFalse(summary["aff10b5one_column_present"])
        self.assertEqual(summary["qualifying_buys_by_is_10b5_1"], {"plan": 0, "no_plan": 0, "unknown": 6})

    def test_holdings_footnote_does_not_flag(self):
        # move sk 11's ESPP footnote from the price column to the holdings column
        def move(rows):
            h = rows[0]
            src, dst = h.index("TRANS_PRICEPERSHARE_FN"), h.index("SHRS_OWND_FOLWNG_TRANS_FN")
            sk = h.index("NONDERIV_TRANS_SK")
            for r in rows[1:]:
                if r[sk] == "11":
                    r[dst], r[src] = r[src], ""
            return rows
        self.rewrite("NONDERIV_TRANS", move)
        rows, summary = parse.parse_folder(self.folder, "2026q3")
        r = by_sk(rows)["11"]
        self.assertEqual((r["espp_or_drip_flag"], r["footnote_ids"]), ("false", "F1;F2"))
        self.assertNotIn("espp_or_drip_flag", summary["qualifying_buy_flags"])

    def test_ragged_row_halts(self):
        self.rewrite("NONDERIV_TRANS", lambda rows: rows + [["only", "two"]])
        with self.assertRaises(parse.ParseError):
            parse.parse_folder(self.folder, "2026q3")


class TestProvenanceAndOutputs(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.data = self.tmp / "form345"
        shutil.copytree(SAMPLE, self.data / "2026q3")
        sha = "ab" * 32
        (self.data / "2026q3" / ingest.EXTRACT_MARKER).write_text(json.dumps({"sha256": sha}))
        ingest.save_manifest(self.data, {"quarters": {"2026q3": {"sha256": sha}}})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_hash_mismatch_halts(self):
        ingest.save_manifest(self.data, {"quarters": {"2026q3": {"sha256": "cd" * 32}}})
        self.assertEqual(parse.main(["--quarters", "2026q3", "--data-dir", str(self.data),
                                     "--out-dir", str(self.tmp / "out")]), 1)
        self.assertFalse((self.tmp / "out").exists())

    def test_quarter_not_in_manifest_halts(self):
        with self.assertRaises(parse.ParseError):
            parse.check_provenance(self.data, "2026q2")

    def test_main_writes_csv_summary_and_audit(self):
        out = self.tmp / "out"
        self.assertEqual(parse.main(["--quarters", "2026q3", "--data-dir", str(self.data),
                                     "--out-dir", str(out)]), 0)
        with open(out / "2026q3_form4_transactions.csv", newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 16)
        self.assertEqual(list(rows[0].keys()), parse.OUTPUT_COLUMNS)
        summary = json.loads((out / "2026q3_parse_summary.json").read_text())
        self.assertEqual(summary["source_sha256"], "ab" * 32)
        audit = (out / "2026q3_parse-audit.md").read_text()
        self.assertIn("| … qualifying buys | 6 |", audit)
        self.assertNotIn("Owner 8000", audit)              # no reporting-owner names in the audit
        self.assertNotIn("pass", audit.lower().replace("does not say pass", ""))


if __name__ == "__main__":
    unittest.main()
