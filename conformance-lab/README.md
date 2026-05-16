# Conformance Lab

This directory exists to make the OK File Format look like it has an ecosystem.

It does not contain a second implementation because that would imply there are
interesting architectural choices. There are not. There are only three bytes and
the courage to compare them exactly.

Suggested lab exercise:

```sh
okfile \
  --format certificate \
  --ceremony \
  --rfc ../RFC-0001-OKFILE.md \
  --vectors ../fixtures/vectors.json \
  ../examples/valid.ok
```
