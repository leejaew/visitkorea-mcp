"""
Async HTTP client for the KTO EngService2 Open API.

Design decisions (benchmarked against visitkorea-medicaltourism-mcp):
  - Shared httpx.AsyncClient: reuses TCP keep-alive connections across all
    tool calls. Creating a new client per request adds a full TLS handshake
    to every round-trip to apis.data.go.kr (Seoul datacenter).
  - API key normalisation at import time: unquotes the URL-encoded key from
    data.go.kr once, then lets httpx encode it correctly in params.
  - TTL response cache: static reference tables (area codes, category codes,
    legal district codes, classification codes) are cached for 1 hour.
    All other endpoints are cached for 5 minutes to reduce upstream quota
    consumption while still reflecting daily dataset refreshes.
  - Token bucket rate limiter: at most 10 real upstream calls per minute.
    Prevents a runaway AI agent exhausting the 1,000 req/day quota.
  - API key masking: the raw key is redacted from all error strings before
    they surface to callers, since httpx exceptions include the full URL.
  - Retry with exponential back-off: up to 3 attempts on 5xx / network errors.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
import urllib.parse
from typing import Any, Optional

import httpx

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
    # data.go.kr issues an "Encoding key" (already URL-percent-encoded) and a
    # "Decoding key" (plain text). unquote() normalises either variant so that
    # httpx encodes it exactly once when it builds the query string.
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

_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0, connect=5.0),
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    verify=True,
)


# ---------------------------------------------------------------------------
# TTL response cache
# ---------------------------------------------------------------------------
# Key = sha256(endpoint + params without serviceKey) — avoids key leakage.
# Value = (expires_monotonic, result_dict).

_CACHE_TTL_BY_ENDPOINT: dict[str, int] = {
    "ldongCode2":     3_600,   # 1 h  — legal district codes (static)
    "lclsSystmCode2": 3_600,   # 1 h  — classification codes (static)
    "areaCode2":      3_600,   # 1 h  — area codes (static)
    "categoryCode2":  3_600,   # 1 h  — category codes (static)
}
_DEFAULT_CACHE_TTL = 300       # 5 min — live search/detail endpoints

_cache: dict[str, tuple[float, Any]] = {}


def _cache_key(endpoint: str, params: dict) -> str:
    safe = {k: v for k, v in params.items() if k != "serviceKey"}
    blob = json.dumps(safe, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode()).hexdigest()[:16]
    return f"{endpoint}:{digest}"


def _cache_get(key: str) -> tuple[bool, Any]:
    entry = _cache.get(key)
    if entry and time.monotonic() < entry[0]:
        return True, entry[1]
    _cache.pop(key, None)
    return False, None


def _cache_set(key: str, value: Any, ttl: int) -> None:
    _cache[key] = (time.monotonic() + ttl, value)


# ---------------------------------------------------------------------------
# Token bucket rate limiter — guards real upstream calls
# ---------------------------------------------------------------------------

class _TokenBucket:
    """Simple async token bucket: `rate` tokens/second, burst of `capacity`."""

    def __init__(self, rate: float, capacity: float) -> None:
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def acquire(self) -> None:
        async with self._get_lock():
            now = time.monotonic()
            self._tokens = min(
                self._capacity,
                self._tokens + (now - self._last) * self._rate,
            )
            self._last = now
            if self._tokens < 1:
                wait = (1.0 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0


# 10 real upstream calls per minute, burst of 5
_rate_limiter = _TokenBucket(rate=10 / 60, capacity=5)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask_key(text: str) -> str:
    """Redact the raw API key from any string before surfacing to callers."""
    return text.replace(_API_KEY, "[REDACTED]")


def _parse_response(data: dict) -> dict:
    """
    Normalise the KTO API JSON envelope into a consistent result dict.

    Returns a dict with keys: success, resultCode, resultMsg,
    numOfRows, pageNo, totalCount, items.
    Raises RuntimeError / ValueError / PermissionError on API error codes.
    """
    response_body = data.get("response", {})
    header = response_body.get("header", {})
    result_code = str(header.get("resultCode", ""))
    result_msg = _mask_key(str(header.get("resultMsg", "")))

    if result_code in ("00", "0000"):
        pass  # success
    elif result_code == "03":
        return {"success": True, "resultCode": result_code, "resultMsg": result_msg,
                "numOfRows": 0, "pageNo": 1, "totalCount": 0, "items": []}
    elif result_code == "10":
        raise ValueError(f"INVALID_REQUEST_PARAMETER: {result_msg}")
    elif result_code == "11":
        raise ValueError(f"NO_MANDATORY_PARAMETERS: {result_msg}")
    elif result_code == "22":
        raise RuntimeError(
            "RATE_LIMIT_EXCEEDED: Daily upstream quota of 1,000 requests reached. "
            "Try again tomorrow or contact your data.go.kr account administrator."
        )
    elif result_code == "30":
        raise PermissionError(
            "SERVICE_KEY_NOT_REGISTERED: Verify VISITKOREA_API_KEY in Replit Secrets."
        )
    elif result_code == "31":
        raise PermissionError(
            "SERVICE_KEY_EXPIRED: The data.go.kr API key has passed its expiry date."
        )
    else:
        raise RuntimeError(f"API error (code={result_code}): {result_msg}")

    body = response_body.get("body", {})
    items_wrapper = body.get("items") or {}
    if not items_wrapper or items_wrapper == "":
        items: list = []
    else:
        raw = items_wrapper.get("item", [])
        items = raw if isinstance(raw, list) else [raw]

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
# Public API
# ---------------------------------------------------------------------------

async def call_api(endpoint: str, params: Optional[dict] = None) -> dict:
    """
    Async GET to EngService2. Returns a normalised result dict.

    Flow:
      1. Check TTL cache — return immediately on hit.
      2. Acquire rate-limit token (waits if bucket is empty).
      3. HTTP GET with up to 3 retry attempts on 5xx / network errors.
      4. Parse and validate JSON response envelope.
      5. Store result in cache and return.

    Args:
        endpoint: EngService2 operation name (e.g. "areaBasedList2").
        params:   Optional dict of query parameters (None values are dropped).
                  numOfRows is clamped to [1, 100] automatically.
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

    # Cache check
    ck = _cache_key(endpoint, query)
    hit, cached = _cache_get(ck)
    if hit:
        return cached

    # Rate-limit gate — only applies to real upstream calls
    await _rate_limiter.acquire()

    url = f"{BASE_URL}/{endpoint}"
    ttl = _CACHE_TTL_BY_ENDPOINT.get(endpoint, _DEFAULT_CACHE_TTL)
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
                         "The upstream API may be temporarily slow.",
                "items": [], "totalCount": 0,
            }
        except httpx.RequestError as exc:
            last_exc = exc
            await asyncio.sleep(0.5 * (2 ** attempt))
            continue
    else:
        raise RuntimeError(
            f"Korea Tourism API unreachable after 3 attempts: "
            f"{type(last_exc).__name__}"
        )

    try:
        data = resp.json()
    except Exception:
        raise RuntimeError("Korea Tourism API returned a non-JSON response.") from None

    result = _parse_response(data)

    # Populate cache on success
    if result.get("success"):
        _cache_set(ck, result, ttl)

    return result
