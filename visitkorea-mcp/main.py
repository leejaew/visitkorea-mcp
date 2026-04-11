"""
VisitKorea MCP Server — entry point
====================================
A Model Context Protocol (MCP) server connecting AI agents (Claude, Manus AI, etc.)
with the Korea Tourism Organization (한국관광공사) English Tourism Information Open Data API.

API Base:     https://apis.data.go.kr/B551011/EngService2/
API Provider: Korea Tourism Organization via data.go.kr

Environment Variables:
  VISITKOREA_API_KEY  — Your service key from data.go.kr (URL-encoded or plain)

Usage:
  python3 main.py              # stdio mode (Claude Desktop / local use)
  python3 main.py --http       # Streamable HTTP mode (remote/web-based MCP clients)
  python3 main.py --http --port 3001
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

# Ensure the package root is on the path so sibling imports work correctly
# when the file is run directly (python3 main.py) as well as via subprocess.
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server import Server
from mcp.server.stdio import stdio_server

from tools import register_all_tools

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)
_log = logging.getLogger("visitkorea_mcp")


# ---------------------------------------------------------------------------
# MCP Server — wired up with all tool modules
# ---------------------------------------------------------------------------

server = Server("visitkorea-mcp")
register_all_tools(server)


# ---------------------------------------------------------------------------
# Transport: stdio (Claude Desktop / local CLI)
# ---------------------------------------------------------------------------

async def _run_stdio() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


# ---------------------------------------------------------------------------
# Transport: Streamable HTTP (Manus AI, remote MCP clients)
# ---------------------------------------------------------------------------

def _run_http(host: str = "127.0.0.1", port: int = 3001) -> None:
    """
    Start a Starlette/uvicorn ASGI server exposing two routes:

      GET  /healthz  — readiness probe (200 only after session manager is ready)
      *    /mcp      — MCP Streamable HTTP endpoint

    The /healthz endpoint is used by the Node.js proxy to avoid forwarding
    requests before Python's async session manager has completed lifespan
    startup (which would raise "Task group is not initialized").

    Python is bound to 127.0.0.1 so the internal port is loopback-only;
    all external traffic arrives via the Node.js reverse proxy on port 8080.
    """
    from contextlib import asynccontextmanager

    import uvicorn
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    from starlette.types import Receive, Scope, Send

    from utils.api_client import _http_client  # shared client to close on shutdown

    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    # Readiness flag — set True only after session_manager.run() enters its
    # lifespan context (the task group and anyio event loop are fully started).
    _ready: dict[str, bool] = {"value": False}

    class MCPApp:
        """
        Canonical ASGI callable for the MCP endpoint.

        Using a class (not an async function) prevents Starlette from wrapping
        the callable in request_response(), which can interfere with exception
        propagation when the session manager sends the HTTP response directly.
        """

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            try:
                await session_manager.handle_request(scope, receive, send)
            except BaseException as exc:
                _log.error("MCP request error (%s): %s", type(exc).__name__, exc)
                if not isinstance(exc, Exception):
                    # Re-raise true async cancellations so anyio can manage them
                    raise

    mcp_app = MCPApp()

    async def healthz(request) -> JSONResponse:
        """Readiness probe — 200 only when the session manager is live."""
        if _ready["value"]:
            return JSONResponse({"status": "ok"})
        return JSONResponse({"status": "starting"}, status_code=503)

    @asynccontextmanager
    async def lifespan(app):
        async with session_manager.run():
            _ready["value"] = True
            try:
                yield
            finally:
                _ready["value"] = False
        # Gracefully close the shared httpx connection pool on shutdown
        await _http_client.aclose()

    asgi_app = Starlette(
        routes=[
            Route("/healthz", endpoint=healthz, methods=["GET"]),
            Route("/mcp", endpoint=mcp_app, methods=["GET", "POST", "DELETE"]),
        ],
        lifespan=lifespan,
    )

    print(f"VisitKorea MCP Server running at http://{host}:{port}/mcp", flush=True)
    # access_log=False prevents uvicorn from writing the full request URL
    # (which contains serviceKey as a query param) to stdout/stderr.
    uvicorn.run(asgi_app, host=host, port=port, access_log=False)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="VisitKorea MCP Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--http", action="store_true",
        help="Run in Streamable HTTP mode (default: stdio)",
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Host to bind in HTTP mode",
    )
    parser.add_argument(
        "--port", type=int, default=None,
        help="Port to listen on in HTTP mode (default: $PORT or 3001)",
    )
    cli_args = parser.parse_args()

    if cli_args.http:
        port = cli_args.port or int(os.environ.get("PORT", 3001))
        _run_http(host=cli_args.host, port=port)
    else:
        asyncio.run(_run_stdio())
