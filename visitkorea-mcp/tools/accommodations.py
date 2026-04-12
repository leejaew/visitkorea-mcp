"""
Accommodations tool handler — hotel and lodging search.

Schema definition lives in schemas/accommodations_schema.py.
"""
from __future__ import annotations

from typing import Optional

from schemas.accommodations_schema import TOOLS
from utils.api_client import call_api

__all__ = ["TOOLS", "handle"]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "search_accommodations":
        return await call_api("searchStay2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "modifiedtime": args.get("modifiedtime"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    return None
