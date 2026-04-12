"""
Async HTTP client for the KTO EngService2 Open API.

Responsibilities (single concern: HTTP transport + response normalisation):
  - Load and normalise the API key once at startup.
  - Maintain a shared httpx.AsyncClient connection pool.
  - Execute GET requests with retry + exponential back-off.
  - Normalise the KTO JSON envelope into a consistent result dict.

Caching and rate-limiting are handled by sibling modules:
  utils/cache.py         — TTL response cache
  utils/rate_limiter.py  — token bucket (10 req/min, burst 5)
"""
from __future__ import annotations

import asyncio
import logging
import os
import urllib.parse
from typing import Any, Optional

import httpx

import utils.cache as cache
from utils.rate_limiter import limiter
from config import BASE_URL, MOBILE_OS, MOBILE_APP

_log = logging.getLogger("visitkorea_mcp.api_client")


# ---------------------------------------------------------------------------
# API key — normalised once at import time
# ---------------------------------------------------------------------------

def _load_api_key() -> str:
    raw = os.environ.get("VISITKOREA_API_KEY", "")
    if not raw:
        raise EnvironmentError(
            "VISITKOREA_API_KEY is not set. "
            "Add it to Replit Secrets (or a .env file for local use)."
        )
    # data.go.kr issues an "Encoding key" (URL-percent-encoded) and a
    # "Decoding key" (plain text). unquote() normalises either variant so
    # that httpx encodes it exactly once when building the query string.
    return urllib.parse.unquote(raw)


_API_KEY: str = _load_api_key()

_FIXED_PARAMS: dict[str, Any] = {
    "MobileOS": MOBILE_OS,
    "MobileApp": MOBILE_APP,
    "_type": "json",
    "serviceKey": _API_KEY,
}


# ---------------------------------------------------------------------------
# Shared async HTTP client with connection pool
# ---------------------------------------------------------------------------
# One client for the lifetime of the process — TCP connections to
# apis.data.go.kr are reused across all tool calls (no per-call TLS handshake).

_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0, connect=5.0),
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    verify=True,
)


# ---------------------------------------------------------------------------
# Response normalisation
# ---------------------------------------------------------------------------

def _mask_key(text: str) -> str:
    """Redact the raw API key from any string before surfacing to callers."""
    return text.replace(_API_KEY, "[REDACTED]")


def _parse_envelope(data: dict) -> dict:
    """
    Convert the KTO API JSON envelope to a consistent result dict.

    Raises RuntimeError / ValueError / PermissionError on API error codes
    so callers never have to inspect raw result codes.
    """
    response_body = data.get("response", {})
    header = response_body.get("header", {})
    result_code = str(header.get("resultCode", ""))
    result_msg = _mask_key(str(header.get("resultMsg", "")))

    _ERROR_MAP = {
        "03": None,          # no results — handled below
        "10": ValueError(f"INVALID_REQUEST_PARAMETER: {result_msg}"),
        "11": ValueError(f"NO_MANDATORY_PARAMETERS: {result_msg}"),
        "22": RuntimeError(
            "RATE_LIMIT_EXCEEDED: Daily upstream quota of 1,000 requests reached. "
            "Try again tomorrow or contact your data.go.kr account administrator."
        ),
        "30": PermissionError(
            "SERVICE_KEY_NOT_REGISTERED: Verify VISITKOREA_API_KEY in Replit Secrets."
        ),
        "31": PermissionError(
            "SERVICE_KEY_EXPIRED: The data.go.kr API key has passed its expiry date."
        ),
    }

    if result_code not in ("00", "0000"):
        exc = _ERROR_MAP.get(result_code)
        if exc is None:  # code "03" → no results
            return {
                "success": True, "resultCode": result_code, "resultMsg": result_msg,
                "numOfRows": 0, "pageNo": 1, "totalCount": 0, "items": [],
            }
        if exc:
            raise exc
        raise RuntimeError(f"API error (code={result_code}): {result_msg}")

    body = response_body.get("body", {})
    items_wrapper = body.get("items") or {}
    raw = items_wrapper.get("item", []) if items_wrapper else []
    items: list = raw if isinstance(raw, list) else [raw]

    return {
        "success": True,
        "resultCode": result_code,
        "resultMsg": result_msg,
        "numOfRows": body.get("numOfRows", 0),
        "pageNo": body.get("pageNo", 1),
        "totalCount": body.get("totalCount", 0),
        "items": items,
    }


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

async def call_api(endpoint: str, params: Optional[dict] = None) -> dict:
    """
    Async GET to EngService2. Returns a normalised result dict.

    Flow:
      1. Check TTL cache — return immediately on hit (no rate-limit token used).
      2. Acquire rate-limit token via token bucket.
      3. HTTP GET with up to 3 retry attempts on 5xx / network errors.
      4. Parse and validate JSON response envelope.
      5. Store successful result in cache.
    """
    query: dict[str, Any] = dict(_FIXED_PARAMS)
    if params:
        for k, v in params.items():
            if v is not None:
                query[k] = v

    # Clamp numOfRows to the API's documented maximum
    if "numOfRows" in query:
        try:
            query["numOfRows"] = max(1, min(int(query["numOfRows"]), 100))
        except (TypeError, ValueError):
            query["numOfRows"] = 10

    ck = cache.make_key(endpoint, query)
    hit, cached = cache.get(ck)
    if hit:
        return cached

    await limiter.acquire()

    url = f"{BASE_URL}/{endpoint}"
    last_exc: Exception | None = None

    for attempt in range(3):
        try:
            resp = await _http_client.get(url, params=query)
            resp.raise_for_status()
            break
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code >= 500:
                last_exc = exc
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue
            raise RuntimeError(
                f"Upstream returned HTTP {exc.response.status_code}: "
                f"{_mask_key(str(exc))}"
            ) from None
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request to Korea Tourism API timed out (30 s). "
                         "The upstream service may be temporarily slow.",
                "items": [], "totalCount": 0,
            }
        except httpx.RequestError as exc:
            last_exc = exc
            await asyncio.sleep(0.5 * (2 ** attempt))
            continue
    else:
        raise RuntimeError(
            f"Korea Tourism API unreachable after 3 attempts: {type(last_exc).__name__}"
        )

    try:
        data = resp.json()
    except Exception:
        raise RuntimeError("Korea Tourism API returned a non-JSON response.") from None

    result = _parse_envelope(data)
    if result.get("success"):
        cache.set(ck, result, cache.ttl_for(endpoint))

    return result
