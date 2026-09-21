"""Ordered MCP tool registration and safe response mapping."""
from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from ..services.tourism import TourismService
from . import accommodations, codes, detail, events, search, sync

_log = logging.getLogger("visitkorea_mcp.tools")
_MODULES = [search, events, accommodations, detail, sync, codes]
_ALL_MODULES = _MODULES


class ToolRegistry:
    """Owns capability callbacks for one constructible MCP server."""

    def __init__(self, service: TourismService) -> None:
        self.service = service

    @property
    def tools(self) -> list[Tool]:
        return [tool for module in _MODULES for tool in module.TOOLS]

    async def list_tools(self) -> list[Tool]:
        return self.tools

    async def call_tool(self, name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        args = arguments or {}
        try:
            for module in _MODULES:
                result = await module.handle(name, args, self.service)
                if result is not None:
                    return [self._text(result, indent=2)]
            return [self._text({"error": f"Unknown tool: {name}"})]
        except ValueError as exc:
            return [self._text({"error": str(exc)})]
        except PermissionError:
            return [self._text({"error": "Upstream authentication failed."})]
        except RuntimeError:
            return [self._text({"error": "The upstream service is temporarily unavailable."})]
        except Exception:
            _log.exception("Unexpected error in tool '%s'", name)
            return [self._text({"error": "Internal server error."})]

    @staticmethod
    def _text(value: dict[str, Any], indent: int | None = None) -> TextContent:
        return TextContent(type="text", text=json.dumps(value, ensure_ascii=False, indent=indent))


def register_all_tools(server: Server, service: TourismService) -> ToolRegistry:
    """Register one registry's callbacks and return it for tests/lifecycle management."""
    registry = ToolRegistry(service)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return await registry.list_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        return await registry.call_tool(name, arguments)

    return registry
