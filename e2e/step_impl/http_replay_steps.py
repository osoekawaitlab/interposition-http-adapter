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


@step(
    "Create a cassette for <method> method on <path> with request body <request_body> and status <status_code> and response body <response_body>"  # noqa: E501
)
def create_method_cassette(
    method: str,
    path: str,
    request_body: str,
    status_code: str,
    response_body: str,
) -> None:
    """Create a cassette with a single interaction for the given HTTP method."""
    request = InteractionRequest(
        protocol="http",
        action=method,
        target=path,
        headers=(),
        body=request_body.encode(),
    )
    response_chunks = (
        ResponseChunk(
            data=response_body.encode(),
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


@step("Send a POST request to <url> with body <body>")
def send_post_request(url: str, body: str) -> None:
    """Send a POST request to the specified URL with the given body."""
    with httpx.Client() as client:
        response = client.post(url, content=body.encode())
    data_store.scenario["response"] = response


@step("Send a PUT request to <url> with body <body>")
def send_put_request(url: str, body: str) -> None:
    """Send a PUT request to the specified URL with the given body."""
    with httpx.Client() as client:
        response = client.put(url, content=body.encode())
    data_store.scenario["response"] = response


@step("Send a PATCH request to <url> with body <body>")
def send_patch_request(url: str, body: str) -> None:
    """Send a PATCH request to the specified URL with the given body."""
    with httpx.Client() as client:
        response = client.patch(url, content=body.encode())
    data_store.scenario["response"] = response


@step("Send a DELETE request to <url>")
def send_delete_request(url: str) -> None:
    """Send a DELETE request to the specified URL."""
    with httpx.Client() as client:
        response = client.delete(url)
    data_store.scenario["response"] = response


@step("Send a HEAD request to <url>")
def send_head_request(url: str) -> None:
    """Send a HEAD request to the specified URL."""
    with httpx.Client() as client:
        response = client.head(url)
    data_store.scenario["response"] = response


@step("Send an OPTIONS request to <url>")
def send_options_request(url: str) -> None:
    """Send an OPTIONS request to the specified URL."""
    with httpx.Client() as client:
        response = client.options(url)
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
