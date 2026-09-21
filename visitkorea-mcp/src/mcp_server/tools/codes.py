"""Thin reference code tool adapter."""
from __future__ import annotations

from typing import Any

from ..services.tourism import TourismService
from .schemas.codes import TOOLS


async def handle(name: str, args: dict[str, Any], service: TourismService) -> dict | None:
    return await service.codes(name, args)
