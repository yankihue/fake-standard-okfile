# The OK File Standard

[![CI](https://github.com/yankihue/fake-standard-okfile/actions/workflows/ci.yml/badge.svg)](https://github.com/yankihue/fake-standard-okfile/actions/workflows/ci.yml)

RFC 0001 defines the only valid OK file:

```text
OK
```

That display hides the whole standard: exactly three bytes, `4f 4b 0a`.
Uppercase `O`, uppercase `K`, one LF. No CRLF. No BOM. No enthusiasm.

This repository contains the RFC, conformance CLI, fixture vectors, diagnostic
codes, tests, and a small public dossier page.

## Quick Start

Run from a checkout:

```sh
python3 tools/okfile_conformance.py examples/valid.ok
python3 tools/okfile_conformance.py examples/invalid-lowercase.ok
```

Install the CLI:

```sh
python3 -m pip install .
okfile examples/valid.ok
```

Install with `pipx` from GitHub:

```sh
pipx install git+https://github.com/yankihue/fake-standard-okfile.git
okfile examples/valid.ok
```

Run the full ceremony:

```sh
okfile \
  --ceremony \
  --rfc RFC-0001-OKFILE.md \
  --vectors fixtures/vectors.json \
  examples/valid.ok
```

Issue a certificate:

```sh
okfile --format certificate examples/valid.ok
```

## What Counts As OK?

Valid:

```text
4f 4b 0a
```

Invalid examples include:

- `OK` without the trailing LF: `OKF002`
- `OK\r\n`: `OKF003`
- UTF-8 BOM plus `OK\n`: `OKF004`
- `OK \n`, `OK!\n`, or `OK\n\n`: `OKF005`
- `ok\n`: `OKF006`

The fixture manifest in [fixtures/vectors.json](fixtures/vectors.json) is the
normative test inventory.

## Exit Codes

- `0`: every checked artifact conforms
- `1`: one or more artifacts fail conformance
- `2`: invocation, I/O, manifest, or RFC audit error

## Repository Map

- [RFC-0001-OKFILE.md](RFC-0001-OKFILE.md): the RFC
- [okfile/conformance.py](okfile/conformance.py): importable reference implementation
- [okfile/cli.py](okfile/cli.py): console entrypoint for `okfile`
- [tools/okfile_conformance.py](tools/okfile_conformance.py): compatibility wrapper
- [fixtures/vectors.json](fixtures/vectors.json): normative vector manifest
- [examples/valid.ok](examples/valid.ok): canonical conforming artifact
- [examples/invalid-lowercase.ok](examples/invalid-lowercase.ok): invalid sample
- [tests/test_okfile_conformance.py](tests/test_okfile_conformance.py): conformance tests
- [docs/IMPLEMENTATION-GUIDE.md](docs/IMPLEMENTATION-GUIDE.md): implementation guidance
- [site/](site/): static dossier and browser validator

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

## Tests

```sh
python3 -m unittest discover -s tests
```

CI runs the tests, installs the package, verifies `okfile examples/valid.ok`,
and runs the ceremony profile.

## Prior Art

- RFC 2119, for normative keyword interpretation.
- Unix exit status `0`, for being useful without needing a committee.
- CI status badges.

## License

MIT.
