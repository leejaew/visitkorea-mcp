"""Thin incremental sync tool adapter."""
from __future__ import annotations

from typing import Any

from ..services.tourism import TourismService
from .schemas.sync import TOOLS


async def handle(name: str, args: dict[str, Any], service: TourismService) -> dict | None:
    return await service.sync(args) if name == "get_sync_list" else None
