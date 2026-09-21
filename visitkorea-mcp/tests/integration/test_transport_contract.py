import unittest
import logging
from pathlib import Path
import subprocess
import sys
import asyncio
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock

from mcp.server import Server

from mcp_server.clients import KTOClient
from mcp_server.config import AppConfig
from mcp_server.observability.logging import configure_logging
from mcp_server.transports import http, stdio


class TransportContractTests(unittest.TestCase):
    def test_transport_adapters_are_importable(self):
        self.assertTrue(callable(http.run))
        self.assertTrue(callable(stdio.run))

    def test_http_routes_are_stateless_and_named(self):
        with TemporaryDirectory() as directory:
            app = http.create_app(
                Server("test"),
                KTOClient(AppConfig(api_key="secret")),
                landing_dir=Path(directory),
            )
            self.assertTrue(app.state.mcp_stateless)
            self.assertFalse(app.state.landing_enabled)
            routes = {route.path: route for route in app.routes}
            self.assertEqual(
                set(routes),
                {"/", "/api", "/api/config", "/healthz", "/mcp"},
            )
            self.assertEqual(routes["/api"].methods, {"GET", "HEAD", "POST"})
            self.assertEqual(
                routes["/mcp"].methods,
                {"GET", "HEAD", "POST", "DELETE"},
            )

    def test_http_mounts_built_landing_page_when_available(self):
        with TemporaryDirectory() as directory:
            landing_dir = Path(directory)
            (landing_dir / "index.html").write_text(
                "<!doctype html><title>VisitKorea</title>",
                encoding="utf-8",
            )
            app = http.create_app(
                Server("test"),
                KTOClient(AppConfig(api_key="secret")),
                landing_dir=landing_dir,
            )

            self.assertTrue(app.state.landing_enabled)
            routes = {route.path: route for route in app.routes}
            self.assertEqual(
                set(routes),
                {"", "/api", "/api/config", "/healthz", "/mcp"},
            )
            self.assertEqual(routes[""].name, "landing")

    def test_http_readiness_and_client_shutdown(self):
        class Client:
            close = AsyncMock()

        client = Client()
        app = http.create_app(Server("test"), client)

        async def exercise():
            self.assertEqual((await app.state.readiness(None)).status_code, 503)
            self.assertEqual((await app.state.healthz(None)).status_code, 503)
            async with app.router.lifespan_context(app):
                self.assertEqual((await app.state.readiness(None)).status_code, 200)
                self.assertEqual((await app.state.healthz(None)).status_code, 200)
            self.assertEqual((await app.state.readiness(None)).status_code, 503)
            self.assertEqual((await app.state.healthz(None)).status_code, 503)

        asyncio.run(exercise())
        client.close.assert_awaited_once()

    def test_http_lifespan_exception_still_closes_and_resets_readiness(self):
        class Client:
            close = AsyncMock()

        client = Client()
        app = http.create_app(Server("test"), client)

        async def exercise():
            self.assertEqual((await app.state.healthz(None)).status_code, 503)
            with self.assertRaises(ExceptionGroup):
                async with app.router.lifespan_context(app):
                    self.assertEqual((await app.state.healthz(None)).status_code, 200)
                    raise RuntimeError("request failed")
            self.assertEqual((await app.state.healthz(None)).status_code, 503)

        asyncio.run(exercise())
        client.close.assert_awaited_once()

    def test_stdio_logging_is_stderr_only(self):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            configure_logging()
            logging.getLogger("stdio-test").warning("diagnostic")
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("diagnostic", stderr.getvalue())

    def test_compatibility_launcher_accepts_help(self):
        completed = subprocess.run(
            [sys.executable, "main.py", "--help"],
            cwd=Path(__file__).parents[2],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("VisitKorea MCP Server", completed.stdout)
