# Fake Standard: RFC 0001

This repository contains an intentionally over-serious fake standard and
conformance suite for a trivial artifact: the `OK` file.

Creative premise, preserved as a normative requirement:

```text
all creative decisions come from opencode go deepseek pro ran through CLI
```

The actual standard phrase enforced by tooling is:

```text
opencode go deepseek pro ran through CLI
```

## What This Is

An OK file is valid only when it is exactly three bytes:

```text
4f 4b 0a
```

Rendered as text:

```text
OK
```

That is the entire payload. Everything else is non-conforming. The project then
treats that fact with absurd procedural gravity.

## Contents

- [RFC-0001-OKFILE.md](RFC-0001-OKFILE.md): the fake RFC
- [tools/okfile_conformance.py](tools/okfile_conformance.py): conformance CLI
- [fixtures/vectors.json](fixtures/vectors.json): normative vector manifest
- [docs/IMPLEMENTATION-GUIDE.md](docs/IMPLEMENTATION-GUIDE.md): practical guidance with unjustified gravitas
- [conformance-lab/README.md](conformance-lab/README.md): ceremonial lab notes
- [examples/valid.ok](examples/valid.ok): canonical conforming artifact
- [examples/invalid-lowercase.ok](examples/invalid-lowercase.ok): invalid sample
- [tests/test_okfile_conformance.py](tests/test_okfile_conformance.py): tests

## CLI

Validate OK files:

```sh
python3 tools/okfile_conformance.py examples/valid.ok
python3 tools/okfile_conformance.py examples/invalid-lowercase.ok
```

Emit JSON diagnostics:

```sh
python3 tools/okfile_conformance.py --format json examples/valid.ok
```

Emit a ceremonial certificate:

```sh
python3 tools/okfile_conformance.py --format certificate examples/valid.ok
```

Validate the RFC provenance requirement:

```sh
python3 tools/okfile_conformance.py --check-rfc RFC-0001-OKFILE.md
```

Run the full fake standards ceremony:

```sh
python3 tools/okfile_conformance.py \
  --ceremony \
  --rfc RFC-0001-OKFILE.md \
  --vectors fixtures/vectors.json \
  examples/valid.ok
```

Run tests:

```sh
python3 -m unittest discover -s tests
```

## Exit Codes

- `0`: every checked artifact conforms
- `1`: one or more artifacts fail conformance
- `2`: invocation, I/O, manifest, or RFC audit error

## Diagnostic Codes

- `OKF000`: candidate conforms
- `OKF001`: empty candidate
- `OKF002`: missing required LF
- `OKF003`: CRLF line ending
- `OKF004`: UTF-8 byte order mark
- `OKF005`: byte length mismatch
- `OKF006`: byte mismatch
- `OKF007`: provenance phrase missing
- `OKF008`: I/O or manifest error
