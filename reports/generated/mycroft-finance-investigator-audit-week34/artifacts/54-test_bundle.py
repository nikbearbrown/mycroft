from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.bundle import (
    BundleError,
    SourceArtifact,
    build_audit_bundle,
    default_bundle_sources,
    verify_audit_bundle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]


class AuditBundleTests(unittest.TestCase):
    def test_builds_and_verifies_reviewer_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "week34"
            manifest = build_audit_bundle("week34", output)
            result = verify_audit_bundle(output)

        self.assertEqual(manifest["summary"]["artifact_count"], 54)
        self.assertEqual(manifest["release_status"], "BLOCKED_PENDING_HUMAN_REVIEW")
        self.assertIsNone(manifest["human_attestation"])
        self.assertEqual(result["status"], "INTEGRITY_MATCHED_HUMAN_REVIEW_OPEN")

    def test_bundle_is_immutable_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "week34"
            build_audit_bundle("week34", output)

            with self.assertRaisesRegex(BundleError, "already exists"):
                build_audit_bundle("week34", output)

    def test_bundle_identifier_is_path_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(BundleError, "bundle_id"):
                build_audit_bundle("../week34", Path(temporary) / "week34")

    def test_verifier_detects_changed_packaged_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "week34"
            build_audit_bundle("week34", output)
            manifest = json.loads(
                (output / "manifest.json").read_text(encoding="utf-8")
            )
            report = next(
                item
                for item in manifest["artifacts"]
                if item["role"] == "investigation_report"
            )
            target = output / report["bundled_path"]
            target.write_text(target.read_text(encoding="utf-8") + "changed\n")

            with self.assertRaisesRegex(BundleError, "size mismatch"):
                verify_audit_bundle(output)

    def test_verifier_detects_changed_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "week34"
            build_audit_bundle("week34", output)
            manifest_path = output / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["release_status"] = "RELEASED"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

            with self.assertRaisesRegex(BundleError, "manifest checksum"):
                verify_audit_bundle(output)

    def test_verifier_detects_changed_human_review_view(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "week34"
            build_audit_bundle("week34", output)
            review_path = output / "REVIEW.md"
            review_path.write_text(
                review_path.read_text(encoding="utf-8") + "changed\n"
            )

            with self.assertRaisesRegex(BundleError, "review checksum"):
                verify_audit_bundle(output)

    def test_verifier_detects_an_unlisted_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "week34"
            build_audit_bundle("week34", output)
            (output / "artifacts/unlisted.txt").write_text("not in manifest\n")

            with self.assertRaisesRegex(BundleError, "inventory mismatch"):
                verify_audit_bundle(output)

    def test_cross_artifact_hash_mismatch_stops_packaging(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            scratch = Path(temporary)
            sources = []
            for source in default_bundle_sources():
                if source.role == "review_request":
                    copied = scratch / "review-request.json"
                    shutil.copyfile(source.path, copied)
                    payload = json.loads(copied.read_text(encoding="utf-8"))
                    payload["source_run_sha256"] = "0" * 64
                    copied.write_text(json.dumps(payload, indent=2) + "\n")
                    sources.append(
                        SourceArtifact(source.role, copied, source.bundled_name)
                    )
                else:
                    sources.append(source)

            with self.assertRaisesRegex(BundleError, "review request hash"):
                build_audit_bundle("mismatch", scratch / "bundle", sources)

    def test_human_boundary_is_visible_in_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "week34"
            build_audit_bundle("week34", output)
            review = (output / "REVIEW.md").read_text(encoding="utf-8")

        self.assertIn("BLOCKED_PENDING_HUMAN_REVIEW", review)
        self.assertIn("not a digital signature", review)
        self.assertIn("Did Not Establish", review)
        self.assertNotIn("Release status: `RELEASED`", review)


if __name__ == "__main__":
    unittest.main()
