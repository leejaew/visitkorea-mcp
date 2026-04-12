"""
TTL response cache for the VisitKorea MCP server.

Simple in-process dict-based cache; no external dependency.
Key = sha256(endpoint + params without serviceKey) so that the raw API key
never appears in cache keys or error messages.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any

# Per-endpoint TTL overrides (seconds).
# Reference data that rarely or never changes gets a 1-hour TTL.
# Live search / detail endpoints get a 5-minute TTL.
TTL_BY_ENDPOINT: dict[str, int] = {
    "ldongCode2":     3_600,
    "lclsSystmCode2": 3_600,
    "areaCode2":      3_600,
    "categoryCode2":  3_600,
}
DEFAULT_TTL = 300  # 5 minutes

_store: dict[str, tuple[float, Any]] = {}


def make_key(endpoint: str, params: dict) -> str:
    """Build a cache key that is safe to log (no API key)."""
    safe = {k: v for k, v in params.items() if k != "serviceKey"}
    blob = json.dumps(safe, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode()).hexdigest()[:16]
    return f"{endpoint}:{digest}"


def get(key: str) -> tuple[bool, Any]:
    """Return (hit, value). Evicts expired entries on access."""
    entry = _store.get(key)
    if entry and time.monotonic() < entry[0]:
        return True, entry[1]
    _store.pop(key, None)
    return False, None


def set(key: str, value: Any, ttl: int) -> None:
    """Store *value* under *key* for *ttl* seconds."""
    _store[key] = (time.monotonic() + ttl, value)


def ttl_for(endpoint: str) -> int:
    """Return the TTL (seconds) to use for a given endpoint."""
    return TTL_BY_ENDPOINT.get(endpoint, DEFAULT_TTL)
