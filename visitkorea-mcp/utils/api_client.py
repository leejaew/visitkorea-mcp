"""Injectable KTO API client with response normalisation and caching."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import httpx

import utils.cache as cache
from config import AppConfig, MOBILE_APP, MOBILE_OS
from utils.rate_limiter import limiter

_log = logging.getLogger("visitkorea_mcp.api_client")


class KTOClient:
    def __init__(self, config: AppConfig, http_client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._client = http_client
        self._owns_client = http_client is None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout_seconds, connect=5.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    def _mask(self, text: str) -> str:
        return text.replace(self.config.api_key, "[REDACTED]")

    def parse_envelope(self, data: dict) -> dict:
        body = data.get("response") if isinstance(data, dict) else None
        if not isinstance(body, dict):
            raise RuntimeError("Korea Tourism API returned a malformed response.")
        header = body.get("header", {}) if isinstance(body, dict) else {}
        if not isinstance(header, dict):
            raise RuntimeError("Korea Tourism API returned a malformed response.")
        code, msg = str(header.get("resultCode", "")), self._mask(str(header.get("resultMsg", "")))
        if code not in ("00", "0000"):
            if code == "03":
                return {"success": True, "resultCode": code, "resultMsg": msg,
                        "numOfRows": 0, "pageNo": 1, "totalCount": 0, "items": []}
            safe = {"10": "INVALID_REQUEST_PARAMETER", "11": "NO_MANDATORY_PARAMETERS",
                    "22": "RATE_LIMIT_EXCEEDED", "30": "SERVICE_KEY_NOT_REGISTERED",
                    "31": "SERVICE_KEY_EXPIRED"}.get(code, "UPSTREAM_ERROR")
            raise PermissionError(safe) if code in ("30", "31") else RuntimeError(safe)
        payload = body.get("body", {})
        if not isinstance(payload, dict):
            raise RuntimeError("Korea Tourism API returned a malformed response.")
        wrapper = payload.get("items") or {}
        if wrapper and not isinstance(wrapper, dict):
            raise RuntimeError("Korea Tourism API returned a malformed response.")
        raw = wrapper.get("item", []) if isinstance(wrapper, dict) else []
        return {"success": True, "resultCode": code, "resultMsg": msg,
                "numOfRows": payload.get("numOfRows", 0), "pageNo": payload.get("pageNo", 1),
                "totalCount": payload.get("totalCount", 0),
                "items": raw if isinstance(raw, list) else [raw]}

    async def call(self, endpoint: str, params: Optional[dict] = None) -> dict:
        query: dict[str, Any] = {"MobileOS": MOBILE_OS, "MobileApp": MOBILE_APP,
                                 "_type": "json", "serviceKey": self.config.api_key}
        query.update({k: v for k, v in (params or {}).items() if v is not None})
        if "numOfRows" in query:
            try: query["numOfRows"] = max(1, min(int(query["numOfRows"]), 100))
            except (TypeError, ValueError): query["numOfRows"] = 10
        key = cache.make_key(endpoint, query)
        hit, value = cache.get(key)
        if hit: return value
        await limiter.acquire()
        client = await self._http()
        last: Exception | None = None
        for attempt in range(3):
            try:
                response = await client.get(f"{self.config.base_url}/{endpoint}", params=query)
                response.raise_for_status()
                break
            except httpx.TimeoutException:
                return {"success": False, "error": "Korea Tourism API request timed out.", "items": [], "totalCount": 0}
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                last = exc
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500:
                    raise RuntimeError("Korea Tourism API rejected the request.") from None
                if attempt < 2: await asyncio.sleep(0.5 * 2 ** attempt)
        else:
            raise RuntimeError("Korea Tourism API is temporarily unavailable.") from None
        try: result = self.parse_envelope(response.json())
        except (ValueError, TypeError):
            raise RuntimeError("Korea Tourism API returned an invalid response.") from None
        if result.get("success") and result.get("totalCount", 0) > 0:
            cache.set(key, result, cache.ttl_for(endpoint))
        return result

    async def close(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()


_client: KTOClient | None = None

def configure_client(client: KTOClient) -> None:
    global _client
    _client = client

async def call_api(endpoint: str, params: Optional[dict] = None) -> dict:
    if _client is None:
        raise RuntimeError("KTO API client is not configured")
    return await _client.call(endpoint, params)