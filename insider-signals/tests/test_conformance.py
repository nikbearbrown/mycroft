"""
GIGO / gate G2 (conformance.py): the halting checks, promotion, the audit and the spot-check.

What is pinned here:
  - on the clean sample every halting check passes and exactly the qualifying buys are
    promoted, with VERIFIED_COLUMNS and their flags (flagged buys stay in the file);
  - **any halting failure writes nothing to data/verified/**: the files already there keep
    their bytes, no file is added, and the failure audit goes to the staging folder instead.
    Covered: hash, required column, duplicate key, a buy dated after its filing, a blank CIK,
    a non-buy smuggled into the buys file, a buy missing from it;
  - the buy-filter purity check is independent of parse.classify (it re-derives the buys
    from the raw tables);
  - the spot-check: reproducible seeded sample; compares code, shares, price, date with the
    filing XML; lists mismatches without correcting them or blocking promotion; tries the
    owner's EDGAR path after a 404; caches filings so a re-run makes no requests; sends the
    User-Agent; and a 403 halts (exit 3) with data/verified/ unchanged;
  - main() refuses (exit 2) without SEC_USER_AGENT unless --no-spot-check is given;
  - the audit reports Rule 1 counts, amendments that repeat an original buy, lag and joint
    filings, and names no reporting owner.

No network: SEC is a scripted fake opener. The fixture is tests/fixtures/parse_sample/
(synthetic rows under real 2026 Q3 headers), run through parse.py in a temp folder.
"""

from __future__ import annotations

import csv
import io
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import conformance  # noqa: E402
import ingest  # noqa: E402
import parse  # noqa: E402

SAMPLE = Path(__file__).resolve().parent / "fixtures" / "parse_sample"
UA = "Test Runner test@example.org"
Q = "2026q3"


# --------------------------------------------------------------------------- fakes

class Resp:
    def __init__(self, status=200, body=b""):
        self.status, self.headers, self._buf = status, {}, io.BytesIO(body)

    def read(self, n=-1):
        return self._buf.read(n)

    def close(self):
        pass


class FakeSec:
    def __init__(self, routes):
        self.routes, self.calls = dict(routes), []

    def __call__(self, url, headers, timeout):
        self.calls.append((url, dict(headers)))
        r = self.routes.get(url)
        return r() if callable(r) else Resp(404)


class Clock:
    def __init__(self):
        self.t = 0.0

    def monotonic(self):
        return self.t

    def sleep(self, dt):
        self.t += dt

    def now(self):
        return datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc) + timedelta(seconds=self.t)


def filing_text(row, shares=None, doc_type=None):
    """A minimal EDGAR full-submission file whose Form 4 XML has a decoy sale and this buy."""
    tx = ("<nonDerivativeTransaction><transactionDate><value>{d}</value></transactionDate>"
          "<transactionCoding><transactionCode>{c}</transactionCode></transactionCoding>"
          "<transactionAmounts><transactionShares><value>{s}</value></transactionShares>"
          "<transactionPricePerShare><value>{p}</value></transactionPricePerShare>"
          "<transactionAcquiredDisposedCode><value>{a}</value></transactionAcquiredDisposedCode>"
          "</transactionAmounts></nonDerivativeTransaction>")
    xml = ('<?xml version="1.0"?>\n<ownershipDocument>'
           f"<documentType>{doc_type or row['document_type']}</documentType>"
           f"<issuer><issuerCik>{int(row['issuer_cik']):010d}</issuerCik></issuer>"
           "<nonDerivativeTable>"
           + tx.format(d="2020-01-02", c="S", s="1", p="1", a="D")
           + tx.format(d=row["trans_date"], c="P", s=shares or row["shares"], p=row["price"], a="A")
           + "</nonDerivativeTable></ownershipDocument>")
    return (f"<SEC-DOCUMENT>\n<DOCUMENT>\n<TYPE>{row['document_type']}\n<TEXT>\n<XML>\n{xml}\n"
            "</XML>\n</TEXT>\n</DOCUMENT>\n</SEC-DOCUMENT>\n").encode()


def read_tsv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))
    return rows[0], rows[1:]


def write_tsv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", quoting=csv.QUOTE_NONE, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


# --------------------------------------------------------------------------- base

class GigoCase(unittest.TestCase):
    """A temp project: extracted sample quarter with real provenance, parsed by parse.py."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.data, self.parsed = self.tmp / "form345", self.tmp / "parsed"
        self.verified, self.staging = self.tmp / "verified", self.tmp / "staging"
        self.filings = self.tmp / "filings"
        shutil.copytree(SAMPLE, self.data / Q)
        self.data.mkdir(exist_ok=True)
        zp = ingest.zip_path(self.data, Q)
        zp.write_bytes(b"stand-in for the quarter's ZIP")
        sha = ingest.sha256_file(zp)
        (self.data / Q / ingest.EXTRACT_MARKER).write_text(json.dumps({"sha256": sha}))
        ingest.save_manifest(self.data, {"quarters": {Q: {"sha256": sha}}})
        self.assertEqual(parse.main(["--quarters", Q, "--data-dir", str(self.data),
                                     "--out-dir", str(self.parsed)]), 0)
        self.clock = Clock()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def client(self, sec):
        return ingest.SecClient(UA, 1.0, self.filings / ingest.REQUEST_LOG_NAME, opener=sec,
                                clock=self.clock.monotonic, sleep=self.clock.sleep,
                                now=self.clock.now)

    def run_gigo(self, client=None, n=25):
        return conformance.run([Q], self.data, self.parsed, self.verified, self.staging,
                               self.filings, client, n, now=self.clock.now)

    def parsed_buys(self):
        with open(self.parsed / f"{Q}_form4_transactions.csv", newline="", encoding="utf-8") as fh:
            return [r for r in csv.DictReader(fh) if r["buy_class"] == parse.QUALIFYING]

    def verified_rows(self):
        with open(self.verified / conformance.BUYS_NAME, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def routes_for(self, rows, path_cik="issuer", tamper=None):
        routes = {}
        for r in rows:
            cik = r["issuer_cik"] if path_cik == "issuer" else r["owners_first_cik"]
            url = conformance.filing_url(cik, r["accession_number"], f"{r['accession_number']}.txt")
            body = filing_text(r, **(tamper or {}).get(r["nonderiv_trans_sk"], {}))
            routes[url] = (lambda b=body: Resp(200, b))
        return routes


# --------------------------------------------------------------------------- helpers

class TestHelpers(unittest.TestCase):
    def test_sec_date_is_strict(self):
        self.assertEqual(conformance.sec_date("05-AUG-2026"), date(2026, 8, 5))
        for bad in ("5-AUG-2026", "2026-08-05", "", "31-FEB-2026", None):
            self.assertIsNone(conformance.sec_date(bad), bad)

    def test_buy_filter_is_independent_and_complete(self):
        ok = dict(doc_type="4", code="P", acquired="A", shares="10", price="1.5", equity_swap="0")
        self.assertTrue(conformance.meets_buy_filter(**ok))
        self.assertTrue(conformance.meets_buy_filter(**{**ok, "doc_type": "4/A", "code": "p"}))
        for k, v in [("doc_type", "5"), ("code", "S"), ("acquired", "D"), ("shares", "0"),
                     ("shares", ""), ("price", "-1"), ("price", "x"), ("equity_swap", "true")]:
            self.assertFalse(conformance.meets_buy_filter(**{**ok, k: v}), (k, v))

    def test_business_days(self):
        fri, mon = date(2026, 8, 7), date(2026, 8, 10)
        self.assertEqual(conformance.business_days(fri, mon), 1)
        self.assertEqual(conformance.business_days(fri, fri), 0)
        self.assertEqual(conformance.business_days(mon, date(2026, 8, 13)), 3)

    def test_seed_is_reproducible_and_order_free(self):
        a = conformance.spot_check_seed(["aa", "bb"])
        self.assertEqual(a, conformance.spot_check_seed(["bb", "aa"]))
        self.assertNotEqual(a, conformance.spot_check_seed(["aa", "bc"]))

    def test_compare_filing_picks_the_matching_transaction(self):
        row = {"trans_code": "P", "shares": "100", "price": "2.50", "trans_date": "2026-08-03",
               "document_type": "4", "issuer_cik": "9000001"}
        doc = conformance.ownership_xml(filing_text(row).decode())
        res = conformance.compare_filing(row, doc)
        self.assertTrue(res["match"])
        self.assertEqual(res["xml_transactions"], 2)
        self.assertTrue(res["issuer_cik_match"] and res["document_type_match"])
        bad = conformance.compare_filing(row, conformance.ownership_xml(
            filing_text(row, shares="101", doc_type="4/A").decode()))
        self.assertFalse(bad["match"])
        self.assertEqual(bad["fields"], {"code": True, "shares": False, "price": True, "date": True})
        self.assertFalse(bad["document_type_match"])

    def test_rounding_only_is_told_apart_from_a_real_mismatch(self):
        row = {"trans_code": "P", "shares": "100.0", "price": "0.01", "trans_date": "2026-08-03",
               "document_type": "4", "issuer_cik": "9000001"}
        filed = dict(row, shares="100", price="0.006")
        res = conformance.compare_filing(row, conformance.ownership_xml(filing_text(filed).decode()))
        self.assertFalse(res["match"])
        self.assertTrue(res["rounding_only"])
        real = conformance.compare_filing(row, conformance.ownership_xml(
            filing_text(dict(filed, price="0.02")).decode()))
        self.assertFalse(real["rounding_only"])
        self.assertTrue(conformance.rounds_to(conformance.dec("4701.02"), conformance.dec("4701.015")))
        self.assertTrue(conformance.rounds_to(conformance.dec("3.22"), conformance.dec("3.2199")))
        self.assertFalse(conformance.rounds_to(conformance.dec("3.21"), conformance.dec("3.2199")))

    def test_no_xml_block(self):
        self.assertIsNone(conformance.ownership_xml("<SEC-DOCUMENT>no xml</SEC-DOCUMENT>"))


# --------------------------------------------------------------------------- pass path

class TestPromotion(GigoCase):
    def test_clean_sample_promotes_exactly_the_buys(self):
        code, s = self.run_gigo()
        self.assertEqual(code, 0)
        self.assertEqual(s["failed_checks"], [])
        rows = self.verified_rows()
        self.assertEqual(list(rows[0].keys()), conformance.VERIFIED_COLUMNS)
        want = {(r["accession_number"], r["nonderiv_trans_sk"]) for r in self.parsed_buys()}
        self.assertEqual({(r["accession_number"], r["nonderiv_trans_sk"]) for r in rows}, want)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(r["trans_code"] == "P" and r["acquired_disposed"] == "A" for r in rows))
        self.assertEqual(sorted(p.name for p in self.verified.iterdir()),
                         sorted([conformance.BUYS_NAME, conformance.AUDIT_NAME, conformance.SUMMARY_NAME]))
        self.assertEqual(list(self.staging.iterdir()), [])      # stage folder cleaned up
        summary = json.loads((self.verified / conformance.SUMMARY_NAME).read_text())
        self.assertEqual(summary["insider_buys_sha256"],
                         ingest.sha256_file(self.verified / conformance.BUYS_NAME))

    def test_flagged_buys_stay_in_verified_with_flags(self):
        self.run_gigo()
        rows = self.verified_rows()
        self.assertTrue(any(r["private_purchase_flag"] == "true" for r in rows))
        self.assertTrue(any(r["espp_or_drip_flag"] == "true" for r in rows))
        f = json.loads((self.verified / conformance.SUMMARY_NAME).read_text())["findings"][Q]
        p = f["prereg_rule1"]
        self.assertEqual(p["cluster_eligible"] + p["excluded_from_clustering"], len(rows))

    def test_joint_filing_lists_every_owner(self):
        self.run_gigo()
        joint = [r for r in self.verified_rows() if int(r["owner_count"]) > 1]
        self.assertTrue(joint)
        for r in joint:
            self.assertEqual(len(r["rptowner_ciks"].split(";")), int(r["owner_count"]))

    def test_audit_without_spot_check_says_not_run_and_names_no_owner(self):
        self.run_gigo()
        audit = (self.verified / conformance.AUDIT_NAME).read_text()
        self.assertIn("**Not run** (--no-spot-check)", audit)
        self.assertIn("PRE_REGISTRATION.md Rule 1", audit)
        self.assertIn("### Amendments (4/A)", audit)
        self.assertNotIn("Owner 8000", audit)


# --------------------------------------------------------------------------- failure path

class TestNothingWrittenOnFailure(GigoCase):
    """Each halting failure: exit 1, data/verified/ byte-for-byte unchanged, audit in staging."""

    def setUp(self):
        super().setUp()
        self.verified.mkdir()
        (self.verified / conformance.BUYS_NAME).write_text("previous verified version\n")
        (self.verified / "clusters.json").write_text("{}\n")
        self.before = {p.name: p.read_bytes() for p in self.verified.iterdir()}

    def assert_halted(self, check):
        code, s = self.run_gigo(self.client(FakeSec({})))
        self.assertEqual(code, 1)
        self.assertIn(f"{Q}:{check}", s["failed_checks"])
        self.assertFalse(s["promoted"])
        self.assertEqual({p.name: p.read_bytes() for p in self.verified.iterdir()}, self.before)
        failed = list(self.staging.glob("conformance-audit-FAILED-*.md"))
        self.assertEqual(len(failed), 1)
        self.assertIn("NOT PROMOTED", failed[0].read_text())
        self.assertFalse(self.filings.exists())       # no spot-check requests on a failure
        return s

    def edit_raw(self, table, fn):
        header, rows = read_tsv(self.data / Q / f"{table}.tsv")
        write_tsv(self.data / Q / f"{table}.tsv", *fn(header, rows))

    def test_hash_mismatch(self):
        ingest.zip_path(self.data, Q).write_bytes(b"different bytes")
        s = self.assert_halted("hash")
        self.assertTrue(s["halting_checks"][Q]["keys"]["not_run"])

    def test_missing_contract_column(self):
        def drop(h, rows):
            i = h.index("AFF10B5ONE")
            return h[:i] + h[i + 1:], [r[:i] + r[i + 1:] for r in rows]
        self.edit_raw("SUBMISSION", drop)
        self.assert_halted("required_columns")

    def test_duplicate_key(self):
        self.edit_raw("NONDERIV_TRANS", lambda h, rows: (h, rows + [rows[0]]))
        self.assert_halted("keys")

    def test_buy_dated_after_its_filing(self):
        buy = self.parsed_buys()[0]
        def late(h, rows):
            a, s, t = h.index("ACCESSION_NUMBER"), h.index("NONDERIV_TRANS_SK"), h.index("TRANS_DATE")
            for r in rows:
                if (r[a], r[s]) == (buy["accession_number"], buy["nonderiv_trans_sk"]):
                    r[t] = "31-DEC-2026"
            return h, rows
        self.edit_raw("NONDERIV_TRANS", late)
        self.assert_halted("dates")

    def test_blank_issuer_cik(self):
        acc = self.parsed_buys()[0]["accession_number"]
        def blank(h, rows):
            a, c = h.index("ACCESSION_NUMBER"), h.index("ISSUERCIK")
            for r in rows:
                if r[a] == acc:
                    r[c] = ""
            return h, rows
        self.edit_raw("SUBMISSION", blank)
        self.assert_halted("identity")

    def _edit_parsed(self, fn):
        path = self.parsed / f"{Q}_form4_transactions.csv"
        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        rows = fn(rows)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=parse.OUTPUT_COLUMNS)
            w.writeheader()
            w.writerows(rows)

    def test_non_buy_in_buys_file(self):
        def smuggle(rows):
            sale = next(r for r in rows if r["trans_code"] == "S")
            sale["buy_class"] = parse.QUALIFYING
            return rows
        self._edit_parsed(smuggle)
        s = self.assert_halted("buy_filter_purity")
        self.assertTrue(any("fails the buy filter" in e
                            for e in s["halting_checks"][Q]["buy_filter_purity"]["examples"]))

    def test_buy_missing_from_buys_file(self):
        drop_key = (self.parsed_buys()[0]["accession_number"], self.parsed_buys()[0]["nonderiv_trans_sk"])
        self._edit_parsed(lambda rows: [r for r in rows
                                        if (r["accession_number"], r["nonderiv_trans_sk"]) != drop_key])
        s = self.assert_halted("buy_filter_purity")
        self.assertTrue(any("missing from the buys file" in e
                            for e in s["halting_checks"][Q]["buy_filter_purity"]["examples"]))

    def test_sec_refusal_during_spot_check(self):
        sec = FakeSec({u: (lambda: Resp(403)) for u in self._all_urls()})
        code, s = self.run_gigo(self.client(sec), n=6)
        self.assertEqual(code, 3)
        self.assertEqual({p.name: p.read_bytes() for p in self.verified.iterdir()}, self.before)
        self.assertIn("halted by SEC", s["spot_check"]["reason"])

    def _all_urls(self):
        urls = []
        for r in self.parsed_buys():
            for o in json.loads(r["owners"]):
                urls.append(conformance.filing_url(o["cik"], r["accession_number"], f"{r['accession_number']}.txt"))
            urls.append(conformance.filing_url(r["issuer_cik"], r["accession_number"], f"{r['accession_number']}.txt"))
        return urls

    def test_main_refuses_without_user_agent(self):
        argv = ["--quarters", Q, "--data-dir", str(self.data), "--parsed-dir", str(self.parsed),
                "--verified-dir", str(self.verified), "--staging-dir", str(self.staging),
                "--filings-dir", str(self.filings)]
        self.assertEqual(conformance.main(argv, env={}), 2)
        self.assertEqual({p.name: p.read_bytes() for p in self.verified.iterdir()}, self.before)


# --------------------------------------------------------------------------- spot-check

class TestSpotCheck(GigoCase):
    def test_matches_mismatches_and_logging(self):
        rows = self.parsed_buys()
        tampered = rows[0]["nonderiv_trans_sk"]
        sec = FakeSec(self.routes_for(rows, tamper={tampered: {"shares": "999999"}}))
        code, s = self.run_gigo(self.client(sec), n=25)
        self.assertEqual(code, 0)                          # a mismatch is a finding, not a halt
        sc = s["spot_check"]
        self.assertEqual(sc["n"], len(rows))
        self.assertEqual(sc["matched"], len(rows) - 1)
        bad = [x for x in sc["results"] if not x["match"]]
        self.assertEqual([x["nonderiv_trans_sk"] for x in bad], [tampered])
        self.assertEqual(bad[0]["fields"]["shares"], False)
        # the data set is not corrected
        v = {r["nonderiv_trans_sk"]: r for r in self.verified_rows()}
        self.assertEqual(v[tampered]["shares"], rows[0]["shares"])
        self.assertTrue(all(h["User-Agent"] == UA for _, h in sec.calls))
        log = (self.filings / ingest.REQUEST_LOG_NAME).read_text().splitlines()
        self.assertEqual(len(log), len({r["accession_number"] for r in rows}))
        audit = (self.verified / conformance.AUDIT_NAME).read_text()
        self.assertIn(f"**{len(rows) - 1} of {len(rows)} match exactly**", audit)
        self.assertEqual((sc["rounding_only"], sc["substantive_mismatch"]), (0, 1))
        self.assertIn("MISMATCH", audit)

    def test_sample_is_reproducible(self):
        rows = self.parsed_buys()
        sec = FakeSec(self.routes_for(rows))
        _, a = self.run_gigo(self.client(sec), n=3)
        shutil.rmtree(self.filings)
        _, b = self.run_gigo(self.client(FakeSec(self.routes_for(rows))), n=3)
        key = lambda s: [(x["accession_number"], x["nonderiv_trans_sk"]) for x in s["spot_check"]["results"]]
        self.assertEqual(key(a), key(b))
        self.assertEqual(len(key(a)), 3)

    def test_owner_path_after_404_and_cache_on_rerun(self):
        rows = self.parsed_buys()
        for r in rows:
            r["owners_first_cik"] = json.loads(r["owners"])[0]["cik"]
        sec = FakeSec(self.routes_for(rows, path_cik="owner"))   # issuer path → 404
        code, s = self.run_gigo(self.client(sec), n=25)
        self.assertEqual(code, 0)
        self.assertEqual(s["spot_check"]["matched"], len(rows))
        self.assertTrue(any("/9000" in u for u, _ in sec.calls))     # issuer path tried first
        sec2 = FakeSec({})
        code, s2 = self.run_gigo(self.client(sec2), n=25)
        self.assertEqual(code, 0)
        self.assertEqual(sec2.calls, [])                              # all from cache
        self.assertTrue(all(x["cached"] for x in s2["spot_check"]["results"]))

    def test_filing_not_found_is_reported(self):
        code, s = self.run_gigo(self.client(FakeSec({})), n=2)
        self.assertEqual(code, 0)
        self.assertEqual({x["status"] for x in s["spot_check"]["results"]}, {"filing_not_found"})
        self.assertEqual(s["spot_check"]["matched"], 0)


if __name__ == "__main__":
    unittest.main()
