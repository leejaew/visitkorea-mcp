"""Instance-owned TTL response cache.

Cache keys deliberately omit the upstream credential and contain only a
canonical hash of the endpoint and non-secret request parameters.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any


class ResponseCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> tuple[bool, Any]:
        entry = self._store.get(key)
        if entry is None:
            return False, None
        expires, value = entry
        if expires <= time.monotonic():
            self._store.pop(key, None)
            return False, None
        return True, value

    def set(self, key: str, value: Any, ttl: float) -> None:
        self._store[key] = (time.monotonic() + ttl, value)

    def clear(self) -> None:
        self._store.clear()


def make_key(endpoint: str, params: dict[str, Any]) -> str:
    safe = {
        key: value
        for key, value in params.items()
        if key not in {"serviceKey", "VISITKOREA_API_KEY"} and value is not None
    }
    blob = json.dumps(safe, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
    return f"{endpoint}:{digest}"


def ttl_for(endpoint: str) -> int:
    return 3600 if endpoint in {
        "ldongCode2", "lclsSystmCode2", "areaCode2", "categoryCode2",
    } else 300
