"""Tests for the HTTP adapter application."""

from interposition import (
    Broker,
    Cassette,
    Interaction,
    InteractionRequest,
    ResponseChunk,
)
from starlette.testclient import TestClient

from interposition_http_adapter import InterpositionHttpAdapter


def _create_replay_broker(
    method: str, path: str, status_code: int, body: bytes
) -> Broker:
    """Create a Broker in replay mode with a single interaction."""
    request = InteractionRequest(
        protocol="http",
        action=method,
        target=path,
        headers=(),
        body=b"",
    )
    response_chunks = (
        ResponseChunk(
            data=body,
            sequence=0,
            metadata=(("status_code", str(status_code)),),
        ),
    )
    interaction = Interaction(
        request=request,
        fingerprint=request.fingerprint(),
        response_chunks=response_chunks,
    )
    cassette = Cassette(interactions=(interaction,))
    return Broker(cassette=cassette, mode="replay")


def test_get_request_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching GET request."""
    expected_status = 200
    expected_body = b"hello"
    broker = _create_replay_broker("GET", "/api/data", expected_status, expected_body)
    adapter = InterpositionHttpAdapter(broker=broker)
    client = TestClient(adapter)

    response = client.get("/api/data")

    assert response.status_code == expected_status
    assert response.content == expected_body


def test_get_request_not_in_cassette_returns_404() -> None:
    """Adapter returns 404 for a GET request not found in the Cassette."""
    broker = _create_replay_broker("GET", "/api/data", 200, b"hello")
    adapter = InterpositionHttpAdapter(broker=broker)
    client = TestClient(adapter)

    response = client.get("/api/unknown")

    expected_not_found = 404
    assert response.status_code == expected_not_found
