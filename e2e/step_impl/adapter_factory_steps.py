"""Step implementations for adapter factory tests."""

from pathlib import Path

import pytest
from getgauge.python import data_store, step
from interposition.errors import CassetteLoadError

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
