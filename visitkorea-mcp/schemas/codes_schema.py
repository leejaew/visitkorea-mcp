"""
MCP Tool schema definitions for the four reference code lookup endpoints:
  get_legal_district_codes  → ldongCode2
  get_classification_codes  → lclsSystmCode2
  get_area_codes            → areaCode2
  get_category_codes        → categoryCode2
"""
from mcp.types import Tool

TOOLS = [
    Tool(
        name="get_legal_district_codes",
        description=(
            "Look up legal administrative district codes (lDongRegnCd / lDongSignguCd) "
            "for use with area-based and location-based search tools. "
            "Without parameters returns all 17 province-level codes. "
            "Pass lDongRegnCd to get city/county codes within a province."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lDongRegnCd": {"type": "string", "description": "Province code. Pass to get city/county codes. Example: '11'=Seoul."},
                "lDongListYn": {"type": "string", "description": "Y=full flat list, N=paginated (default N)", "enum": ["Y", "N"]},
                "numOfRows": {"type": "integer", "description": "Results per page (default 100)", "default": 100},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
            },
            "required": [],
        },
    ),
    Tool(
        name="get_classification_codes",
        description=(
            "Get the new-style tourism classification system codes (lclsSystm1/2/3 hierarchy). "
            "Used with search_tourism_by_area, by_location, by_keyword, search_accommodations, and get_sync_list. "
            "Without parameters returns all level-1 codes. "
            "Pass lclsSystm1 for level-2, lclsSystm1+lclsSystm2 for level-3."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "lclsSystm1": {"type": "string", "description": "Level-1 code. Pass to get level-2 subcodes."},
                "lclsSystm2": {"type": "string", "description": "Level-2 code (requires lclsSystm1). Pass to get level-3 subcodes."},
                "lclsSystm3": {"type": "string", "description": "Level-3 code (requires lclsSystm1 + lclsSystm2)."},
                "lclsSystmListYn": {"type": "string", "description": "Y=full flat list, N=paginated (default N)", "enum": ["Y", "N"]},
                "numOfRows": {"type": "integer", "description": "Results per page (default 100)", "default": 100},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
            },
            "required": [],
        },
    ),
    Tool(
        name="get_area_codes",
        description=(
            "Get old-style province/district area codes (areaCode / sigunguCode) "
            "used with the areaCode and sigunguCode parameters in search tools. "
            "Without parameters returns all 17 province codes. "
            "Pass areaCode to get sub-district codes. Examples: 1=Seoul, 6=Busan, 39=Jeju-do."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "areaCode": {"type": "string", "description": "Province code. Pass to get district codes within a province."},
                "numOfRows": {"type": "integer", "description": "Results per page (default 50)", "default": 50},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
            },
            "required": [],
        },
    ),
    Tool(
        name="get_category_codes",
        description=(
            "Get old-style content category codes (cat1/cat2/cat3 hierarchy). "
            "Use these with cat1/cat2/cat3 parameters in search_tourism_by_area, "
            "search_tourism_by_location, and search_tourism_by_keyword. "
            "Level-1 (cat1): A01=Nature, A02=Culture/Art/History, A03=Leisure/Sports, "
            "A04=Shopping, A05=Cuisine, B02=Accommodation. "
            "Pass cat1 for level-2 codes, cat1+cat2 for level-3."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "cat1": {"type": "string", "description": "Level-1 code (e.g. 'A01'=Nature). Leave empty for all level-1 categories."},
                "cat2": {"type": "string", "description": "Level-2 code (e.g. 'A0101'). Requires cat1."},
                "contentTypeId": {
                    "type": "string",
                    "description": "Filter by content type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "numOfRows": {"type": "integer", "description": "Results per page (default 100)", "default": 100},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
            },
            "required": [],
        },
    ),
]
