"""
Search tools — area-based, location-based, and keyword search.

Tools:
  search_tourism_by_area      → areaBasedList2
  search_tourism_by_location  → locationBasedList2
  search_tourism_by_keyword   → searchKeyword2
"""
from __future__ import annotations

from typing import Any, Optional

from mcp.types import Tool

from utils.api_client import call_api
from utils.validation import validate_gps, validate_radius

TOOLS = [
    Tool(
        name="search_tourism_by_area",
        description=(
            "Search Korean tourism attractions, restaurants, accommodations, shopping, "
            "cultural facilities, leisure spots, and festivals by geographic area (province/city). "
            "Returns a paginated list with addresses, GPS coordinates, representative images, "
            "and content IDs. Use lDongRegnCd to filter by province and lDongSignguCd for district. "
            "Use contentTypeId to filter by tourism type. "
            "Content Types: 75=Leisure/Sports, 76=Tourist Attraction, 78=Cultural Facility, "
            "79=Shopping, 80=Accommodation, 82=Restaurant, 85=Festival/Performance/Event."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "numOfRows": {
                    "type": "integer",
                    "description": "Number of results per page (default: 10, max: 100)",
                    "default": 10,
                },
                "pageNo": {
                    "type": "integer",
                    "description": "Page number (default: 1)",
                    "default": 1,
                },
                "arrange": {
                    "type": "string",
                    "description": (
                        "Sort order: A=by title, C=by modified date (newest first), "
                        "D=by created date. For results with images only: O=title, "
                        "Q=modified, R=created. Default: C"
                    ),
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "contentTypeId": {
                    "type": "string",
                    "description": (
                        "Tourism content type ID. "
                        "75=Leisure/Sports, 76=Tourist Attraction, 78=Cultural Facility, "
                        "79=Shopping, 80=Accommodation, 82=Restaurant, 85=Festival/Event"
                    ),
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "lDongRegnCd": {
                    "type": "string",
                    "description": (
                        "Legal district province code. Use get_legal_district_codes tool "
                        "to look up codes. Example: '11'=Seoul, '26'=Busan, '41'=Gyeonggi"
                    ),
                },
                "lDongSignguCd": {
                    "type": "string",
                    "description": (
                        "Legal district city/county code (requires lDongRegnCd). "
                        "Use get_legal_district_codes tool to look up codes."
                    ),
                },
                "lclsSystm1": {
                    "type": "string",
                    "description": "Classification system level-1 code (e.g. 'AC', 'EV', 'EX'). Use get_classification_codes tool to look up.",
                },
                "lclsSystm2": {
                    "type": "string",
                    "description": "Classification system level-2 code (requires lclsSystm1).",
                },
                "lclsSystm3": {
                    "type": "string",
                    "description": "Classification system level-3 code (requires lclsSystm1 and lclsSystm2).",
                },
                "modifiedtime": {
                    "type": "string",
                    "description": "Filter by modified date (format: YYYYMMDD). Returns items modified on or after this date.",
                },
                "areaCode": {
                    "type": "string",
                    "description": "Old-style province code (alternative to lDongRegnCd). Use get_area_codes tool to look up. Example: '1'=Seoul, '6'=Busan, '39'=Jeju-do",
                },
                "sigunguCode": {
                    "type": "string",
                    "description": "Old-style district code within province (requires areaCode). Use get_area_codes tool to look up.",
                },
                "cat1": {
                    "type": "string",
                    "description": "Old-style category level-1 code (e.g. 'A01'=Nature, 'A02'=Culture/Art/History). Use get_category_codes tool to look up.",
                },
                "cat2": {
                    "type": "string",
                    "description": "Old-style category level-2 code (e.g. 'A0201'=Historical Sites). Requires cat1.",
                },
                "cat3": {
                    "type": "string",
                    "description": "Old-style category level-3 code (e.g. 'A02010100'=Palaces). Requires cat1 and cat2.",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="search_tourism_by_location",
        description=(
            "Search Korean tourism attractions near a specific GPS location (latitude/longitude). "
            "Returns results within the specified radius, sorted by distance. "
            "Ideal for 'things to do near me' or 'attractions near [location]' queries. "
            "Content Types: 75=Leisure/Sports, 76=Tourist Attraction, 78=Cultural Facility, "
            "79=Shopping, 80=Accommodation, 82=Restaurant, 85=Festival/Performance/Event."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "mapX": {
                    "type": "number",
                    "description": "GPS longitude (WGS84). Example: 126.9784 for central Seoul.",
                },
                "mapY": {
                    "type": "number",
                    "description": "GPS latitude (WGS84). Example: 37.5665 for central Seoul.",
                },
                "radius": {
                    "type": "integer",
                    "description": "Search radius in meters (max: 20000). Example: 5000 for 5km.",
                },
                "numOfRows": {
                    "type": "integer",
                    "description": "Number of results per page (default: 10)",
                    "default": 10,
                },
                "pageNo": {
                    "type": "integer",
                    "description": "Page number (default: 1)",
                    "default": 1,
                },
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified date, D=created date. For image-only: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "contentTypeId": {
                    "type": "string",
                    "description": "Tourism type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "lDongRegnCd": {"type": "string", "description": "Legal district province code filter."},
                "lDongSignguCd": {"type": "string", "description": "Legal district city/county code filter (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 code filter."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 code filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 code filter (requires lclsSystm1 and lclsSystm2)."},
            },
            "required": ["mapX", "mapY", "radius"],
        },
    ),
    Tool(
        name="search_tourism_by_keyword",
        description=(
            "Search Korean tourism information by keyword (English). "
            "Searches across all content types including attractions, restaurants, accommodations, "
            "shopping, events, and cultural facilities. Returns paginated results with addresses, "
            "GPS coordinates, and images. "
            "Content Types: 75=Leisure/Sports, 76=Tourist Attraction, 78=Cultural Facility, "
            "79=Shopping, 80=Accommodation, 82=Restaurant, 85=Festival/Performance/Event."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search keyword in English. Example: 'Gyeongbokgung', 'Jeju', 'temple', 'market'",
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified date, D=created. For images only: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "contentTypeId": {
                    "type": "string",
                    "description": "Filter by type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "lDongRegnCd": {"type": "string", "description": "Filter by province code. Use get_legal_district_codes to look up."},
                "lDongSignguCd": {"type": "string", "description": "Filter by city/county code (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 and lclsSystm2)."},
            },
            "required": ["keyword"],
        },
    ),
]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "search_tourism_by_area":
        return await call_api("areaBasedList2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
            "modifiedtime": args.get("modifiedtime"),
            "areaCode": args.get("areaCode"),
            "sigunguCode": args.get("sigunguCode"),
            "cat1": args.get("cat1"),
            "cat2": args.get("cat2"),
            "cat3": args.get("cat3"),
        })

    if name == "search_tourism_by_location":
        map_x, map_y = validate_gps(args["mapX"], args["mapY"])
        radius = validate_radius(args["radius"])
        return await call_api("locationBasedList2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "mapX": map_x,
            "mapY": map_y,
            "radius": radius,
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    if name == "search_tourism_by_keyword":
        return await call_api("searchKeyword2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "keyword": args.get("keyword"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    return None
