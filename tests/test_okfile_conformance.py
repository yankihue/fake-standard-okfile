import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from okfile.conformance import (
    CANONICAL_OKFILE,
    check_okfile,
    check_rfc,
    check_vectors,
    diagnose_okfile_bytes,
    explain_okfile_failure,
    main,
    render_certificate,
    render_json,
)


ROOT = Path(__file__).resolve().parents[1]


class OkFileConformanceTests(unittest.TestCase):
    def test_canonical_vector_is_accepted(self):
        result = diagnose_okfile_bytes(CANONICAL_OKFILE)
        self.assertTrue(result.ok)
        self.assertEqual(result.code, "OKF000")
        self.assertEqual(explain_okfile_failure(CANONICAL_OKFILE), "conforms")

    def test_normative_invalid_vectors_have_stable_codes(self):
        vectors = {
            "missing-lf": (b"OK", "OKF002"),
            "crlf": (b"OK\r\n", "OKF003"),
            "lowercase": (b"ok\n", "OKF006"),
            "trailing-space": (b"OK \n", "OKF005"),
            "bom-prefixed": (b"\xef\xbb\xbfOK\n", "OKF004"),
            "empty": (b"", "OKF001"),
            "enthusiastic": (b"OK!\n", "OKF005"),
            "hesitant": (b"OK?\n", "OKF005"),
            "leading-space": (b" OK\n", "OKF005"),
            "double-newline": (b"OK\n\n", "OKF005"),
        }
        for name, (data, code) in vectors.items():
            with self.subTest(name=name):
                result = diagnose_okfile_bytes(data)
                self.assertFalse(result.ok)
                self.assertEqual(result.code, code)

    def test_check_okfile_reads_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.ok"
            path.write_bytes(CANONICAL_OKFILE)
            result = check_okfile(path)
            self.assertTrue(result.ok)
            self.assertEqual(result.observed_hex, "4f4b0a")

    def test_check_rfc_requires_provenance_and_ceremony(self):
        result = check_rfc(ROOT / "RFC-0001-OKFILE.md")
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.profile, "ceremony")

    def test_check_rfc_rejects_missing_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RFC.md"
            path.write_text("## 3. Creative Provenance\nnothing to see\n", encoding="utf-8")
            result = check_rfc(path)
            self.assertFalse(result.ok)
            self.assertEqual(result.code, "OKF007")

    def test_vector_manifest_is_self_consistent(self):
        results = check_vectors(ROOT / "fixtures" / "vectors.json")
        self.assertTrue(results)
        self.assertTrue(all(result.ok for result in results), results)

    def test_json_report_contains_summary(self):
        report = render_json(
            [
                diagnose_okfile_bytes(CANONICAL_OKFILE, "valid"),
                diagnose_okfile_bytes(b"ok\n", "invalid"),
            ]
        )
        payload = json.loads(report)
        self.assertEqual(payload["summary"], {"total": 2, "passed": 1, "failed": 1})
        self.assertEqual(payload["creative_source"], "opencode go deepseek pro ran through CLI")

    def test_certificate_report_has_grandiose_verdict(self):
        report = render_certificate([diagnose_okfile_bytes(CANONICAL_OKFILE, "valid")])
        self.assertIn("CERTIFICATE OF OK FILE CONFORMANCE", report)
        self.assertIn("Verdict: AFFIRMED", report)
        self.assertIn("Seal Bytes: 4f 4b 0a", report)

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            valid = Path(tmp) / "valid.ok"
            invalid = Path(tmp) / "invalid.ok"
            valid.write_bytes(CANONICAL_OKFILE)
            invalid.write_bytes(b"ok\n")

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(valid)]), 0)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(invalid)]), 1)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "--ceremony",
                            "--rfc",
                            str(ROOT / "RFC-0001-OKFILE.md"),
                            "--vectors",
                            str(ROOT / "fixtures" / "vectors.json"),
                            str(valid),
                        ]
                    ),
                    0,
                )


if __name__ == "__main__":
    unittest.main()
