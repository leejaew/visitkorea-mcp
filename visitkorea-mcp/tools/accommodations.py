"""
Accommodations tool — hotel and lodging search.

Tools:
  search_accommodations → searchStay2
"""
from __future__ import annotations

from typing import Optional

from mcp.types import Tool

from utils.api_client import call_api

TOOLS = [
    Tool(
        name="search_accommodations",
        description=(
            "Search Korean accommodations (hotels, pensions, hostels, motels, condominiums, camping, etc.). "
            "Returns a list with addresses, GPS coordinates, representative images, and content IDs. "
            "Use get_tourism_intro_info for detailed accommodation info like room types and facilities."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified, D=created. For images: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "modifiedtime": {"type": "string", "description": "Filter by modified date (YYYYMMDD)."},
                "lDongRegnCd": {"type": "string", "description": "Province code. Use get_legal_district_codes to look up. Example: '11'=Seoul"},
                "lDongSignguCd": {"type": "string", "description": "City/county code (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter (e.g. 'AC' for accommodation types)."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 and lclsSystm2)."},
            },
            "required": [],
        },
    ),
]


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
