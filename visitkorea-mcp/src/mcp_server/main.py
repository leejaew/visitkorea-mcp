"""Small process coordinator for the VisitKorea MCP server."""
from __future__ import annotations

import argparse
import asyncio

from .config import AppConfig
from .observability import configure_logging
from .server import create_server
from .transports.stdio import run as run_stdio


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="VisitKorea MCP Server")
    parser.add_argument("--http", action="store_true")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    config = AppConfig.from_env()
    if args.host or args.port:
        config = AppConfig(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout_seconds=config.timeout_seconds,
            host=args.host or config.host,
            port=args.port or config.port,
        )
    server, client = create_server(config)
    if args.http:
        from .transports.http import run
        run(server, client, config)
        return

    async def run_local() -> None:
        try:
            await run_stdio(server)
        finally:
            await client.close()

    asyncio.run(run_local())
