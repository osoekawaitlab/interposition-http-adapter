"""HTTP adapter for Interposition."""

from interposition_http_adapter._version import __version__
from interposition_http_adapter.app import InterpositionHttpAdapter

__all__ = ["InterpositionHttpAdapter", "__version__"]
