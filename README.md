# interposition-http-adapter

HTTP adapter for [Interposition](https://github.com/osoekawaitlab/interposition).
Serves recorded HTTP interactions from an Interposition `Cassette` as a real HTTP server, allowing you to replay captured API responses for testing and development.

## Installation

```bash
pip install interposition-http-adapter
```

## Usage

`InterpositionHttpAdapter` is an ASGI application (based on Starlette) that replays HTTP interactions through an Interposition `Broker`.

```python
from interposition import (
    Broker,
    Cassette,
    Interaction,
    InteractionRequest,
    ResponseChunk,
)
import uvicorn

from interposition_http_adapter import InterpositionHttpAdapter

# 1. Build an InteractionRequest describing the HTTP request to match
request = InteractionRequest(
    protocol="http",
    action="GET",
    target="/api/data",
    headers=(),
    body=b"",
)

# 2. Build ResponseChunks with status_code in the first chunk's metadata
response_chunks = (
    ResponseChunk(
        data=b'{"message": "hello"}',
        sequence=0,
        metadata=(("status_code", "200"),),
    ),
)

# 3. Create a Cassette containing the interaction
interaction = Interaction(
    request=request,
    fingerprint=request.fingerprint(),
    response_chunks=response_chunks,
)
cassette = Cassette(interactions=(interaction,))

# 4. Create a Broker in replay mode
broker = Broker(cassette=cassette, mode="replay")

# 5. Create the adapter and serve it
app = InterpositionHttpAdapter(broker=broker)
uvicorn.run(app, host="127.0.0.1", port=8000)
```

Once the server is running, a `GET` request to `http://127.0.0.1:8000/api/data` returns the recorded response with status code 200 and body `{"message": "hello"}`.
The adapter supports all standard HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS). Requests that do not match any recorded interaction return a `500 Internal Server Error` response.

## API Reference

Detailed documentation is available in MkDocs: <https://osoekawaitlab.github.io/interposition-http-adapter/>.

## CLI

The package provides a command-line interface:

```bash
interposition_http_adapter --version
```

## License

MIT
