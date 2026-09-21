# Deployment

Install the package with Python 3.11 or newer:

```bash
python -m pip install -e visitkorea-mcp
export VISITKOREA_API_KEY="your-service-key"
python -m mcp_server --http --port 3001
```

The compatibility command remains available:

```bash
python visitkorea-mcp/main.py
```

Use stdio for local MCP clients and Streamable HTTP for the `/mcp` endpoint.
`/healthz` returns `200` after the HTTP session manager is ready and `503`
while it is starting.
