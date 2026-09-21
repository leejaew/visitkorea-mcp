"""Constructible MCP application; importing this module has no I/O side effects."""
from __future__ import annotations

from mcp.server import Server

from config import AppConfig
from tools import register_all_tools
from utils.api_client import KTOClient


def create_server(config: AppConfig, client: KTOClient | None = None) -> tuple[Server, KTOClient]:
    api_client = client or KTOClient(config)
    server = Server("visitkorea-mcp")
    register_all_tools(server, client=api_client)
    return server, api_client