"""Safe application errors used at the MCP boundary."""
from __future__ import annotations


class ApplicationError(Exception):
    """Base class for expected, client-safe application failures."""

    public_message = "Internal server error."


class ConfigurationError(ValueError, ApplicationError):
    """Raised when startup configuration is invalid."""


class UpstreamError(RuntimeError, ApplicationError):
    """Raised when the upstream tourism API cannot fulfill a request."""
