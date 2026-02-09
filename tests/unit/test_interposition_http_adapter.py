"""Unit tests for interposition_http_adapter exports."""

import re

import interposition_http_adapter


def test_interposition_http_adapter_exports_version() -> None:
    """Test that interposition_http_adapter exports the correct version."""
    assert re.match(r"^\d+\.\d+\.\d+$", interposition_http_adapter.__version__)
