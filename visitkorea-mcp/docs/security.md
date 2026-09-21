# Security

- Store `VISITKOREA_API_KEY` in the environment or Replit Secrets; never
  commit it.
- API keys are redacted from upstream error messages.
- Python HTTP binds to loopback by default. Public deployments should use the
  Node proxy and its security headers and rate limiting.
- Uvicorn access logging is disabled because query parameters contain the
  service key.
- Stdio application logging is directed to stderr.
- Inputs are validated before upstream requests, including dates, coordinates,
  radius, and bounded result pages.
- Client, cache, and rate-limiter state is isolated per constructed server.
