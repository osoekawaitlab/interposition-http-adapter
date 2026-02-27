# ADR 0004: Factory Class Methods for Adapter Creation

## Status

Accepted (Amended 2026-02-26)

## Date

2026-02-24

## Context

Creating an adapter requires assembling multiple interposition objects:

1. **Boilerplate assembly**: Constructing a store, creating a Broker, and passing it to the adapter involves three separate objects and their wiring
2. **Common use case**: In testing workflows, cassettes are frequently swapped per test case, making this assembly code repetitive
3. **Multiple modes**: The Broker supports replay, record, and auto modes, all of which benefit from simplified construction
4. **Two abstraction levels**: Some users work directly with file paths (the most common case), while others need the flexibility of custom store implementations

## Decision

Provide two layered factory class methods on the adapter:

1. **from_store**: Accepts any CassetteStore implementation. This is the general-purpose factory that mirrors the interposition library's own Broker.from_store pattern.
2. **from_cassette_file**: Accepts a file path (str or Path). This is a convenience method built on top of from_store that covers the most common use case. It internally creates a JsonFileCassetteStore and delegates to from_store.

The initial implementation supports replay mode, with record and auto modes to follow as the Broker mode parameter is exposed.

## Rationale

- **Reduced boilerplate**: A single call replaces three-step manual assembly (store, broker, adapter)
- **Leverages upstream API**: Uses the Broker's own store-based factory method rather than reimplementing load-and-wire logic
- **Layered design**: from_store provides generality for custom stores, from_cassette_file provides convenience for the dominant file-based use case
- **Familiar pattern**: Class method factories are idiomatic in Python and immediately discoverable via the class interface
- **Type flexibility**: from_cassette_file accepts both str and Path, avoiding forcing callers to wrap paths

## Implications

### Positive

- Test setup code is significantly shorter for both file-based and custom-store use cases
- Error propagation is straightforward: store-level errors (missing file, invalid JSON) surface directly to the caller
- Custom store implementations can be used via from_store without needing to construct a Broker manually
- No new dependencies introduced; uses existing interposition store and Broker APIs

### Concerns

- Only supports JSON file format through the underlying store (mitigation: additional file formats can be supported by adding new factory methods or parameters in the future)
- Initial implementation only supports replay mode (mitigation: the method signature will be extended with a mode parameter to support record and auto modes; replay-only is a deliberate incremental step)

## Alternatives

### File-path Factory Only

Providing only from_cassette_file without from_store, requiring users who need custom stores to construct a Broker manually.

- **Pros**: Simpler API surface with a single factory method
- **Cons**: Forces custom-store users to understand Broker construction, misses the opportunity to mirror the upstream API's layered design
- **Reason for rejection**: The additional cost of from_store is minimal (a thin wrapper over Broker.from_store), and it provides a natural extension point for users with custom store implementations

### Standalone Function

A module-level function (e.g., `create_adapter_from_file()`) instead of a class method.

- **Pros**: Simpler to test in isolation, no class coupling
- **Cons**: Less discoverable, requires users to know about a separate function, does not follow the common Python factory pattern
- **Reason for rejection**: A class method is more discoverable and keeps the creation API co-located with the class it creates

## Future Direction

The factory method will be extended to accept a mode parameter (replay, record, auto) and, for record and auto modes, a live responder. This allows the same file-based entry point to cover all Broker modes while keeping the common replay case simple with sensible defaults.

## References

- [interposition JsonFileCassetteStore](https://github.com/osoekawaitlab/interposition)
- [Python Factory Method Pattern](https://docs.python.org/3/library/functions.html#classmethod)

## Amendment (2026-02-26)

### What Changed

The original ADR described factory methods supporting only replay mode, with record and auto modes as a future extension.

- **Original**: Factory methods only support replay mode
- **Amended to**: Factory methods accept a mode parameter (replay, record, auto) and a live_responder parameter

The core design of two layered factory methods (from_store and from_cassette_file) remains unchanged. Only the parameter surface has been extended.

### Reason for Amendment

The interposition library's Broker already supports replay, record, and auto modes. Requiring users to bypass the factory methods and manually construct a Broker to use these modes defeats the purpose of the convenience API. Exposing the mode and live_responder parameters through the factory methods completes the planned extension described in the original Future Direction section.

### Impact on Original ADR

**Unchanged:**

- Two layered factory methods (from_store and from_cassette_file)
- from_cassette_file delegates to from_store
- Default mode is replay (backward compatible)
- Error propagation from the underlying store and Broker

**Changed:**

- Both factory methods now accept a mode parameter (default: replay)
- Both factory methods now accept a live_responder parameter for record and auto modes
- Validation of mode and live_responder is delegated to the interposition library's Broker, keeping the adapter as a thin pass-through
