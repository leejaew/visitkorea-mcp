"""
MCP Tool schema definitions for the four detail endpoints:
  get_tourism_common_info  → detailCommon2
  get_tourism_intro_info   → detailIntro2
  get_tourism_detail_info  → detailInfo2
  get_tourism_images       → detailImage2
"""
from mcp.types import Tool

_CONTENT_TYPE_DESC = (
    "75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event"
)
_CONTENT_TYPE_ENUM = ["75", "76", "78", "79", "80", "82", "85"]
_YN_ENUM = ["Y", "N"]

TOOLS = [
    Tool(
        name="get_tourism_common_info",
        description=(
            "Get common/overview information for a specific tourism content item by its content ID. "
            "Returns title, address, GPS coordinates, telephone, homepage URL, representative image, "
            "content type, overview description, copyright type, and classification codes. "
            "IMPORTANT: contentId must be obtained from an active search tool call in the same session "
            "(search_tourism_by_area, search_tourism_by_location, or search_tourism_by_keyword). "
            "Do not guess or invent content IDs — they will return empty results. "
            "If the response contains a 'hint' field, it explains why no data was returned."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "contentId": {
                    "type": "string",
                    "description": (
                        "Numeric content ID string from a search result (e.g. '264337'). "
                        "Must come from an active search call — do not guess."
                    ),
                },
                "contentTypeId": {
                    "type": "string",
                    "description": (
                        "Optional. Content type of the item — pass when known from the search result. "
                        + _CONTENT_TYPE_DESC
                    ),
                    "enum": _CONTENT_TYPE_ENUM,
                },
                "defaultYN": {"type": "string", "description": "Include default info (Y/N, default Y)", "enum": _YN_ENUM},
                "firstImageYN": {"type": "string", "description": "Include representative image (Y/N, default Y)", "enum": _YN_ENUM},
                "areacodeYN": {"type": "string", "description": "Include area code (Y/N, default Y)", "enum": _YN_ENUM},
                "catcodeYN": {"type": "string", "description": "Include category codes (Y/N, default Y)", "enum": _YN_ENUM},
                "addrinfoYN": {"type": "string", "description": "Include address details (Y/N, default Y)", "enum": _YN_ENUM},
                "mapinfoYN": {"type": "string", "description": "Include GPS coordinates (Y/N, default Y)", "enum": _YN_ENUM},
                "overviewYN": {"type": "string", "description": "Include overview description (Y/N, default Y)", "enum": _YN_ENUM},
            },
            "required": ["contentId"],
        },
    ),
    Tool(
        name="get_tourism_intro_info",
        description=(
            "Get introductory details for a tourism content item (by content ID and type). "
            "Returns type-specific intro fields: opening hours, admission fees, rest days, parking, "
            "facility info, age suitability, and other details that vary by content type. "
            "Requires both contentId and contentTypeId."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "contentId": {"type": "string", "description": "Content ID of the tourism item (from search results)."},
                "contentTypeId": {"type": "string", "description": _CONTENT_TYPE_DESC, "enum": _CONTENT_TYPE_ENUM},
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
            },
            "required": ["contentId", "contentTypeId"],
        },
    ),
    Tool(
        name="get_tourism_detail_info",
        description=(
            "Get detailed type-specific information for a tourism content item. "
            "Returns repeating detail fields that vary by content type, such as "
            "room types for accommodation, menu items for restaurants, or facility details. "
            "Requires both contentId and contentTypeId."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "contentId": {"type": "string", "description": "Content ID of the tourism item (from search results)."},
                "contentTypeId": {"type": "string", "description": _CONTENT_TYPE_DESC, "enum": _CONTENT_TYPE_ENUM},
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
            },
            "required": ["contentId", "contentTypeId"],
        },
    ),
    Tool(
        name="get_tourism_images",
        description=(
            "Get image gallery for a specific tourism content item. "
            "imageYN=Y returns venue photos; N returns food/menu photos (restaurants only). "
            "Returns URLs for all available images of the place."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "contentId": {"type": "string", "description": "Content ID of the tourism item (from search results)."},
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "imageYN": {
                    "type": "string",
                    "description": "Y=venue images (default), N=food/menu images (restaurants only)",
                    "enum": _YN_ENUM,
                },
            },
            "required": ["contentId"],
        },
    ),
]
