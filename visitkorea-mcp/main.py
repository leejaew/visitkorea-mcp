"""Compatibility launcher for documented and existing integrations."""
from __future__ import annotations

import pathlib
import sys

_SRC = pathlib.Path(__file__).with_name("src")
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from mcp_server.__main__ import main


if __name__ == "__main__":
    main()