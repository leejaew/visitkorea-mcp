"""
MCP Tool schema definitions for the three search endpoints:
  search_tourism_by_area      → areaBasedList2
  search_tourism_by_location  → locationBasedList2
  search_tourism_by_keyword   → searchKeyword2
"""
from mcp.types import Tool

_CONTENT_TYPE_DESC = (
    "75=Leisure/Sports, 76=Tourist Attraction, 78=Cultural Facility, "
    "79=Shopping, 80=Accommodation, 82=Restaurant, 85=Festival/Event"
)
_CONTENT_TYPE_ENUM = ["75", "76", "78", "79", "80", "82", "85"]
_ARRANGE_ENUM = ["A", "C", "D", "O", "Q", "R"]

TOOLS = [
    Tool(
        name="search_tourism_by_area",
        description=(
            "Search Korean tourism attractions, restaurants, accommodations, shopping, "
            "cultural facilities, leisure spots, and festivals by geographic area (province/city). "
            "Returns a paginated list with addresses, GPS coordinates, representative images, "
            "and content IDs. Use lDongRegnCd to filter by province and lDongSignguCd for district. "
            f"Content Types: {_CONTENT_TYPE_DESC}."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "numOfRows": {"type": "integer", "description": "Results per page (default 10, max 100)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified (newest first), D=created. With images only: O/Q/R",
                    "enum": _ARRANGE_ENUM,
                },
                "contentTypeId": {"type": "string", "description": _CONTENT_TYPE_DESC, "enum": _CONTENT_TYPE_ENUM},
                "lDongRegnCd": {
                    "type": "string",
                    "description": "Province code. Use get_legal_district_codes to look up. Example: '11'=Seoul, '26'=Busan",
                },
                "lDongSignguCd": {
                    "type": "string",
                    "description": "City/county code (requires lDongRegnCd). Use get_legal_district_codes to look up.",
                },
                "lclsSystm1": {"type": "string", "description": "Classification level-1 (e.g. 'AC', 'EV'). Use get_classification_codes."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 (requires lclsSystm1 + lclsSystm2)."},
                "modifiedtime": {"type": "string", "description": "Filter by modified date (YYYYMMDD). Returns items modified on/after."},
                "areaCode": {"type": "string", "description": "Old-style province code. Use get_area_codes. Example: '1'=Seoul, '39'=Jeju"},
                "sigunguCode": {"type": "string", "description": "Old-style district code (requires areaCode)."},
                "cat1": {"type": "string", "description": "Category level-1 (e.g. 'A01'=Nature, 'A02'=Culture). Use get_category_codes."},
                "cat2": {"type": "string", "description": "Category level-2 (e.g. 'A0201'=Historical Sites). Requires cat1."},
                "cat3": {"type": "string", "description": "Category level-3 (e.g. 'A02010100'=Palaces). Requires cat1 + cat2."},
            },
            "required": [],
        },
    ),
    Tool(
        name="search_tourism_by_location",
        description=(
            "Search Korean tourism attractions near a specific GPS location (WGS84). "
            "Returns results within the specified radius, sorted by distance. "
            f"Content Types: {_CONTENT_TYPE_DESC}."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "mapX": {"type": "number", "description": "GPS longitude (WGS84). Example: 126.9784 for central Seoul."},
                "mapY": {"type": "number", "description": "GPS latitude (WGS84). Example: 37.5665 for central Seoul."},
                "radius": {"type": "integer", "description": "Search radius in metres (max 20000). Example: 5000 = 5 km."},
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "arrange": {"type": "string", "description": "Sort: A=title, C=modified, D=created. With images: O/Q/R", "enum": _ARRANGE_ENUM},
                "contentTypeId": {"type": "string", "description": _CONTENT_TYPE_DESC, "enum": _CONTENT_TYPE_ENUM},
                "lDongRegnCd": {"type": "string", "description": "Province code filter."},
                "lDongSignguCd": {"type": "string", "description": "City/county code filter (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 + lclsSystm2)."},
            },
            "required": ["mapX", "mapY", "radius"],
        },
    ),
    Tool(
        name="search_tourism_by_keyword",
        description=(
            "Search Korean tourism information by English keyword. "
            "Searches across all content types: attractions, restaurants, accommodations, "
            "shopping, events, and cultural facilities. "
            f"Content Types: {_CONTENT_TYPE_DESC}."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "English keyword. Example: 'Gyeongbokgung', 'Jeju', 'temple', 'market'"},
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "arrange": {"type": "string", "description": "Sort: A=title, C=modified, D=created. With images: O/Q/R", "enum": _ARRANGE_ENUM},
                "contentTypeId": {"type": "string", "description": _CONTENT_TYPE_DESC, "enum": _CONTENT_TYPE_ENUM},
                "lDongRegnCd": {"type": "string", "description": "Province code filter."},
                "lDongSignguCd": {"type": "string", "description": "City/county code filter (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 + lclsSystm2)."},
            },
            "required": ["keyword"],
        },
    ),
]
