"""Thin accommodation tool adapter."""
from __future__ import annotations

from typing import Any

from ..services.tourism import TourismService
from .schemas.accommodations import TOOLS


async def handle(name: str, args: dict[str, Any], service: TourismService) -> dict | None:
    return await service.accommodations(args) if name == "search_accommodations" else None
