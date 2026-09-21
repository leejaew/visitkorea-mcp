"""Constructible MCP server and dependency wiring."""
from __future__ import annotations

from mcp.server import Server

from .clients import KTOClient
from .config import AppConfig
from .services import TourismService
from .tools import register_all_tools


def create_server(
    config: AppConfig,
    client: KTOClient | None = None,
) -> tuple[Server, KTOClient]:
    """Construct a server without starting a process or performing I/O."""
    api_client = client or KTOClient(config)
    server = Server("visitkorea-mcp")
    register_all_tools(server, TourismService(api_client))
    return server, api_client
