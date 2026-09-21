"""Validated process configuration and application constants."""
from __future__ import annotations

import os
import urllib.parse
from dataclasses import dataclass, field

from ..errors import ConfigurationError

BASE_URL = "https://apis.data.go.kr/B551011/EngService2"
MOBILE_OS = "ETC"
MOBILE_APP = "VisitKoreaMCP"
CONTENT_TYPE_MAP: dict[str, str] = {
    "75": "Leisure/Sports (레포츠)",
    "76": "Tourist Attraction (관광지)",
    "78": "Cultural Facility (문화시설)",
    "79": "Shopping (쇼핑)",
    "80": "Accommodation (숙박)",
    "82": "Restaurant/Food (음식점)",
    "85": "Festival/Performance/Event (축제공연행사)",
}
CONTENT_TYPE_IDS = list(CONTENT_TYPE_MAP)


@dataclass(frozen=True)
class AppConfig:
    """Validated process configuration, constructed once at startup."""

    api_key: str = field(repr=False)
    base_url: str = BASE_URL
    timeout_seconds: float = 30.0
    host: str = "127.0.0.1"
    port: int = 3001

    @classmethod
    def from_env(cls) -> "AppConfig":
        raw = os.environ.get("VISITKOREA_API_KEY", "").strip()
        if not raw:
            raise ConfigurationError("VISITKOREA_API_KEY is required")
        try:
            port = int(os.environ.get("PORT", "3001"))
            timeout = float(os.environ.get("VISITKOREA_TIMEOUT", "30"))
        except ValueError as exc:
            raise ConfigurationError("PORT and VISITKOREA_TIMEOUT must be valid numbers") from exc
        if not 1 <= port <= 65535 or timeout <= 0:
            raise ConfigurationError("PORT or VISITKOREA_TIMEOUT is out of range")
        return cls(api_key=urllib.parse.unquote(raw), timeout_seconds=timeout, port=port)
