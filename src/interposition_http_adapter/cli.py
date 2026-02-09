"""CLI module for interposition_http_adapter."""

from argparse import ArgumentParser

from interposition_http_adapter._version import __version__


def generate_cli_parser() -> ArgumentParser:
    """Generate the argument parser for the interposition_http_adapter CLI."""
    parser = ArgumentParser(description="HTTP adapter for Interposition.")
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main() -> None:
    """Entry point for the interposition_http_adapter command-line interface."""
    parser = generate_cli_parser()
    _ = parser.parse_args()
