"""Thin festival and event tool adapter."""
from __future__ import annotations

from typing import Any

from ..services.tourism import TourismService
from .schemas.events import TOOLS


async def handle(name: str, args: dict[str, Any], service: TourismService) -> dict | None:
    return await service.events(args) if name == "search_festivals_and_events" else None
