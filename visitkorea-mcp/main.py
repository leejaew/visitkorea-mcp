"""VisitKorea MCP process entry point."""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from config import AppConfig
from server import create_server
from transports.stdio import run as run_stdio

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s", stream=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="VisitKorea MCP Server")
    parser.add_argument("--http", action="store_true")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    config = AppConfig.from_env()
    if args.host or args.port:
        config = AppConfig(config.api_key, config.base_url, config.timeout_seconds,
                           args.host or config.host, args.port or config.port)
    server, client = create_server(config)
    if args.http:
        from transports.http import run
        run(server, client, config)
    else:
        async def run_local() -> None:
            try:
                await run_stdio(server)
            finally:
                # Keep shutdown in the same loop as the stdio transport.
                await client.close()
        asyncio.run(run_local())


if __name__ == "__main__":
    main()