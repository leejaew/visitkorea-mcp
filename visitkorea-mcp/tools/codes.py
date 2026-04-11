"""
Reference code lookup tools — all responses are cached for 1 hour.

Tools:
  get_legal_district_codes  → ldongCode2
  get_classification_codes  → lclsSystmCode2
  get_area_codes            → areaCode2
  get_category_codes        → categoryCode2
"""
from __future__ import annotations

from typing import Optional

from mcp.types import Tool

from utils.api_client import call_api

TOOLS = [
    Tool(
        name="get_legal_district_codes",
        description=(
            "Look up legal administrative district codes (lDongRegnCd / lDongSignguCd) "
            "for use with area-based and location-based search tools. "
            "Without parameters, returns all 17 province-level codes. "
            "Pass lDongRegnCd to get city/county codes within a province."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lDongRegnCd": {
                    "type": "string",
                    "description": "Province code. Pass to get city/county codes within a province. Example: '11' for Seoul.",
                },
                "lDongListYn": {
                    "type": "string",
                    "description": "Y=return full flat list, N=return paginated (default: N)",
                    "enum": ["Y", "N"],
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 100)", "default": 100},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
            },
            "required": [],
        },
    ),
    Tool(
        name="get_classification_codes",
        description=(
            "Get the new-style tourism classification system codes (lclsSystm1/2/3 hierarchy). "
            "These codes are used with search_tourism_by_area, search_tourism_by_location, "
            "search_tourism_by_keyword, search_accommodations, and get_sync_list. "
            "Without parameters, returns all level-1 codes. "
            "Pass lclsSystm1 to drill into level-2 codes, then lclsSystm1+lclsSystm2 for level-3."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lclsSystm1": {"type": "string", "description": "Level-1 code. Pass to get level-2 subcodes."},
                "lclsSystm2": {"type": "string", "description": "Level-2 code (requires lclsSystm1). Pass to get level-3 subcodes."},
                "lclsSystm3": {"type": "string", "description": "Level-3 code (requires lclsSystm1 and lclsSystm2)."},
                "lclsSystmListYn": {
                    "type": "string",
                    "description": "Y=return full flat list, N=return paginated (default: N)",
                    "enum": ["Y", "N"],
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 100)", "default": 100},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
            },
            "required": [],
        },
    ),
    Tool(
        name="get_area_codes",
        description=(
            "Get old-style province/district area codes (areaCode / sigunguCode) "
            "used with the areaCode and sigunguCode parameters in search tools. "
            "Without parameters, returns all 17 province codes. "
            "Pass areaCode to get sub-district (sigungu) codes within a province. "
            "Examples: 1=Seoul, 6=Busan, 39=Jeju-do."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "areaCode": {
                    "type": "string",
                    "description": "Province code to get districts for. Leave empty to get all 17 provinces.",
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 50)", "default": 50},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
            },
            "required": [],
        },
    ),
    Tool(
        name="get_category_codes",
        description=(
            "Get the old-style content category codes (cat1/cat2/cat3 hierarchy) used by Korean tourism APIs. "
            "The category hierarchy has 3 levels. Use these codes with cat1/cat2/cat3 parameters in "
            "search_tourism_by_area, search_tourism_by_location, and search_tourism_by_keyword. "
            "Optionally filter by contentTypeId to see which categories apply to a content type. "
            "Level-1 (cat1) categories: A01=Nature, A02=Culture/Art/History, A03=Leisure/Sports, "
            "A04=Shopping, A05=Cuisine, B01=Transportation, B02=Accommodation. "
            "Drill deeper: use cat1 to get level-2 codes, then cat1+cat2 to get level-3 codes."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "cat1": {"type": "string", "description": "Level-1 category code (e.g. 'A01', 'A02'). Leave empty to get all level-1 categories."},
                "cat2": {"type": "string", "description": "Level-2 category code (e.g. 'A0101'). Requires cat1. Get level-3 subcategories."},
                "contentTypeId": {
                    "type": "string",
                    "description": "Filter to categories used by this content type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 100)", "default": 100},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
            },
            "required": [],
        },
    ),
]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "get_legal_district_codes":
        return await call_api("ldongCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongListYn": args.get("lDongListYn", "N"),
        })

    if name == "get_classification_codes":
        return await call_api("lclsSystmCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
            "lclsSystmListYn": args.get("lclsSystmListYn", "N"),
        })

    if name == "get_area_codes":
        return await call_api("areaCode2", {
            "numOfRows": args.get("numOfRows", 50),
            "pageNo": args.get("pageNo", 1),
            "areaCode": args.get("areaCode"),
        })

    if name == "get_category_codes":
        return await call_api("categoryCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "cat1": args.get("cat1"),
            "cat2": args.get("cat2"),
            "contentTypeId": args.get("contentTypeId"),
        })

    return None
