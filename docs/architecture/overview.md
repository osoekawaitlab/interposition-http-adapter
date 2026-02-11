# Architecture Overview

This document provides a high-level overview of architectural decisions made for the interposition-http-adapter project.

## Architecture Decision Records

### [ADR-0001: Use Starlette and uvicorn as HTTP Framework](../adr/0001-http-framework-selection.md)

**Status**: Accepted | **Date**: 2026-02-10

Use Starlette as the ASGI framework and uvicorn as the ASGI server for unified HTTP and WebSocket support with lightweight dependencies.

---

### [ADR-0002: HTTP to InteractionRequest Mapping Conventions](../adr/0002-http-interaction-mapping.md)

**Status**: Accepted | **Date**: 2026-02-10

Define conventions for mapping HTTP requests to InteractionRequest and ResponseChunk to HTTP responses, with status code in the first chunk's metadata.

---
