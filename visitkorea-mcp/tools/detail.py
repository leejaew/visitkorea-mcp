"""
Detail tools — common info, intro info, type-specific detail, and images.

Tools:
  get_tourism_common_info  → detailCommon2
  get_tourism_intro_info   → detailIntro2
  get_tourism_detail_info  → detailInfo2
  get_tourism_images       → detailImage2
"""
from __future__ import annotations

from typing import Optional

from mcp.types import Tool

from utils.api_client import call_api

TOOLS = [
    Tool(
        name="get_tourism_common_info",
        description=(
            "Get common/overview information for a specific tourism content item by its content ID. "
            "Returns: title, address, GPS coordinates, telephone, homepage URL, representative images, "
            "content type, overview description, copyright type, and classification codes. "
            "Use this after finding a content ID from one of the search tools."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "contentId": {
                    "type": "string",
                    "description": "The unique content ID of the tourism item. Obtained from search results.",
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                "defaultYN": {"type": "string", "description": "Include default info (Y/N). Default: Y", "enum": ["Y", "N"]},
                "firstImageYN": {"type": "string", "description": "Include representative image (Y/N). Default: Y", "enum": ["Y", "N"]},
                "areacodeYN": {"type": "string", "description": "Include area code (Y/N). Default: Y", "enum": ["Y", "N"]},
                "catcodeYN": {"type": "string", "description": "Include category codes (Y/N). Default: Y", "enum": ["Y", "N"]},
                "addrinfoYN": {"type": "string", "description": "Include address details (Y/N). Default: Y", "enum": ["Y", "N"]},
                "mapinfoYN": {"type": "string", "description": "Include GPS coordinates (Y/N). Default: Y", "enum": ["Y", "N"]},
                "overviewYN": {"type": "string", "description": "Include overview description (Y/N). Default: Y", "enum": ["Y", "N"]},
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
                "contentId": {
                    "type": "string",
                    "description": "Content ID of the tourism item (from search results).",
                },
                "contentTypeId": {
                    "type": "string",
                    "description": "Content type ID: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
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
                "contentId": {
                    "type": "string",
                    "description": "Content ID of the tourism item (from search results).",
                },
                "contentTypeId": {
                    "type": "string",
                    "description": "Content type ID: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
            },
            "required": ["contentId", "contentTypeId"],
        },
    ),
    Tool(
        name="get_tourism_images",
        description=(
            "Get image gallery for a specific tourism content item. "
            "imageYN=Y returns venue photos; N returns food menu photos (restaurant type only). "
            "Returns URLs for all available images of the place."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "contentId": {
                    "type": "string",
                    "description": "Content ID of the tourism item (from search results).",
                },
                "numOfRows": {"type": "integer", "description": "Number of results per page (default: 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default: 1)", "default": 1},
                "imageYN": {
                    "type": "string",
                    "description": "Y=venue images (default), N=food/menu images (restaurants only)",
                    "enum": ["Y", "N"],
                },
            },
            "required": ["contentId"],
        },
    ),
]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "get_tourism_common_info":
        return await call_api("detailCommon2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "defaultYN": args.get("defaultYN", "Y"),
            "firstImageYN": args.get("firstImageYN", "Y"),
            "areacodeYN": args.get("areacodeYN", "Y"),
            "catcodeYN": args.get("catcodeYN", "Y"),
            "addrinfoYN": args.get("addrinfoYN", "Y"),
            "mapinfoYN": args.get("mapinfoYN", "Y"),
            "overviewYN": args.get("overviewYN", "Y"),
        })

    if name == "get_tourism_intro_info":
        return await call_api("detailIntro2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "contentTypeId": args["contentTypeId"],
        })

    if name == "get_tourism_detail_info":
        return await call_api("detailInfo2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "contentTypeId": args["contentTypeId"],
        })

    if name == "get_tourism_images":
        return await call_api("detailImage2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "imageYN": args.get("imageYN", "Y"),
        })

    return None
