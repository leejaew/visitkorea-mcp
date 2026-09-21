"""
Tool registration for the VisitKorea MCP server.

Each sub-module owns a logical group of related tools:
  search.py        — area, location, and keyword search
  events.py        — festivals and events
  accommodations.py — accommodation search
  detail.py        — common, intro, detail, and image info
  sync.py          — delta sync list
  codes.py         — reference code lookups (area, category, district, classification)

register_all_tools() wires all handlers into the MCP Server instance.
"""
from __future__ import annotations

import json
import logging

from mcp.server import Server
from mcp.types import TextContent
from utils.api_client import KTOClient, configure_client

from . import search, events, accommodations, detail, sync, codes

_log = logging.getLogger("visitkorea_mcp.tools")

_ALL_MODULES = [search, events, accommodations, detail, sync, codes]


def register_all_tools(server: Server, client: KTOClient | None = None) -> None:
    """Register list_tools and call_tool handlers on *server*."""
    if client is not None:
        configure_client(client)

    @server.list_tools()
    async def list_tools():
        tools = []
        for mod in _ALL_MODULES:
            tools.extend(mod.TOOLS)
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            for mod in _ALL_MODULES:
                result = await mod.handle(name, arguments or {})
                if result is not None:
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )]
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False),
            )]
        except ValueError as exc:
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(exc)}, ensure_ascii=False),
            )]
        except PermissionError:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "Upstream authentication failed."}, ensure_ascii=False),
            )]
        except RuntimeError:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "The upstream service is temporarily unavailable."}, ensure_ascii=False),
            )]
        except Exception as exc:
            _log.exception("Unexpected error in tool '%s'", name)
            return [TextContent(
                type="text",
                text=json.dumps(
                    {"error": "Internal server error."},
                    ensure_ascii=False,
                ),
            )]
