# Conformance Lab

This directory contains the recommended conformance exercise for RFC 0001.

Suggested lab exercise:

```sh
okfile \
  --format certificate \
  --ceremony \
  --rfc ../RFC-0001-OKFILE.md \
  --vectors ../fixtures/vectors.json \
  ../examples/valid.ok
```
