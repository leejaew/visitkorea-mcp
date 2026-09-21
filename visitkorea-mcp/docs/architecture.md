# Architecture

The server uses a Python `src/mcp_server` package. `main.py` coordinates
configuration, dependency construction, transport selection, and shutdown;
`server.py` constructs the MCP SDK server without starting it.

MCP capability adapters in `tools/` only map requests to `TourismService`.
The service owns ordinary Python workflows and validation, while `clients/`
contains the KTO HTTP client, response parsing, retries, cache, and rate
limiter. Every constructed server receives its own client, cache, and limiter.

The HTTP adapter is stateless Streamable HTTP at `/mcp` and exposes `/healthz`.
The stdio adapter reserves stdout for MCP protocol traffic; application logs
are configured for stderr.
