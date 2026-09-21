"""Stateless Streamable HTTP transport and health endpoint."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
from urllib.parse import urlsplit

from mcp.server import Server

from ..clients import KTOClient
from ..config import AppConfig


DEFAULT_LANDING_DIR = (
    Path(__file__).resolve().parents[4]
    / "artifacts"
    / "landing"
    / "dist"
    / "public"
)


def create_app(
    server: Server,
    client: KTOClient,
    landing_dir: Path | None = None,
):
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Mount, Route
    from starlette.staticfiles import StaticFiles

    manager = StreamableHTTPSessionManager(
        app=server, event_store=None, json_response=True, stateless=True,
    )
    ready = False
    static_dir = landing_dir or DEFAULT_LANDING_DIR
    landing_enabled = (static_dir / "index.html").is_file()

    class MCPApp:
        async def __call__(self, scope, receive, send):
            await manager.handle_request(scope, receive, send)

    async def healthz(request):
        return JSONResponse(
            {"status": "ok" if ready else "starting"},
            status_code=200 if ready else 503,
        )

    async def readiness(request):
        return JSONResponse(
            {
                "name": "VisitKorea MCP Server",
                "status": "ok" if ready else "starting",
                "mcp": "/mcp",
                "health": "/healthz",
            },
            status_code=200 if ready else 503,
        )

    async def config(request):
        configured_url = os.environ.get("PRODUCTION_MCP_URL", "").strip()
        if configured_url:
            parsed = urlsplit(configured_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise RuntimeError(
                    "PRODUCTION_MCP_URL must be an absolute HTTP or HTTPS URL"
                )
            mcp_url = configured_url
        else:
            forwarded_host = request.headers.get("x-forwarded-host")
            host = (
                forwarded_host.split(",", 1)[0].strip()
                if forwarded_host
                else request.url.netloc
            )
            hostname = host.split(":", 1)[0].lower()
            is_development_host = (
                hostname == "localhost"
                or hostname == "127.0.0.1"
                or hostname.endswith(".replit.dev")
            )
            if is_development_host:
                mcp_url = None
            else:
                forwarded_proto = request.headers.get("x-forwarded-proto")
                scheme = (
                    forwarded_proto.split(",", 1)[0].strip()
                    if forwarded_proto
                    else request.url.scheme
                )
                mcp_url = f"{scheme}://{host}/mcp"

        public_host = urlsplit(mcp_url).netloc if mcp_url else None
        return JSONResponse(
            {
                "mcpUrl": mcp_url,
                "host": public_host,
            }
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

    routes = [
        Route("/api", readiness, methods=["GET", "POST"]),
        Route("/api/config", config, methods=["GET"]),
        Route("/healthz", healthz, methods=["GET"]),
        Route("/mcp", MCPApp(), methods=["GET", "POST", "DELETE"]),
    ]
    if landing_enabled:
        routes.append(
            Mount(
                "/",
                app=StaticFiles(directory=static_dir, html=True),
                name="landing",
            )
        )
    else:
        routes.insert(0, Route("/", readiness, methods=["GET"]))

    app = Starlette(routes=routes, lifespan=lifespan)
    app.state.mcp_manager = manager
    app.state.mcp_stateless = True
    app.state.landing_enabled = landing_enabled
    app.state.config = config
    app.state.readiness = readiness
    app.state.healthz = healthz
    return app


def run(server: Server, client: KTOClient, config: AppConfig) -> None:
    import uvicorn

    app = create_app(server, client)
    uvicorn.run(app, host=config.host, port=config.port, access_log=False)
