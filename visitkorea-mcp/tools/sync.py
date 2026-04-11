"""
Sync tool — delta sync list for incremental data updates.

Tools:
  get_sync_list → areaBasedSyncList2
"""
from __future__ import annotations

from typing import Optional

from mcp.types import Tool

from utils.api_client import call_api

TOOLS = [
    Tool(
        name="get_sync_list",
        description=(
            "Retrieve tourism content updated since a given modification timestamp. "
            "Useful for incrementally syncing a local cached copy of KTO data. "
            "Returns content IDs, modification times, display flags, and old content IDs."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                "modifiedtime": {
                    "type": "string",
                    "description": "Return only items modified on or after this date (YYYYMMDD). Omit for full list.",
                },
                "showflag": {
                    "type": "string",
                    "description": "Filter by display flag: '1'=displayed, '0'=hidden. Omit for all.",
                    "enum": ["0", "1"],
                },
                "arrange": {
                    "type": "string",
                    "description": "Sort order: A=title, C=modified, D=created. For images: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "contentTypeId": {
                    "type": "string",
                    "description": "Filter by content type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "oldContentid": {
                    "type": "string",
                    "description": "Look up the new content ID for a given legacy content ID.",
                },
                "lDongRegnCd": {"type": "string", "description": "Filter by province code."},
                "lDongSignguCd": {"type": "string", "description": "Filter by city/county code (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 and lclsSystm2)."},
            },
            "required": [],
        },
    ),
]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "get_sync_list":
        return await call_api("areaBasedSyncList2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "modifiedtime": args.get("modifiedtime"),
            "showflag": args.get("showflag"),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "oldContentid": args.get("oldContentid"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    return None
