"""Stateless Streamable HTTP transport and health endpoint."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from mcp.server import Server

from ..clients import KTOClient
from ..config import AppConfig


def create_app(server: Server, client: KTOClient):
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    manager = StreamableHTTPSessionManager(
        app=server, event_store=None, json_response=True, stateless=True,
    )
    ready = False

    class MCPApp:
        async def __call__(self, scope, receive, send):
            await manager.handle_request(scope, receive, send)

    async def healthz(request):
        return JSONResponse(
            {"status": "ok" if ready else "starting"},
            status_code=200 if ready else 503,
        )

    async def root(request):
        return JSONResponse(
            {
                "name": "VisitKorea MCP Server",
                "status": "ok" if ready else "starting",
                "mcp": "/mcp",
                "health": "/healthz",
            },
            status_code=200 if ready else 503,
        )

    @asynccontextmanager
    async def lifespan(app):
        nonlocal ready
        closed = False
        try:
            async with manager.run():
                ready = True
                try:
                    yield
                finally:
                    ready = False
        finally:
            ready = False
            if not closed:
                closed = True
                close_task = asyncio.create_task(client.close())
                try:
                    await asyncio.shield(close_task)
                except asyncio.CancelledError:
                    # Complete cleanup before propagating cancellation. The
                    # shield prevents cancellation from interrupting close().
                    await asyncio.shield(close_task)
                    raise

    app = Starlette(
        routes=[
            Route("/", root, methods=["GET"]),
            Route("/api", root, methods=["GET", "POST"]),
            Route("/healthz", healthz, methods=["GET"]),
            Route("/mcp", MCPApp(), methods=["GET", "POST", "DELETE"]),
        ],
        lifespan=lifespan,
    )
    app.state.mcp_manager = manager
    app.state.mcp_stateless = True
    app.state.root = root
    app.state.healthz = healthz
    return app


def run(server: Server, client: KTOClient, config: AppConfig) -> None:
    import uvicorn

    app = create_app(server, client)
    uvicorn.run(app, host=config.host, port=config.port, access_log=False)
