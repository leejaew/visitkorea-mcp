"""Thin tourism detail tool adapter."""
from __future__ import annotations

from typing import Any

from ..services.tourism import TourismService
from .schemas.detail import TOOLS


async def handle(name: str, args: dict[str, Any], service: TourismService) -> dict | None:
    return await service.detail(name, args)
