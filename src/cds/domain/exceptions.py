"""Passive typed exceptions for unexpected domain-system failures."""


class ValidationError(Exception):
    """Unexpected failure enforcing an internal validation contract."""


class ContentNotFound(Exception):
    """Required application or repository content could not be located."""


class CalculationError(Exception):
    """Unexpected failure in a calculation implementation."""
