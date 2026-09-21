"""Safe logging setup for MCP transports."""
from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.WARNING) -> None:
    """Configure application logs on stderr, never stdout."""
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )
