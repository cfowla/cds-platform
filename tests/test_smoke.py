"""Smoke tests for the installed package scaffold."""

import importlib


def test_package_imports() -> None:
    """The test runner can import the top-level CDS package."""
    package = importlib.import_module("cds")

    assert package.__name__ == "cds"
