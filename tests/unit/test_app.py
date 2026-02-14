"""Tests for the HTTP adapter application."""

from dataclasses import dataclass

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
HTTP_CREATED = 201
HTTP_INTERNAL_SERVER_ERROR = 500


@dataclass(frozen=True)
class ReplaySpec:
    """Specification for creating a replay broker.

    Bundles the parameters for ``_create_replay_broker`` into a single
    object to stay within the PLR0913 argument-count limit.
    """

    method: str
    target: str
    status_code: int
    response_body: bytes
    headers: tuple[tuple[str, str], ...] = ()
    request_body: bytes = b""


def _create_replay_broker(spec: ReplaySpec) -> Broker:
    """Create a Broker in replay mode with a single interaction."""
    request = InteractionRequest(
        protocol="http",
        action=spec.method,
        target=spec.target,
        headers=spec.headers,
        body=spec.request_body,
    )
    response_chunks = (
        ResponseChunk(
            data=spec.response_body,
            sequence=0,
            metadata=(("status_code", str(spec.status_code)),),
        ),
    )
    interaction = Interaction(
        request=request,
        fingerprint=request.fingerprint(),
        response_chunks=response_chunks,
    )
    cassette = Cassette(interactions=(interaction,))
    return Broker(cassette=cassette, mode="replay")


async def _send_request(
    adapter: InterpositionHttpAdapter,
    method: str,
    path: str,
    body: bytes = b"",
    headers: dict[str, str] | None = None,
) -> Response:
    transport = ASGITransport(app=adapter)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.request(method, path, content=body, headers=headers)


@pytest.mark.anyio
async def test_get_request_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching GET request."""
    expected_status = HTTP_OK
    expected_body = b"hello"
    spec = ReplaySpec(
        method="GET",
        target="/api/data",
        status_code=expected_status,
        response_body=expected_body,
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "GET", "/api/data")

    assert response.status_code == expected_status
    assert response.content == expected_body


@pytest.mark.anyio
async def test_get_request_not_in_cassette_returns_500() -> None:
    """Adapter returns 500 for a GET request not found in the Cassette."""
    spec = ReplaySpec(
        method="GET",
        target="/api/data",
        status_code=HTTP_OK,
        response_body=b"hello",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "GET", "/api/unknown")

    assert response.status_code == HTTP_INTERNAL_SERVER_ERROR


@pytest.mark.anyio
async def test_get_request_uses_recorded_header_fields_for_matching() -> None:
    """Adapter matches using the header fields recorded in the interaction."""
    spec = ReplaySpec(
        method="GET",
        target="/api/data",
        status_code=HTTP_OK,
        response_body=b"hello",
        headers=(("x-role", "admin"),),
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(
        adapter,
        "GET",
        "/api/data",
        headers={"x-role": "admin", "x-ignored": "anything"},
    )

    assert response.status_code == HTTP_OK
    assert response.content == b"hello"


@pytest.mark.anyio
async def test_get_request_query_string_is_part_of_matching_target() -> None:
    """Adapter includes query string in target matching."""
    spec = ReplaySpec(
        method="GET",
        target="/api/data?kind=user",
        status_code=HTTP_OK,
        response_body=b"hello-query",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    matched = await _send_request(adapter, "GET", "/api/data?kind=user")
    not_matched = await _send_request(adapter, "GET", "/api/data?kind=admin")

    assert matched.status_code == HTTP_OK
    assert matched.content == b"hello-query"
    assert not_matched.status_code == HTTP_INTERNAL_SERVER_ERROR


@pytest.mark.anyio
async def test_post_request_with_body_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching POST request with body."""
    spec = ReplaySpec(
        method="POST",
        target="/api/data",
        status_code=HTTP_CREATED,
        response_body=b"created",
        request_body=b"req-body",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "POST", "/api/data", body=b"req-body")

    assert response.status_code == HTTP_CREATED
    assert response.content == b"created"


@pytest.mark.anyio
async def test_put_request_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching PUT request."""
    spec = ReplaySpec(
        method="PUT",
        target="/api/items/1",
        status_code=HTTP_OK,
        response_body=b"updated",
        request_body=b"update-data",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "PUT", "/api/items/1", body=b"update-data")

    assert response.status_code == HTTP_OK
    assert response.content == b"updated"


HTTP_NO_CONTENT = 204


@pytest.mark.anyio
async def test_delete_request_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching DELETE request."""
    spec = ReplaySpec(
        method="DELETE",
        target="/api/items/1",
        status_code=HTTP_NO_CONTENT,
        response_body=b"",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "DELETE", "/api/items/1")

    assert response.status_code == HTTP_NO_CONTENT


@pytest.mark.anyio
async def test_patch_request_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching PATCH request."""
    spec = ReplaySpec(
        method="PATCH",
        target="/api/items/1",
        status_code=HTTP_OK,
        response_body=b"patched",
        request_body=b"patch-data",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "PATCH", "/api/items/1", body=b"patch-data")

    assert response.status_code == HTTP_OK
    assert response.content == b"patched"


@pytest.mark.anyio
async def test_head_request_returns_recorded_response() -> None:
    """Adapter returns the recorded status code for a matching HEAD request."""
    spec = ReplaySpec(
        method="HEAD",
        target="/api/health",
        status_code=HTTP_OK,
        response_body=b"",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "HEAD", "/api/health")

    assert response.status_code == HTTP_OK


@pytest.mark.anyio
async def test_options_request_returns_recorded_response() -> None:
    """Adapter returns the recorded response for a matching OPTIONS request."""
    spec = ReplaySpec(
        method="OPTIONS",
        target="/api/data",
        status_code=HTTP_NO_CONTENT,
        response_body=b"",
    )
    broker = _create_replay_broker(spec)
    adapter = InterpositionHttpAdapter(broker=broker)

    response = await _send_request(adapter, "OPTIONS", "/api/data")

    assert response.status_code == HTTP_NO_CONTENT
