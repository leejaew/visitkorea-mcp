"""Streamable HTTP transport adapter."""
from __future__ import annotations

from contextlib import asynccontextmanager

from config import AppConfig
from mcp.server import Server
from utils.api_client import KTOClient


def run(server: Server, client: KTOClient, config: AppConfig) -> None:
    import uvicorn
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    manager = StreamableHTTPSessionManager(app=server, event_store=None, json_response=True, stateless=True)
    ready = False

    class MCPApp:
        async def __call__(self, scope, receive, send):
            await manager.handle_request(scope, receive, send)

    async def healthz(request):
        return JSONResponse({"status": "ok" if ready else "starting"}, status_code=200 if ready else 503)

    @asynccontextmanager
    async def lifespan(app):
        nonlocal ready
        async with manager.run():
            ready = True
            try:
                yield
            finally:
                ready = False
        await client.close()

    app = Starlette(routes=[
        Route("/healthz", healthz, methods=["GET"]),
        Route("/mcp", MCPApp(), methods=["GET", "POST", "DELETE"]),
    ], lifespan=lifespan)
    uvicorn.run(app, host=config.host, port=config.port, access_log=False)