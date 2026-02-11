"""Tests for the HTTP adapter application."""

import pytest
from httpx import ASGITransport, AsyncClient, Response
from interposition import (
    Broker,
    Cassette,
    Interaction,
    InteractionRequest,
    ResponseChunk,
)

from interposition_http_adapter import InterpositionHttpAdapter

HTTP_OK = 200
HTTP_INTERNAL_SERVER_ERROR = 500


def _create_replay_broker(
    method: str,
    target: str,
    status_code: int,
    body: bytes,
    headers: tuple[tuple[str, str], ...] = (),
) -> Broker:
    """Create a Broker in replay mode with a single interaction."""
    request = InteractionRequest(
        protocol="http",
        action=method,
        target=target,
        headers=headers,
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


async def _send_get(
    adapter: InterpositionHttpAdapter,
    path: str,
    headers: dict[str, str] | None = None,
) -> Response:
    transport = ASGITransport(app=adapter)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path, headers=headers)


@pytest.mark.anyio
async def test_get_request_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching GET request."""
    expected_status = 200
    expected_body = b"hello"
    broker = _create_replay_broker("GET", "/api/data", expected_status, expected_body)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_get(adapter, "/api/data")

    assert response.status_code == expected_status
    assert response.content == expected_body


@pytest.mark.anyio
async def test_get_request_not_in_cassette_returns_500() -> None:
    """Adapter returns 500 for a GET request not found in the Cassette."""
    broker = _create_replay_broker("GET", "/api/data", 200, b"hello")
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_get(adapter, "/api/unknown")

    assert response.status_code == HTTP_INTERNAL_SERVER_ERROR


@pytest.mark.anyio
async def test_get_request_uses_recorded_header_fields_for_matching() -> None:
    """Adapter matches using the header fields recorded in the interaction."""
    broker = _create_replay_broker(
        method="GET",
        target="/api/data",
        status_code=200,
        body=b"hello",
        headers=(("x-role", "admin"),),
    )
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_get(
        adapter,
        "/api/data",
        headers={"x-role": "admin", "x-ignored": "anything"},
    )

    assert response.status_code == HTTP_OK
    assert response.content == b"hello"


@pytest.mark.anyio
async def test_get_request_query_string_is_part_of_matching_target() -> None:
    """Adapter includes query string in target matching."""
    broker = _create_replay_broker(
        method="GET",
        target="/api/data?kind=user",
        status_code=200,
        body=b"hello-query",
    )
    adapter = InterpositionHttpAdapter(broker=broker)

    matched = await _send_get(adapter, "/api/data?kind=user")
    not_matched = await _send_get(adapter, "/api/data?kind=admin")

    assert matched.status_code == HTTP_OK
    assert matched.content == b"hello-query"
    assert not_matched.status_code == HTTP_INTERNAL_SERVER_ERROR
