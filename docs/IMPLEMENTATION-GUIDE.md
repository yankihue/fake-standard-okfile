# OK File Format Implementation Guide

This guide is non-normative, except emotionally.

## Producer Algorithm

1. Open the destination in binary mode.
2. Write exactly `b"OK\n"`.
3. Close the file.
4. Resist the urge to add context.
5. Resist the urge again.

Reference implementation:

```python
from pathlib import Path

Path("result.ok").write_bytes(b"OK\n")
```

## Consumer Algorithm

1. Read the candidate in binary mode.
2. Compare it to `b"OK\n"`.
3. Accept only if the comparison is exact.
4. Do not call `.strip()`.
5. Do not call `.lower()`.
6. Do not be generous.

Reference implementation:

```python
from pathlib import Path

valid = Path("result.ok").read_bytes() == b"OK\n"
```

## Compliance Ritual

For the full Ceremony Profile:

```sh
okfile \
  --ceremony \
  --rfc RFC-0001-OKFILE.md \
  --vectors fixtures/vectors.json \
  --format certificate \
  examples/valid.ok
```

The resulting certificate is deliberately grandiose. It is still only about
three bytes.

## Common Non-Conformances

| Candidate | Problem |
| --- | --- |
| `OK` | missing required LF |
| `OK\r\n` | CRLF is not LF |
| `ok\n` | lowercase drift |
| `OK \n` | surplus whitespace |
| `OK!\n` | emotional escalation |
| `\xef\xbb\xbfOK\n` | byte order mark |

## Design Maxim

When in doubt, bytes win. If two parties disagree about an OK file, place the
candidate under a hex dump and let the offsets testify.
