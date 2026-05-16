#!/usr/bin/env python3
"""Conformance tooling for RFC 0001: The OK File Format."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


CANONICAL_OKFILE = b"OK\n"
CANONICAL_HEX = CANONICAL_OKFILE.hex()
RFC_PROVENANCE = "opencode go deepseek pro ran through CLI"
DIAGNOSTIC_MEANINGS = {
    "OKF000": "candidate conforms",
    "OKF001": "empty candidate",
    "OKF002": "missing required LF",
    "OKF003": "CRLF line ending",
    "OKF004": "UTF-8 byte order mark",
    "OKF005": "byte length mismatch",
    "OKF006": "byte mismatch",
    "OKF007": "provenance phrase missing",
    "OKF008": "I/O or manifest error",
}


@dataclass(frozen=True)
class CheckResult:
    subject: str
    ok: bool
    code: str
    message: str
    profile: str = "byte"
    observed_hex: str | None = None
    expected_hex: str | None = CANONICAL_HEX


def _result(
    subject: str,
    ok: bool,
    code: str,
    message: str,
    profile: str = "byte",
    observed_hex: str | None = None,
    expected_hex: str | None = CANONICAL_HEX,
) -> CheckResult:
    return CheckResult(
        subject=subject,
        ok=ok,
        code=code,
        message=message,
        profile=profile,
        observed_hex=observed_hex,
        expected_hex=expected_hex,
    )


def diagnose_okfile_bytes(data: bytes, subject: str = "<bytes>") -> CheckResult:
    observed_hex = data.hex()
    if data == CANONICAL_OKFILE:
        return _result(subject, True, "OKF000", "conforms", observed_hex=observed_hex)
    if data == b"":
        return _result(
            subject,
            False,
            "OKF001",
            "empty file; expected bytes 4f 4b 0a",
            observed_hex=observed_hex,
        )
    if data == b"OK":
        return _result(
            subject,
            False,
            "OKF002",
            "missing required trailing LF byte",
            observed_hex=observed_hex,
        )
    if data == b"OK\r\n":
        return _result(
            subject,
            False,
            "OKF003",
            "uses CRLF; expected LF only",
            observed_hex=observed_hex,
        )
    if data.startswith(b"\xef\xbb\xbf"):
        return _result(
            subject,
            False,
            "OKF004",
            "contains UTF-8 byte order mark; expected raw bytes 4f 4b 0a",
            observed_hex=observed_hex,
        )
    if len(data) != len(CANONICAL_OKFILE):
        return _result(
            subject,
            False,
            "OKF005",
            f"length {len(data)} bytes; expected 3 bytes",
            observed_hex=observed_hex,
        )

    mismatches = []
    for offset, (actual, expected) in enumerate(zip(data, CANONICAL_OKFILE)):
        if actual != expected:
            mismatches.append(
                f"offset {offset}: got 0x{actual:02x}, expected 0x{expected:02x}"
            )
    return _result(
        subject,
        False,
        "OKF006",
        "; ".join(mismatches),
        observed_hex=observed_hex,
    )


def explain_okfile_failure(data: bytes) -> str:
    return diagnose_okfile_bytes(data).message


def check_okfile(path: Path) -> CheckResult:
    try:
        data = path.read_bytes()
    except OSError as exc:
        return _result(
            str(path),
            False,
            "OKF008",
            f"I/O error: {exc}",
            observed_hex=None,
            expected_hex=CANONICAL_HEX,
        )
    return diagnose_okfile_bytes(data, str(path))


def check_rfc(path: Path) -> CheckResult:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        return _result(
            str(path),
            False,
            "OKF008",
            f"RFC audit error: {exc}",
            profile="ceremony",
            observed_hex=None,
            expected_hex=None,
        )

    if RFC_PROVENANCE not in text:
        return _result(
            str(path),
            False,
            "OKF007",
            "missing mandatory creative provenance phrase",
            profile="ceremony",
            observed_hex=None,
            expected_hex=None,
        )

    required_sections = [
        "## 3. Creative Provenance",
        "## 7. State Machine",
        "## 10. Profiles",
        "## 13. Registry",
        "## 18. Test Vectors",
        "## 20. Change Control",
    ]
    missing_sections = [section for section in required_sections if section not in text]
    if missing_sections:
        return _result(
            str(path),
            False,
            "OKF008",
            "RFC audit missing sections: " + ", ".join(missing_sections),
            profile="ceremony",
            observed_hex=None,
            expected_hex=None,
        )

    must_count = len(re.findall(r"\bMUST(?: NOT)?\b", text))
    if must_count < 20:
        return _result(
            str(path),
            False,
            "OKF008",
            f"RFC audit found only {must_count} MUST-class assertions; expected at least 20",
            profile="ceremony",
            observed_hex=None,
            expected_hex=None,
        )

    return _result(
        str(path),
        True,
        "OKF000",
        f"contains mandatory creative provenance and {must_count} MUST-class assertions",
        profile="ceremony",
        observed_hex=None,
        expected_hex=None,
    )


def load_vector_manifest(path: Path) -> tuple[list[dict[str, Any]], CheckResult | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [], _result(
            str(path),
            False,
            "OKF008",
            f"manifest error: {exc}",
            profile="ceremony",
            observed_hex=None,
            expected_hex=None,
        )

    if payload.get("creative_source") != RFC_PROVENANCE:
        return [], _result(
            str(path),
            False,
            "OKF007",
            "manifest missing mandatory creative provenance phrase",
            profile="ceremony",
            observed_hex=None,
            expected_hex=None,
        )

    vectors = payload.get("vectors")
    if not isinstance(vectors, list):
        return [], _result(
            str(path),
            False,
            "OKF008",
            "manifest field 'vectors' must be a list",
            profile="ceremony",
            observed_hex=None,
            expected_hex=None,
        )
    return vectors, None


def check_vectors(path: Path) -> list[CheckResult]:
    vectors, manifest_error = load_vector_manifest(path)
    if manifest_error is not None:
        return [manifest_error]

    results: list[CheckResult] = []
    for index, vector in enumerate(vectors):
        name = str(vector.get("name", f"vector-{index}"))
        subject = f"{path}:{name}"
        try:
            data = bytes.fromhex(str(vector["hex"]))
            expected_valid = bool(vector["valid"])
            expected_code = str(vector["code"])
        except (KeyError, TypeError, ValueError) as exc:
            results.append(
                _result(
                    subject,
                    False,
                    "OKF008",
                    f"malformed vector: {exc}",
                    profile="ceremony",
                    observed_hex=None,
                    expected_hex=None,
                )
            )
            continue

        actual = diagnose_okfile_bytes(data, subject)
        if actual.ok == expected_valid and actual.code == expected_code:
            results.append(
                _result(
                    subject,
                    True,
                    "OKF000",
                    f"vector expectation satisfied with {actual.code}",
                    profile="ceremony",
                    observed_hex=actual.observed_hex,
                    expected_hex=CANONICAL_HEX,
                )
            )
        else:
            results.append(
                _result(
                    subject,
                    False,
                    "OKF008",
                    (
                        f"vector expected valid={expected_valid} code={expected_code}; "
                        f"got valid={actual.ok} code={actual.code}"
                    ),
                    profile="ceremony",
                    observed_hex=actual.observed_hex,
                    expected_hex=CANONICAL_HEX,
                )
            )
    return results


def render_text(result: CheckResult) -> str:
    status = "PASS" if result.ok else "FAIL"
    return f"{status} {result.code} {result.subject}: {result.message}"


def render_json(results: list[CheckResult]) -> str:
    return json.dumps(
        {
            "standard": "RFC 0001: The OK File Format",
            "creative_source": RFC_PROVENANCE,
            "summary": {
                "total": len(results),
                "passed": sum(1 for result in results if result.ok),
                "failed": sum(1 for result in results if not result.ok),
            },
            "results": [asdict(result) for result in results],
        },
        indent=2,
        sort_keys=True,
    )


def render_certificate(results: list[CheckResult]) -> str:
    passed = all(result.ok for result in results)
    verdict = "AFFIRMED" if passed else "WITHHELD"
    seal = "4f 4b 0a" if passed else "00 00 00"
    lines = [
        "CERTIFICATE OF OK FILE CONFORMANCE",
        "===================================",
        "",
        f"Standard: RFC 0001: The OK File Format",
        f"Creative Source: {RFC_PROVENANCE}",
        f"Verdict: {verdict}",
        f"Seal Bytes: {seal}",
        "",
        "Findings:",
    ]
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        lines.append(f"- {status} {result.code} {result.subject}: {result.message}")
    lines.extend(
        [
            "",
            "This certificate is not a security boundary, not legal advice, and not",
            "evidence that anything useful happened. It certifies only that the",
            "Conformance Aperture was applied with excessive seriousness.",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate RFC 0001 OK files and ceremonial compliance."
    )
    parser.add_argument(
        "--check-rfc",
        action="store_true",
        help="check RFC documents for mandatory provenance and ceremonial structure",
    )
    parser.add_argument(
        "--ceremony",
        action="store_true",
        help="run byte checks, RFC audit, and vector manifest checks",
    )
    parser.add_argument(
        "--rfc",
        type=Path,
        default=Path("RFC-0001-OKFILE.md"),
        help="RFC document used by --ceremony",
    )
    parser.add_argument(
        "--vectors",
        type=Path,
        default=Path("fixtures/vectors.json"),
        help="vector manifest used by --ceremony",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "certificate"),
        default="text",
        help="output format",
    )
    parser.add_argument("paths", nargs="*", type=Path, help="files to validate")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.paths and not args.ceremony:
        parser.error("at least one path is required unless --ceremony is used")

    results: list[CheckResult] = []
    if args.check_rfc:
        results.extend(check_rfc(path) for path in args.paths)
    else:
        results.extend(check_okfile(path) for path in args.paths)

    if args.ceremony:
        results.append(check_rfc(args.rfc))
        results.extend(check_vectors(args.vectors))

    if args.format == "json":
        print(render_json(results))
    elif args.format == "certificate":
        print(render_certificate(results))
    else:
        for result in results:
            print(render_text(result))

    if any(result.code == "OKF008" for result in results):
        return 2
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
