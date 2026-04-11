"""
Events tool — festival and event search.

Tools:
  search_festivals_and_events → searchFestival2
"""
from __future__ import annotations

from typing import Optional

from mcp.types import Tool

from utils.api_client import call_api
from utils.validation import validate_date

TOOLS = [
    Tool(
        name="search_festivals_and_events",
        description=(
            "Search Korean festivals, performances, and events by date range. "
            "Returns event-specific information including start/end dates, venue, and descriptions. "
            "Requires an event start date. Optionally filter by province, district, or classification."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "eventStartDate": {
                    "type": "string",
                    "description": "Event start date in YYYYMMDD format. Required. Example: '20260101'",
                },
                "eventEndDate": {
                    "type": "string",
                    "description": "Event end date in YYYYMMDD format. Optional. Example: '20261231'",
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified, D=created. For images: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "modifiedtime": {"type": "string", "description": "Filter by content modified date (YYYYMMDD)."},
                "lDongRegnCd": {"type": "string", "description": "Province code filter. Use get_legal_district_codes to look up."},
                "lDongSignguCd": {"type": "string", "description": "City/county code filter (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter (e.g. 'EV' for events)."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 and lclsSystm2)."},
            },
            "required": ["eventStartDate"],
        },
    ),
]


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
