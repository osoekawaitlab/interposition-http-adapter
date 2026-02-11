# ADR 0003: Replay Miss HTTP Status Policy

## Status

Accepted

## Date

2026-02-11

## Context

In replay mode, the HTTP adapter may receive requests that do not match any interaction in the cassette. The adapter must map this replay miss to an HTTP response status.

If miss handling is ambiguous, tests can become hard to diagnose because it is unclear whether a response came from a valid recorded interaction or from fallback behavior.

## Decision

When no interaction matches during replay, the adapter returns HTTP `500 Internal Server Error`.

## Rationale

- **Fail-fast for test environments**: A replay miss usually indicates a recording gap or request-mapping mismatch, both of which should fail loudly.
- **Clearer diagnosis than `404`**: `404` can be confused with a legitimate recorded upstream response, while `500` signals adapter-level failure to satisfy replay.
- **Simple and deterministic behavior**: A single default policy avoids hidden fallback semantics during early development.

## Implications

### Positive Implications

- Missing or stale cassettes are detected immediately.
- CI failures point directly to replay configuration or recording completeness issues.
- Consumers can distinguish replay-system failures from domain-level `404` responses.

### Concerns

- Some consumers may expect miss behavior to mirror upstream `404` semantics (mitigation: document replay miss semantics clearly and provide assertion helpers in test code that treat `500` as cassette coverage failure)
- `500` may be too strict for exploratory or non-test usage (mitigation: keep current default for CI/test safety and revisit a configurable miss policy when non-test use cases become concrete)

## Alternatives

### Return `404 Not Found`

- **Pros**: Familiar REST-style response for missing resources.
- **Cons**: Blurs distinction between real recorded `404` and replay miss; can hide cassette gaps.
- **Reason for rejection**: Lower diagnostic value for replay correctness.

### Return `501 Not Implemented`

- **Pros**: Explicitly indicates unsupported behavior.
- **Cons**: Semantically intended for unimplemented server capabilities (for example, unsupported HTTP method), not missing replay data.
- **Reason for rejection**: Misleading status semantics.

### Configurable Policy (`500` / `404` / custom)

- **Pros**: Flexible across environments and use cases.
- **Cons**: More complexity and risk of inconsistent behavior across projects.
- **Reason for rejection**: Deferred until concrete multi-mode requirements emerge.

## Future Direction

- Revisit policy configurability if production-oriented replay workflows require softer miss handling.
- If configurability is introduced, define a safe default that preserves fail-fast behavior in test/CI contexts.

## References

- [HTTP Semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)
