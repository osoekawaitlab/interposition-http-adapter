"""Step implementations for HTTP replay server tests."""

import threading
import time

import httpx
import uvicorn
from getgauge.python import data_store, step
from interposition import (
    Broker,
    Cassette,
    Interaction,
    InteractionRequest,
    ResponseChunk,
)

from interposition_http_adapter import InterpositionHttpAdapter


@step("Create a GET cassette for <path> with status <status_code> and body <body>")
def create_cassette(path: str, status_code: str, body: str) -> None:
    """Create a cassette with a single GET interaction."""
    request = InteractionRequest(
        protocol="http",
        action="GET",
        target=path,
        headers=(),
        body=b"",
    )
    response_chunks = (
        ResponseChunk(
            data=body.encode(),
            sequence=0,
            metadata=(("status_code", status_code),),
        ),
    )
    interaction = Interaction(
        request=request,
        fingerprint=request.fingerprint(),
        response_chunks=response_chunks,
    )
    data_store.scenario["cassette"] = Cassette(interactions=(interaction,))


@step("Create a replay broker with the cassette")
def create_replay_broker() -> None:
    """Create a Broker in replay mode with the scenario cassette."""
    cassette = data_store.scenario["cassette"]
    assert isinstance(cassette, Cassette)
    data_store.scenario["broker"] = Broker(cassette=cassette, mode="replay")


@step("Create an HTTP adapter with the broker")
def create_http_adapter() -> None:
    """Create an InterpositionHttpAdapter with the scenario broker."""
    broker = data_store.scenario["broker"]
    assert isinstance(broker, Broker)
    data_store.scenario["adapter"] = InterpositionHttpAdapter(broker=broker)


@step("Start the adapter on port <port>")
def start_adapter(port: str) -> None:
    """Start the adapter as a real HTTP server in a background thread."""
    adapter = data_store.scenario["adapter"]
    assert isinstance(adapter, InterpositionHttpAdapter)
    config = uvicorn.Config(
        app=adapter, host="127.0.0.1", port=int(port), log_level="error"
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    data_store.scenario["server"] = server
    data_store.scenario["server_thread"] = thread
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)
    if not server.started:
        server.should_exit = True
        thread.join(timeout=5.0)
    assert server.started


@step("Send a GET request to <url>")
def send_get_request(url: str) -> None:
    """Send a GET request to the specified URL."""
    with httpx.Client() as client:
        response = client.get(url)
    data_store.scenario["response"] = response


@step("Verify that the response status code is <status_code>")
def verify_status_code(status_code: str) -> None:
    """Verify the HTTP response status code."""
    response = data_store.scenario["response"]
    assert isinstance(response, httpx.Response)
    assert response.status_code == int(status_code), (
        f"Expected status {status_code}, got {response.status_code}"
    )


@step("Verify that the response body is <body>")
def verify_response_body(body: str) -> None:
    """Verify the HTTP response body."""
    response = data_store.scenario["response"]
    assert isinstance(response, httpx.Response)
    assert response.text == body, f"Expected body '{body}', got '{response.text}'"


@step("Stop the adapter if running")
def stop_adapter_if_running() -> None:
    """Stop the running adapter server if it was started."""
    server = data_store.scenario.get("server")
    thread = data_store.scenario.get("server_thread")
    if isinstance(server, uvicorn.Server):
        server.should_exit = True
    if isinstance(thread, threading.Thread):
        thread.join(timeout=5.0)
