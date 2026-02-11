# ADR 0001: Use Starlette and uvicorn as HTTP Framework

## Status
Accepted

## Date
2026-02-10

## Context

The HTTP adapter needs a framework to serve HTTP and WebSocket requests as a standalone server. The requirements are:

1. **HTTP and WebSocket Support**: The adapter intercepts both HTTP and WebSocket protocols
2. **Lightweight Dependencies**: As a testing library, minimizing transitive dependencies is important
3. **Concurrent Request Handling**: Record mode involves upstream I/O, and tests may run in parallel

## Decision

Use Starlette as the ASGI framework and uvicorn as the ASGI server.

The adapter class extends Starlette's application class, providing an ASGI-compatible application that can be served by uvicorn.

## Rationale

- **Unified Protocol Support**: HTTP and WebSocket handled through a single ASGI interface, avoiding fragmented APIs
- **Async-First Design**: Non-blocking I/O handles concurrent requests naturally, critical for record mode (upstream forwarding) and parallel test execution
- **Lightweight Footprint**: Only 5 transitive packages (starlette, uvicorn, anyio, sniffio, h11)
- **ASGI Standard**: Well-established standard with broad ecosystem support and interoperability

## Implications

### Positive

- Single framework covers both HTTP and WebSocket protocols
- Concurrent upstream forwarding in record mode without thread pool scaling
- Parallel test execution supported naturally via async event loop

### Concerns

- Adds runtime dependencies (~5 transitive packages), which increases footprint for a testing library (mitigation: all packages are lightweight and widely adopted)
- Async programming model adds complexity compared to synchronous alternatives (mitigation: async complexity is contained within the adapter; users interact via standard HTTP)

## Alternatives

### stdlib http.server

Using Python's built-in `http.server` module.

- **Pros**: Zero dependencies, simple API, proven reliability
- **Cons**: Synchronous (single-threaded by default), no WebSocket support, would require ThreadingMixIn for concurrency and a separate WebSocket library
- **Reason for rejection**: No WebSocket support and synchronous model would require significant workarounds for concurrent request handling

### Flask

Using Flask as a WSGI framework.

- **Pros**: Simple API, widely known, large ecosystem
- **Cons**: Synchronous WSGI, no native WebSocket support, would need extensions for async and WebSocket
- **Reason for rejection**: Same limitations as stdlib regarding synchronous model and WebSocket support

### aiohttp

Using aiohttp as both HTTP client and server.

- **Pros**: Async, supports both HTTP and WebSocket, can serve as HTTP client for upstream forwarding
- **Cons**: Heavier dependency footprint (multidict, yarl, frozenlist, aiosignal), more opinionated API
- **Reason for rejection**: Heavier dependencies without proportional benefit; ASGI standard provides better interoperability

## Future Direction

Revisit if dependency weight becomes a concern for users or if the ASGI ecosystem evolves significantly.

## References

- [Starlette Documentation](https://www.starlette.io/)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [uvicorn Documentation](https://www.uvicorn.org/)
