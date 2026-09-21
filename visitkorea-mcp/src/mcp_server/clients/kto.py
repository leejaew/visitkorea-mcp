"""Korea Tourism Organization API client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from ..config import AppConfig, MOBILE_APP, MOBILE_OS
from ..errors import UpstreamError
from .cache import ResponseCache, make_key, ttl_for
from .rate_limiter import AsyncRateLimiter

_log = logging.getLogger("visitkorea_mcp.clients.kto")


class KTOClient:
    def __init__(
        self,
        config: AppConfig,
        http_client: httpx.AsyncClient | None = None,
        cache: ResponseCache | None = None,
        rate_limiter: AsyncRateLimiter | None = None,
    ) -> None:
        self.config = config
        self._client = http_client
        self._owns_client = http_client is None
        self.cache = cache or ResponseCache()
        self.rate_limiter = rate_limiter or AsyncRateLimiter()

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
            raise UpstreamError("Korea Tourism API returned a malformed response.")
        header = body.get("header", {})
        if not isinstance(header, dict):
            raise UpstreamError("Korea Tourism API returned a malformed response.")
        code = str(header.get("resultCode", ""))
        msg = self._mask(str(header.get("resultMsg", "")))
        if code not in ("00", "0000"):
            if code == "03":
                return {"success": True, "resultCode": code, "resultMsg": msg,
                        "numOfRows": 0, "pageNo": 1, "totalCount": 0, "items": []}
            safe = {"10": "INVALID_REQUEST_PARAMETER", "11": "NO_MANDATORY_PARAMETERS",
                    "22": "RATE_LIMIT_EXCEEDED", "30": "SERVICE_KEY_NOT_REGISTERED",
                    "31": "SERVICE_KEY_EXPIRED"}.get(code, "UPSTREAM_ERROR")
            if code in ("30", "31"):
                raise PermissionError(safe)
            raise UpstreamError(safe)
        payload = body.get("body", {})
        if not isinstance(payload, dict):
            raise UpstreamError("Korea Tourism API returned a malformed response.")
        wrapper = payload.get("items") or {}
        if wrapper and not isinstance(wrapper, dict):
            raise UpstreamError("Korea Tourism API returned a malformed response.")
        raw = wrapper.get("item", []) if isinstance(wrapper, dict) else []
        return {"success": True, "resultCode": code, "resultMsg": msg,
                "numOfRows": payload.get("numOfRows", 0), "pageNo": payload.get("pageNo", 1),
                "totalCount": payload.get("totalCount", 0),
                "items": raw if isinstance(raw, list) else [raw]}

    async def call(self, endpoint: str, params: dict[str, Any] | None = None) -> dict:
        query: dict[str, Any] = {
            "MobileOS": MOBILE_OS, "MobileApp": MOBILE_APP,
            "_type": "json", "serviceKey": self.config.api_key,
        }
        query.update({key: value for key, value in (params or {}).items() if value is not None})
        if "numOfRows" in query:
            try:
                query["numOfRows"] = max(1, min(int(query["numOfRows"]), 100))
            except (TypeError, ValueError):
                query["numOfRows"] = 10
        key = make_key(endpoint, query)
        hit, value = self.cache.get(key)
        if hit:
            return value
        await self.rate_limiter.acquire()
        client = await self._http()
        for attempt in range(3):
            try:
                response = await client.get(
                    f"{self.config.base_url}/{endpoint}", params=query,
                )
                response.raise_for_status()
                break
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "error": "Korea Tourism API request timed out.",
                    "items": [],
                    "totalCount": 0,
                }
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500:
                    raise UpstreamError("Korea Tourism API rejected the request.") from None
                if attempt == 2:
                    raise UpstreamError(
                        "Korea Tourism API is temporarily unavailable."
                    ) from None
                await asyncio.sleep(0.5 * 2 ** attempt)
        try:
            result = self.parse_envelope(response.json())
        except (ValueError, TypeError):
            raise UpstreamError("Korea Tourism API returned an invalid response.") from None
        if result.get("success") and result.get("totalCount", 0) > 0:
            self.cache.set(key, result, ttl_for(endpoint))
        return result

    async def close(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
