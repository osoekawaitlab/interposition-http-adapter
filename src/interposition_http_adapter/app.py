"""HTTP adapter application for Interposition."""

from collections.abc import Awaitable, Callable

from interposition import (
    Broker,
    Interaction,
    InteractionNotFoundError,
    InteractionRequest,
    ResponseChunk,
)
from starlette.applications import Starlette
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


def _create_get_handler(
    broker: Broker,
) -> Callable[[Request], Awaitable[Response]]:
    """Create a GET request handler bound to the given broker."""

    async def handle_get(request: Request) -> Response:
        target = request.url.path
        if request.url.query:
            target = f"{target}?{request.url.query}"

        body = await request.body()
        chunks = _replay_matching_get(
            broker=broker,
            request_headers=request.headers,
            target=target,
            body=body,
        )
        if chunks is None:
            return Response(status_code=500, content=b"Interaction Not Found")

        status_code = 200
        if chunks:
            for key, value in chunks[0].metadata:
                if key == "status_code":
                    status_code = int(value)

        response_body = b"".join(chunk.data for chunk in chunks)
        return Response(status_code=status_code, content=response_body)

    return handle_get


def _replay_matching_get(
    broker: Broker,
    request_headers: Headers,
    target: str,
    body: bytes,
) -> tuple[ResponseChunk, ...] | None:
    """Try replay candidates built from stored interaction header schemas."""
    candidates = _build_get_replay_candidates(
        interactions=broker.cassette.interactions,
        request_headers=request_headers,
        target=target,
        body=body,
    )
    for candidate in candidates:
        try:
            return tuple(broker.replay(candidate))
        except InteractionNotFoundError:
            continue
    return None


def _build_get_replay_candidates(
    interactions: tuple[Interaction, ...],
    request_headers: Headers,
    target: str,
    body: bytes,
) -> tuple[InteractionRequest, ...]:
    """Create candidate requests using the stored header fields per interaction."""
    candidates: list[InteractionRequest] = []
    seen_fingerprints: set[str] = set()

    for interaction in interactions:
        recorded_request = interaction.request
        if recorded_request.protocol != "http":
            continue
        if recorded_request.action != "GET":
            continue
        if recorded_request.target != target:
            continue

        candidate_headers: list[tuple[str, str]] = []
        missing_header = False
        for key, _ in recorded_request.headers:
            value = request_headers.get(key)
            if value is None:
                missing_header = True
                break
            candidate_headers.append((key, value))

        if missing_header:
            continue

        candidate = InteractionRequest(
            protocol="http",
            action="GET",
            target=target,
            headers=tuple(candidate_headers),
            body=body,
        )
        candidate_fingerprint = candidate.fingerprint().value
        if candidate_fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(candidate_fingerprint)
        candidates.append(candidate)

    if not candidates:
        candidates.append(
            InteractionRequest(
                protocol="http",
                action="GET",
                target=target,
                headers=(),
                body=body,
            )
        )

    return tuple(candidates)


class InterpositionHttpAdapter(Starlette):
    """ASGI application that replays HTTP interactions via an Interposition Broker."""

    def __init__(self, broker: Broker) -> None:
        """Initialize the adapter with a Broker.

        Args:
            broker: The Interposition Broker to use for replaying interactions.
        """
        self._broker = broker
        routes = [
            Route("/{path:path}", _create_get_handler(broker), methods=["GET"]),
        ]
        super().__init__(routes=routes)
