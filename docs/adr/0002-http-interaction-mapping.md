# ADR 0002: HTTP to InteractionRequest Mapping Conventions

## Status

Accepted

## Date

2026-02-11

## Context

The HTTP adapter translates between HTTP requests/responses and Interposition's protocol-agnostic data model (`InteractionRequest` and `ResponseChunk`). A consistent mapping convention is needed so that recorded interactions are correctly matched during replay.

Interposition provides the following fields for request representation:

- `protocol`: Protocol identifier
- `action`: Action or method name
- `target`: Target resource
- `headers`: Key-value pairs
- `body`: Raw bytes

For responses, `ResponseChunk` provides:

- `data`: Chunk payload
- `sequence`: Chunk ordering
- `metadata`: Key-value pairs for protocol-specific information

## Decision

### Request Mapping

Map HTTP requests to `InteractionRequest` as follows:

- `protocol` = `"http"`
- `action` = HTTP method (e.g., `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`)
- `target` = Request path with query string when present (e.g., `"/api/data?kind=user"`)
- `headers` = HTTP request headers as tuple of key-value pairs
- `body` = Request body bytes

Matching policy for which headers participate in fingerprinting is intentionally adapter-specific and may be derived from recorded interaction schemas rather than fixed global allow/deny lists.

### Response Mapping

Encode HTTP response information across `ResponseChunk` instances:

- **First chunk (sequence=0)**: `metadata` contains status code as `("status_code", "<code>")` (e.g., `("status_code", "200")`). Response headers are reserved for future definition.
- **All chunks**: `data` contains a segment of the response body.

This mirrors HTTP's own structure where status code and headers are sent once at the beginning, followed by body data which may arrive in multiple chunks.

## Rationale

- **Direct Mapping**: HTTP concepts map naturally to Interposition's fields without lossy transformations
- **Replay Correctness for Query-driven APIs**: Including query string in `target` avoids collisions between requests that share a path but differ by query
- **User-defined Header Participation**: Reusing recorded header keys lets cassette authors control which headers influence matching, instead of imposing adapter-side allow/deny lists
- **Metadata for Response Attributes**: Status code and response headers are protocol-specific and don't have dedicated fields in `ResponseChunk`, so metadata is the appropriate storage
- **First-Chunk Convention**: Placing status code only in the first chunk matches HTTP semantics where status and headers precede the body

## Implications

### Positive

- Consistent fingerprinting enables reliable request matching across environments
- Clear separation between request matching fields and response metadata
- Query string-sensitive APIs can be replayed without extra adapter configuration
- Header matching policy can be chosen per adapter/use case while keeping a consistent data model
- Chunked responses are represented naturally

### Concerns

- If recorded interactions include volatile headers, replay may fail unless those values are reproduced by clients (mitigation: curate recorded headers at capture time)
- Status code stored as string in metadata requires parsing (mitigation: simple `int()` conversion, validated at recording time)

## Alternatives

### Full URL as Target

Using the complete URL (including scheme, host, port) as the `target` field.

- **Pros**: Preserves full request context
- **Cons**: Fingerprints would differ between environments (localhost:8080 vs production host), breaking replay portability
- **Reason for rejection**: Environment-dependent fingerprints would make cassettes non-portable

### Dedicated Response Model

Creating a custom response model instead of using `ResponseChunk.metadata`.

- **Pros**: Type-safe, explicit fields for status code and headers
- **Cons**: Breaks compatibility with Interposition's data model, requires custom serialization
- **Reason for rejection**: Working within Interposition's existing model is simpler and maintains compatibility

### Status Code in Every Chunk

Storing the status code in every `ResponseChunk`'s metadata for redundancy.

- **Pros**: Any chunk can be interpreted independently
- **Cons**: Redundant data, diverges from HTTP semantics, risk of inconsistency between chunks
- **Reason for rejection**: HTTP sends status code once; the mapping should reflect this

## Future Direction

- Define response header encoding convention when response header matching is needed
- Standardize optional canonicalization and filtering profiles for headers and bodies (for example, stable JSON serialization and removal of volatile fields) for common use cases

## References

- [Interposition data model documentation](https://osoekawaitlab.github.io/interposition/api/api_reference/)
