"""HTTP adapter application for Interposition."""

from collections.abc import Awaitable, Callable

from interposition import Broker, InteractionNotFoundError, InteractionRequest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


def _create_get_handler(
    broker: Broker,
) -> Callable[[Request], Awaitable[Response]]:
    """Create a GET request handler bound to the given broker."""

    async def handle_get(request: Request) -> Response:
        interaction_request = InteractionRequest(
            protocol="http",
            action="GET",
            target=request.url.path,
            headers=(),
            body=b"",
        )
        try:
            chunks = list(broker.replay(interaction_request))
        except InteractionNotFoundError:
            return Response(status_code=404, content=b"Not Found")

        status_code = 200
        if chunks:
            for key, value in chunks[0].metadata:
                if key == "status_code":
                    status_code = int(value)

        body = b"".join(chunk.data for chunk in chunks)
        return Response(status_code=status_code, content=body)

    return handle_get


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
