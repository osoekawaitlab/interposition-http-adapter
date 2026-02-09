"""Step implementations for Gauge tests."""

import importlib
import re
import subprocess

from getgauge.python import Messages, data_store, step

SEMVER_PATTERN = (
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


@step("Import the <package_name> package")
def import_package(package_name: str) -> None:
    """Import the specified package and verify it is imported successfully."""
    imported_module = importlib.import_module(package_name)
    assert imported_module is not None, f"Failed to import {package_name}"
    Messages.write_message(f"Successfully verified import of {package_name}")
    data_store.scenario["imported_module"] = imported_module


@step("Verify that <attr_name> follows the Semantic Versioning format")
def verify_version_format(attr_name: str) -> None:
    """Verify that the specified attribute follows Semantic Versioning."""
    imported_module = data_store.scenario["imported_module"]
    version_value = getattr(imported_module, attr_name, None)

    assert version_value is not None, f"Attribute {attr_name} not found in package."
    Messages.write_message(f"Detected Version: {version_value}")

    match = re.match(SEMVER_PATTERN, version_value)

    assert match is not None, f"Version '{version_value}' does not follow SemVer!"


@step("Execute the CLI command with <arguments>")
def execute_the_cli_command_with(arguments: str) -> None:
    """Execute the CLI command with the specified argument."""
    args = ["interposition_http_adapter"] + [
        d.strip() for d in arguments.split(" ") if d.strip()
    ]
    result = subprocess.run(  # noqa: S603
        args,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"CLI command failed with error: {result.stderr}"
    data_store.scenario["cli_output"] = result.stdout.strip()


@step("Verify that the output matches the __version__ from the package")
def verify_that_the_output_matches_the_version_from_the_package() -> None:
    """Verify that the CLI output matches the package version."""
    imported_module = data_store.scenario["imported_module"]
    expected_version = getattr(imported_module, "__version__", None)
    cli_output = data_store.scenario["cli_output"]
    assert expected_version is not None, "__version__ attribute not found in package."
    assert expected_version == cli_output, (
        f"Version mismatch: expected '{expected_version}', got '{cli_output}'"
    )
