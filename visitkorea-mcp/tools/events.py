"""
Events tool handler — festival and event search.

Schema definition lives in schemas/events_schema.py.
"""
from __future__ import annotations

from typing import Optional

from schemas.events_schema import TOOLS
from utils.api_client import call_api
from utils.validation import validate_date

__all__ = ["TOOLS", "handle"]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "search_festivals_and_events":
        start = validate_date(args["eventStartDate"])
        end = args.get("eventEndDate")
        if end:
            end = validate_date(end)
        return await call_api("searchFestival2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "eventStartDate": start,
            "eventEndDate": end,
            "modifiedtime": args.get("modifiedtime"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    return None
