"""Step implementations for adapter factory tests."""

import json
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from getgauge.python import data_store, step
from interposition import InteractionRequest, ResponseChunk
from interposition.errors import CassetteLoadError, LiveResponderRequiredError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from interposition import BrokerMode

from interposition_http_adapter import InterpositionHttpAdapter

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@step("Create an adapter from cassette file <file_path>")
def create_adapter_from_cassette_file(file_path: str) -> None:
    """Create an InterpositionHttpAdapter from a cassette JSON file."""
    resolved_path = _PROJECT_ROOT / file_path
    adapter = InterpositionHttpAdapter.from_cassette_file(resolved_path)
    data_store.scenario["adapter"] = adapter


@step("Verify that creating an adapter from cassette file <file_path> raises an error")
def verify_adapter_creation_raises_error(file_path: str) -> None:
    """Verify that creating an adapter from a cassette file raises an error."""
    resolved_path = _PROJECT_ROOT / file_path
    with pytest.raises(CassetteLoadError):
        InterpositionHttpAdapter.from_cassette_file(resolved_path)


@step(
    "Verify that creating an adapter from cassette file <file_path> in <mode> mode without a live responder raises an error"
)
def verify_adapter_creation_without_live_responder_raises_error(
    file_path: str, mode: str
) -> None:
    """Verify that creating an adapter without a live responder raises an error."""
    resolved_path = _PROJECT_ROOT / file_path
    with pytest.raises(LiveResponderRequiredError):
        InterpositionHttpAdapter.from_cassette_file(
            resolved_path, mode=cast("BrokerMode", mode)
        )


def _live_responder(
    _request: InteractionRequest,
) -> "Iterable[ResponseChunk]":
    """A simple live responder that returns a fixed response."""
    return [
        ResponseChunk(
            data=b"recorded response",
            sequence=0,
            metadata=(("status_code", "200"),),
        ),
    ]


@step(
    "Create an adapter from cassette file <file_path> in <mode> mode with a live responder"
)
def create_adapter_from_file_with_mode_and_live_responder(
    file_path: str, mode: str
) -> None:
    """Create an adapter from a cassette file with mode and live responder."""
    resolved_path = _PROJECT_ROOT / file_path
    adapter = InterpositionHttpAdapter.from_cassette_file(
        resolved_path,
        mode=cast("BrokerMode", mode),
        live_responder=_live_responder,
    )
    data_store.scenario["adapter"] = adapter


@step("Create a temporary cassette file")
def create_temporary_cassette_file() -> None:
    """Create an empty temporary cassette file."""
    tmp_dir = tempfile.mkdtemp()
    cassette_path = Path(tmp_dir) / "cassette.json"
    cassette_path.write_text(json.dumps({"interactions": []}))
    data_store.scenario["tmp_cassette_path"] = cassette_path


@step("Create a temporary cassette file from <file_path>")
def create_temporary_cassette_file_from(file_path: str) -> None:
    """Create a temporary cassette file copied from an existing fixture."""
    source_path = _PROJECT_ROOT / file_path
    tmp_dir = tempfile.mkdtemp()
    cassette_path = Path(tmp_dir) / "cassette.json"
    shutil.copy2(source_path, cassette_path)
    data_store.scenario["tmp_cassette_path"] = cassette_path


@step(
    "Create an adapter from the temporary cassette file in <mode> mode with a live responder"
)
def create_adapter_with_mode_and_live_responder(
    mode: str,
) -> None:
    """Create an adapter with mode and live responder."""
    cassette_path = data_store.scenario["tmp_cassette_path"]
    assert isinstance(cassette_path, Path)
    adapter = InterpositionHttpAdapter.from_cassette_file(
        cassette_path,
        mode=cast("BrokerMode", mode),
        live_responder=_live_responder,
    )
    data_store.scenario["adapter"] = adapter


@step(
    [
        "Verify that the temporary cassette file contains <count> interaction",
        "Verify that the temporary cassette file contains <count> interactions",
    ]
)
def verify_cassette_file_interaction_count(
    count: str,
) -> None:
    """Verify the number of interactions in the temporary cassette file."""
    cassette_path = data_store.scenario["tmp_cassette_path"]
    assert isinstance(cassette_path, Path)
    data = json.loads(cassette_path.read_text())
    assert len(data["interactions"]) == int(count)


@step("Clean up temporary cassette file if created")
def clean_up_temporary_cassette_file() -> None:
    """Remove the temporary cassette directory if it was created."""
    cassette_path = data_store.scenario.get("tmp_cassette_path")
    if isinstance(cassette_path, Path) and cassette_path.parent.exists():
        shutil.rmtree(cassette_path.parent)
