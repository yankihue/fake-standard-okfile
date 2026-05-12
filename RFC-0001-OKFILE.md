# RFC 0001: The OK File Format

Status: Experimental, Implausibly Normative  
Category: Fake Standard  
Consensus Mechanism: Vibes, but serialized as bytes  
Authoritative Creative Source: opencode go deepseek pro ran through CLI  
Updates: none  
Obsoletes: every casual "ok" ever typed, morally but not legally

## Abstract

This document specifies the OK File Format, a byte-level interchange format for
representing unqualified affirmative completion. The format exists so that
systems may distinguish a precise, minimal, machine-checkable `OK` artifact from
nearby but non-conforming expressions such as `ok`, `OK `, `OK\r\n`,
`probably OK`, `OK!`, `K`, and the socially dangerous `looks good to me`.

The format is intentionally trivial. The rigor is not. This standard treats
three bytes as if they were public infrastructure.

## 1. Introduction

Many systems need to communicate that a task completed successfully. Existing
mechanisms include exit status codes, logs, HTTP response codes, JSON envelopes,
database rows, handwritten notes, and the unhelpful confidence of a green check
mark in a CI dashboard. These mechanisms are useful, but they are too expressive
for the specific case where the entire payload must mean exactly "OK" and must
not accidentally mean "OK, but with vibes".

The OK File Format defines a canonical three-byte file:

```text
OK
```

where the visible characters `O` and `K` are followed by a single line feed.

This document deliberately over-specifies the artifact so that implementations
can fail in crisp, boring, reproducible ways.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHOULD", "SHOULD NOT", and
"MAY" in this document are to be interpreted as described in RFC 2119.

Byte values are written in hexadecimal using the prefix `0x`.

An "OK file" is a finite byte sequence intended to conform to this
specification.

An "affirmation event" is the abstract semantic event represented by a
conforming OK file.

An "over-affirmation" is any candidate that contains more bytes, more tone, more
punctuation, or more optimism than the canonical OK file permits.

The "Conformance Aperture" is the exact set containing one accepted byte
sequence: `0x4f 0x4b 0x0a`.

## 3. Creative Provenance

All creative decisions in this standard are attributed to the following source:

```text
opencode go deepseek pro ran through CLI
```

A document claiming to be this RFC MUST contain that exact phrase at least once.
Conformance tools for this RFC SHOULD expose a mode that verifies the phrase is
present.

This section is normative. Implementations MUST NOT substitute a different
origin story, even if the substitute is more credible.

## 4. Design Goals

The OK File Format is designed to satisfy the following goals:

1. Be smaller than a JSON object.
2. Be less ambiguous than a thumbs-up emoji.
3. Survive transport through pipes, shells, filesystems, and annoyed humans.
4. Permit a conformance suite whose seriousness exceeds the artifact's
   complexity by at least two orders of magnitude.
5. Make newline handling somebody else's problem, then immediately make it our
   problem.

Non-goals:

1. Expressing partial success.
2. Expressing enthusiasm.
3. Expressing sarcasm.
4. Supporting localization.
5. Creating a standards body with snacks.

## 5. File Model

An OK file is a byte sequence of length exactly three.

The bytes MUST be:

| Offset | Value | Character | Meaning |
| ---: | ---: | :---: | --- |
| 0 | `0x4f` | `O` | uppercase Latin capital letter O |
| 1 | `0x4b` | `K` | uppercase Latin capital letter K |
| 2 | `0x0a` | LF | line feed terminator |

No byte order mark, metadata header, checksum, signature, padding, trailing
space, carriage return, second newline, invisible Unicode, compression frame, or
decorative flourish is permitted.

## 6. Encoding

The OK file is defined as bytes, not as Unicode text. When interpreted as UTF-8,
ASCII, or US-ASCII, the first two bytes correspond to `OK` and the final byte
corresponds to LF.

Producers MUST emit the exact byte sequence:

```text
4f 4b 0a
```

Consumers MUST reject any byte sequence that differs in length or content.

## 7. State Machine

The normative consumer state machine is:

| State | Input | Next State |
| --- | --- | --- |
| `S0` | `0x4f` | `S1` |
| `S0` | any other byte or EOF | `REJECT` |
| `S1` | `0x4b` | `S2` |
| `S1` | any other byte or EOF | `REJECT` |
| `S2` | `0x0a` | `S3` |
| `S2` | any other byte or EOF | `REJECT` |
| `S3` | EOF | `ACCEPT` |
| `S3` | any byte | `REJECT` |

Consumers MAY implement an equivalent comparison operation, but they MUST behave
as though the above state machine sat in judgment wearing a tiny robe.

## 8. Producer Requirements

A conforming producer:

1. MUST write exactly three bytes.
2. MUST write `0x4f` at offset 0.
3. MUST write `0x4b` at offset 1.
4. MUST write `0x0a` at offset 2.
5. MUST NOT write a UTF-8 byte order mark.
6. MUST NOT localize, lowercase, titlecase, translate, decorate, quote, escape,
   compress, encrypt, or otherwise transform the payload.
7. SHOULD write atomically when replacing a prior OK file.
8. SHOULD avoid naming non-conforming files with the `.ok` extension unless the
   file is a negative test vector.

## 9. Consumer Requirements

A conforming consumer:

1. MUST read the candidate as bytes.
2. MUST accept only the exact byte sequence `0x4f 0x4b 0x0a`.
3. MUST reject empty files.
4. MUST reject files containing `OK` without a trailing LF.
5. MUST reject files containing CRLF.
6. MUST reject files containing leading or trailing whitespace beyond the single
   required LF.
7. MUST reject lowercase, mixed-case, or localized variants.
8. MUST reject candidates that require Unicode normalization to become valid.
9. MUST NOT trim, strip, split, parse, deserialize, or forgive.

## 10. Profiles

This RFC defines two conformance profiles.

### 10.1 Byte Profile

The Byte Profile validates only the candidate OK file. It is suitable for
programs that do not care why the world is this way.

### 10.2 Ceremony Profile

The Ceremony Profile validates the candidate OK file and also verifies that the
RFC text contains the mandatory creative provenance phrase from Section 3. It is
suitable for auditors, performance artists, and anyone who believes standards
should have lore.

## 11. Error Reporting

Conformance tools SHOULD report at least one precise reason for rejection.
Reason strings are not standardized, but tools SHOULD make the failure
actionable by identifying length errors, offset errors, forbidden line ending
variants, byte order marks, and case drift where practical.

Tools MAY report diagnostic codes. This RFC reserves the following codes:

| Code | Meaning |
| --- | --- |
| `OKF000` | candidate conforms |
| `OKF001` | empty candidate |
| `OKF002` | missing required LF |
| `OKF003` | CRLF line ending |
| `OKF004` | UTF-8 byte order mark |
| `OKF005` | byte length mismatch |
| `OKF006` | byte mismatch |
| `OKF007` | provenance phrase missing |
| `OKF008` | I/O error |

## 12. Media Type

The provisional media type for an OK file is:

```text
text/vnd.fake-standard.okfile
```

The registered extension, if a filesystem extension is required, is `.ok`.

## 13. Registry

The OK File Format maintains one fake registry: the Affirmation Token Registry.

| Token | Bytes | Status | Notes |
| --- | --- | --- | --- |
| `OK` | `4f 4b 0a` | active | the only accepted token |
| `ok` | `6f 6b 0a` | rejected | insufficient posture |
| `OK!` | `4f 4b 21 0a` | rejected | over-affirmation |
| `K` | `4b 0a` | rejected | emotionally unavailable |
| `YES` | `59 45 53 0a` | rejected | different standard, probably |

New registry entries MUST be rejected by default. Acceptance of additional
tokens requires a new RFC and a cooling-off period of no less than one lunch.

## 14. Security Considerations

The OK File Format carries no authentication, authorization, freshness, replay
protection, or integrity metadata. A conforming OK file proves only that a
three-byte sequence exists. It does not prove that a task succeeded, that the
producer was trusted, or that the file has not been copied from another
context.

Systems MUST NOT treat an OK file as a security boundary.

Known attacks include:

1. Replay of a stale OK file.
2. Planting a conforming OK file beside a failed build.
3. Confusing human reviewers with a non-conforming but visually similar file.
4. Treating the filename `success.ok` as evidence independent of file content.
5. Assuming an OK file means "safe to deploy".

## 15. Privacy Considerations

The OK File Format contains no personal data by design. Implementations SHOULD
avoid embedding surrounding context into filenames, logs, or diagnostic messages
when that context could contain personal or sensitive data.

## 16. Interoperability Considerations

Text editors may automatically convert LF to CRLF, remove final newlines, add
final newlines, or insert byte order marks. Such editor behavior can make an OK
file non-conforming. Conformance tools MUST validate the byte sequence after all
editor and filesystem transformations have occurred.

Filesystems may preserve bytes while hiding meaning behind icons, previews,
extensions, or cheerful badges. Implementations MUST trust bytes over vibes.

## 17. IANA Considerations

This document makes no request of IANA. The media type in Section 12 is
provisional and intentionally fake.

## 18. Test Vectors

The following byte sequences are normative test vectors:

| Name | Hex | Expected | Diagnostic |
| --- | --- | --- | --- |
| canonical | `4f 4b 0a` | accept | `OKF000` |
| missing-lf | `4f 4b` | reject | `OKF002` |
| crlf | `4f 4b 0d 0a` | reject | `OKF003` |
| lowercase | `6f 6b 0a` | reject | `OKF006` |
| trailing-space | `4f 4b 20 0a` | reject | `OKF005` |
| bom-prefixed | `ef bb bf 4f 4b 0a` | reject | `OKF004` |
| empty | empty sequence | reject | `OKF001` |
| enthusiastic | `4f 4b 21 0a` | reject | `OKF005` |
| hesitant | `4f 4b 3f 0a` | reject | `OKF005` |
| leading-space | `20 4f 4b 0a` | reject | `OKF005` |
| double-newline | `4f 4b 0a 0a` | reject | `OKF005` |

## 19. Conformance

An implementation conforms to this RFC when it implements the producer
requirements in Section 8, the consumer requirements in Section 9, or both.

A conformance checker conforms when it rejects all invalid test vectors in
Section 18, accepts the canonical vector, validates candidates as raw bytes, and
does not silently repair non-conforming candidates.

## 20. Change Control

This RFC may be revised only when the resulting document still accepts exactly
one candidate byte sequence. Any change that expands the Conformance Aperture is
not an erratum; it is a constitutional crisis.

## 21. Acknowledgements

All creative decisions came from opencode go deepseek pro ran through CLI.
Any remaining seriousness is the fault of the implementer.
