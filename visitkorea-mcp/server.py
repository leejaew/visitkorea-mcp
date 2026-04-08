"""
VisitKorea MCP Server
=====================
A Model Context Protocol (MCP) server that connects AI agents (Claude, Manus AI, etc.)
with the Korea Tourism Organization (한국관광공사) English Tourism Information Open Data API.

API Base: https://apis.data.go.kr/B551011/EngService2/
API Provider: Korea Tourism Organization via data.go.kr

Environment Variables:
  VISITKOREA_API_KEY  - Your service key from data.go.kr (URL-encoded)

Usage:
  python3 server.py              # stdio mode (for Claude Desktop / Manus AI stdio)
  python3 server.py --sse        # SSE mode  (for web-based MCP clients)
  python3 server.py --http       # Streamable HTTP mode
"""

import os
import sys
import json
import asyncio
import argparse
import httpx
from urllib.parse import urlencode
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://apis.data.go.kr/B551011/EngService2"
MOBILE_OS = "ETC"
MOBILE_APP = "VisitKoreaMCP"

CONTENT_TYPE_MAP = {
    "75": "Leisure/Sports (레포츠)",
    "76": "Tourist Attraction (관광지)",
    "78": "Cultural Facility (문화시설)",
    "79": "Shopping (쇼핑)",
    "80": "Accommodation (숙박)",
    "82": "Restaurant/Food (음식점)",
    "85": "Festival/Performance/Event (축제공연행사)",
}

# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------


def get_api_key() -> str:
    key = os.environ.get("VISITKOREA_API_KEY", "")
    if not key:
        raise RuntimeError(
            "VISITKOREA_API_KEY environment variable is not set. "
            "Please set your Korea Tourism Organization API service key."
        )
    return key


async def call_api(endpoint: str, params: dict[str, Any]) -> dict:
    """Call the VisitKorea Open API and return parsed JSON.

    The serviceKey is already URL-encoded in the environment variable, so we
    embed it directly in the URL string to avoid double-encoding by httpx.
    All other parameters are passed via httpx params (which handles encoding).
    """
    service_key = get_api_key()  # already URL-encoded from data.go.kr

    # Other fixed params (httpx will encode these)
    other_params: dict[str, Any] = {
        "MobileOS": MOBILE_OS,
        "MobileApp": MOBILE_APP,
        "_type": "json",
    }
    # Merge caller params, dropping None values
    for k, v in params.items():
        if v is not None:
            other_params[k] = v

    # Build the complete query string manually so the pre-encoded serviceKey
    # is not re-encoded by httpx (httpx replaces the entire query string when
    # params= is used, losing the pre-embedded serviceKey).
    query_string = "serviceKey=" + service_key + "&" + urlencode(other_params)
    url = f"{BASE_URL}/{endpoint}?{query_string}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url)

    # Handle HTTP errors gracefully
    if resp.status_code == 401:
        return {
            "success": False,
            "error": "Authentication failed. Please check your VISITKOREA_API_KEY.",
            "items": [],
            "totalCount": 0,
        }
    if resp.status_code >= 400:
        return {
            "success": False,
            "error": f"API returned HTTP {resp.status_code}: {resp.reason_phrase}",
            "items": [],
            "totalCount": 0,
        }

    data = resp.json()

    # Normalise response structure
    response = data.get("response", {})
    header = response.get("header", {})
    result_code = header.get("resultCode", "")
    result_msg = header.get("resultMsg", "")

    if result_code != "0000":
        return {
            "success": False,
            "resultCode": result_code,
            "resultMsg": result_msg,
            "items": [],
            "totalCount": 0,
        }

    body = response.get("body", {})
    items_wrapper = body.get("items", {})

    # items can be "" (empty string) when no results
    if not items_wrapper or items_wrapper == "":
        items = []
    else:
        raw = items_wrapper.get("item", [])
        items = raw if isinstance(raw, list) else [raw]

    return {
        "success": True,
        "resultCode": result_code,
        "resultMsg": result_msg,
        "numOfRows": body.get("numOfRows", 0),
        "pageNo": body.get("pageNo", 1),
        "totalCount": body.get("totalCount", 0),
        "items": items,
    }


def format_result(data: dict) -> str:
    """Return a clean JSON string for MCP tool output."""
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# MCP Server setup
# ---------------------------------------------------------------------------

server = Server("visitkorea-mcp")


# ---------------------------------------------------------------------------
# Tool: search_tourism_by_area
# ---------------------------------------------------------------------------
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
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
                    "lDongRegnCd": {
                        "type": "string",
                        "description": "Legal district province code filter.",
                    },
                    "lDongSignguCd": {
                        "type": "string",
                        "description": "Legal district city/county code filter (requires lDongRegnCd).",
                    },
                    "lclsSystm1": {
                        "type": "string",
                        "description": "Classification level-1 code filter.",
                    },
                    "lclsSystm2": {
                        "type": "string",
                        "description": "Classification level-2 code filter (requires lclsSystm1).",
                    },
                    "lclsSystm3": {
                        "type": "string",
                        "description": "Classification level-3 code filter (requires lclsSystm1 and lclsSystm2).",
                    },
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
                        "description": "Sort: A=title, C=modified date, D=created. For images only: O/Q/R",
                        "enum": ["A", "C", "D", "O", "Q", "R"],
                    },
                    "contentTypeId": {
                        "type": "string",
                        "description": "Filter by type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                        "enum": ["75", "76", "78", "79", "80", "82", "85"],
                    },
                    "lDongRegnCd": {
                        "type": "string",
                        "description": "Filter by province code. Use get_legal_district_codes to look up.",
                    },
                    "lDongSignguCd": {
                        "type": "string",
                        "description": "Filter by city/county code (requires lDongRegnCd).",
                    },
                    "lclsSystm1": {
                        "type": "string",
                        "description": "Classification level-1 filter.",
                    },
                    "lclsSystm2": {
                        "type": "string",
                        "description": "Classification level-2 filter (requires lclsSystm1).",
                    },
                    "lclsSystm3": {
                        "type": "string",
                        "description": "Classification level-3 filter (requires lclsSystm1 and lclsSystm2).",
                    },
                },
                "required": ["keyword"],
            },
        ),
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
                        "description": "Sort: A=title, C=modified, D=created. For images: O/Q/R",
                        "enum": ["A", "C", "D", "O", "Q", "R"],
                    },
                    "modifiedtime": {
                        "type": "string",
                        "description": "Filter by content modified date (YYYYMMDD).",
                    },
                    "lDongRegnCd": {
                        "type": "string",
                        "description": "Province code filter. Use get_legal_district_codes to look up.",
                    },
                    "lDongSignguCd": {
                        "type": "string",
                        "description": "City/county code filter (requires lDongRegnCd).",
                    },
                    "lclsSystm1": {
                        "type": "string",
                        "description": "Classification level-1 filter (e.g. 'EV' for events).",
                    },
                    "lclsSystm2": {
                        "type": "string",
                        "description": "Classification level-2 filter (requires lclsSystm1).",
                    },
                    "lclsSystm3": {
                        "type": "string",
                        "description": "Classification level-3 filter (requires lclsSystm1 and lclsSystm2).",
                    },
                },
                "required": ["eventStartDate"],
            },
        ),
        Tool(
            name="search_accommodations",
            description=(
                "Search Korean accommodations (hotels, pensions, hostels, motels, condominiums, camping, etc.). "
                "Returns a list with addresses, GPS coordinates, representative images, and content IDs. "
                "Use get_tourism_detail_intro for detailed accommodation info like room types and facilities."
            ),
            inputSchema={
                "type": "object",
                "properties": {
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
                        "description": "Sort: A=title, C=modified, D=created. For images: O/Q/R",
                        "enum": ["A", "C", "D", "O", "Q", "R"],
                    },
                    "modifiedtime": {
                        "type": "string",
                        "description": "Filter by modified date (YYYYMMDD).",
                    },
                    "lDongRegnCd": {
                        "type": "string",
                        "description": "Province code. Use get_legal_district_codes to look up. Example: '11'=Seoul",
                    },
                    "lDongSignguCd": {
                        "type": "string",
                        "description": "City/county code (requires lDongRegnCd).",
                    },
                    "lclsSystm1": {
                        "type": "string",
                        "description": "Classification level-1 filter (e.g. 'AC' for accommodation types).",
                    },
                    "lclsSystm2": {
                        "type": "string",
                        "description": "Classification level-2 filter (requires lclsSystm1).",
                    },
                    "lclsSystm3": {
                        "type": "string",
                        "description": "Classification level-3 filter (requires lclsSystm1 and lclsSystm2).",
                    },
                },
                "required": [],
            },
        ),
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
                },
                "required": ["contentId"],
            },
        ),
        Tool(
            name="get_tourism_intro_info",
            description=(
                "Get type-specific introduction/detail information for a tourism content item. "
                "Each content type returns unique fields: "
                "Tourist Attraction (76): heritage info, parking, restrooms, pet info; "
                "Cultural Facility (78): scale, age restrictions, parking, fee info; "
                "Festival/Event (85): venue, program, sponsor, ticket fee; "
                "Leisure/Sports (75): reservation info, rental equipment, capacity; "
                "Accommodation (80): check-in/out, number of rooms, cooking facilities, reservation method; "
                "Shopping (79): opening hours, rest days, credit cards, baby carriage; "
                "Restaurant (82): opening hours, rest days, speciality dishes, parking, reservation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contentId": {
                        "type": "string",
                        "description": "The unique content ID. Obtained from search results.",
                    },
                    "contentTypeId": {
                        "type": "string",
                        "description": (
                            "Content type ID (required): "
                            "75=Leisure/Sports, 76=Tourist Attraction, 78=Cultural Facility, "
                            "79=Shopping, 80=Accommodation, 82=Restaurant, 85=Festival/Event"
                        ),
                        "enum": ["75", "76", "78", "79", "80", "82", "85"],
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
                },
                "required": ["contentId", "contentTypeId"],
            },
        ),
        Tool(
            name="get_tourism_detail_info",
            description=(
                "Get repeating/additional detail information for a tourism content item by content ID and type. "
                "Returns type-specific repeated data such as: "
                "Tourist Attraction (76): nearby tourism info; "
                "Cultural Facility (78): usage plan items; "
                "Festival/Event (85): event program, sub-event info; "
                "Leisure/Sports (75): sub-facility info; "
                "Accommodation (80): room type details (room name, capacity, bathroom, TV, internet, price per night); "
                "Shopping (79): shopping items/products; "
                "Restaurant (82): menu items and prices. "
                "Use contentTypeId=80 with this tool to get room-level details for hotels."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contentId": {
                        "type": "string",
                        "description": "The unique content ID. Obtained from search results.",
                    },
                    "contentTypeId": {
                        "type": "string",
                        "description": (
                            "Content type ID (required): "
                            "75=Leisure/Sports, 76=Tourist Attraction, 78=Cultural Facility, "
                            "79=Shopping, 80=Accommodation, 82=Restaurant, 85=Festival/Event"
                        ),
                        "enum": ["75", "76", "78", "79", "80", "82", "85"],
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
                },
                "required": ["contentId", "contentTypeId"],
            },
        ),
        Tool(
            name="get_tourism_images",
            description=(
                "Get all images for a specific tourism content item by content ID. "
                "Returns image URLs (original and thumbnail) for all photos associated with the item. "
                "For restaurant content, use imageYN=N to get food/menu images instead of venue photos. "
                "Useful for building galleries or showing multiple views of an attraction, hotel, or restaurant."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contentId": {
                        "type": "string",
                        "description": "The unique content ID. Obtained from search results.",
                    },
                    "imageYN": {
                        "type": "string",
                        "description": "Y=content/venue images (default), N=food menu images (only for restaurant type 82)",
                        "enum": ["Y", "N"],
                        "default": "Y",
                    },
                    "numOfRows": {
                        "type": "integer",
                        "description": "Number of image results per page (default: 10)",
                        "default": 10,
                    },
                    "pageNo": {
                        "type": "integer",
                        "description": "Page number (default: 1)",
                        "default": 1,
                    },
                },
                "required": ["contentId"],
            },
        ),
        Tool(
            name="get_sync_list",
            description=(
                "Get a list of tourism content items that have been created or modified since a specific date. "
                "Useful for keeping local data in sync with the Korea Tourism Organization database. "
                "Returns content IDs, type, modification timestamps, and show/hide status. "
                "Use showflag=1 to only get currently visible content, or omit for all changes including deleted/hidden. "
                "oldContentid in the response is the previous content ID when a content was re-registered."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "modifiedtime": {
                        "type": "string",
                        "description": "Get content modified on or after this date (format: YYYYMMDD or YYYYMM or YYYY). Example: '20250101' for all changes since Jan 1, 2025.",
                    },
                    "showflag": {
                        "type": "string",
                        "description": "Display status filter: '1'=only visible content, '0'=only hidden/deleted content. Omit for all.",
                        "enum": ["1", "0"],
                    },
                    "arrange": {
                        "type": "string",
                        "description": "Sort: A=title, C=modified (newest first), D=created. For images only: O/Q/R",
                        "enum": ["A", "C", "D", "O", "Q", "R"],
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
                    "contentTypeId": {
                        "type": "string",
                        "description": "Filter by type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                        "enum": ["75", "76", "78", "79", "80", "82", "85"],
                    },
                    "oldContentid": {
                        "type": "string",
                        "description": "Previous content ID — use this for cursor-based sync to get data starting from a known previous ID.",
                    },
                    "lDongRegnCd": {
                        "type": "string",
                        "description": "Province code filter.",
                    },
                    "lDongSignguCd": {
                        "type": "string",
                        "description": "City/county code filter (requires lDongRegnCd).",
                    },
                    "lclsSystm1": {
                        "type": "string",
                        "description": "Classification level-1 filter.",
                    },
                    "lclsSystm2": {
                        "type": "string",
                        "description": "Classification level-2 filter.",
                    },
                    "lclsSystm3": {
                        "type": "string",
                        "description": "Classification level-3 filter.",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_legal_district_codes",
            description=(
                "Get Korean legal district (법정동, Beopjeongdong) codes for provinces and cities/counties. "
                "Use this to find the lDongRegnCd (province code) and lDongSignguCd (city/county code) "
                "needed for filtering other search tools. "
                "Call without parameters to get all provinces. "
                "Call with lDongRegnCd to get cities/counties within that province. "
                "Common province codes: 11=Seoul, 26=Busan, 27=Daegu, 28=Incheon, 29=Gwangju, "
                "30=Daejeon, 31=Ulsan, 36=Sejong, 41=Gyeonggi, 42=Gangwon, 43=Chungbuk, "
                "44=Chungnam, 45=Jeonbuk, 46=Jeonnam, 47=Gyeongbuk, 48=Gyeongnam, 50=Jeju"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "lDongRegnCd": {
                        "type": "string",
                        "description": "Province code to get cities/counties for. Leave empty to get all provinces.",
                    },
                    "lDongListYn": {
                        "type": "string",
                        "description": "N=look up code+name by lDongRegnCd (default), Y=return full list with all province+city fields",
                        "enum": ["N", "Y"],
                        "default": "N",
                    },
                    "numOfRows": {
                        "type": "integer",
                        "description": "Number of results per page (default: 100)",
                        "default": 100,
                    },
                    "pageNo": {
                        "type": "integer",
                        "description": "Page number (default: 1)",
                        "default": 1,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_classification_codes",
            description=(
                "Get the new classification system codes (분류체계) for Korean tourism content. "
                "The classification has 3 levels: level-1 (대분류), level-2 (중분류), level-3 (소분류). "
                "Use lclsSystmListYn=Y to get full hierarchy list, or N (default) to get specific code info. "
                "Main level-1 categories: AC=Accommodation, EV=Festivals/Performances/Events, "
                "EX=Experience Tourism, FO=Food, LC=Leisure/Sports, SH=Shopping, "
                "TR=Transportation, VE=Culture/Arts/History. "
                "Use these codes with lclsSystm1/2/3 parameters in search tools."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "lclsSystm1": {
                        "type": "string",
                        "description": "Level-1 category code. Example: 'AC'=Accommodation, 'EV'=Events, 'FO'=Food",
                    },
                    "lclsSystm2": {
                        "type": "string",
                        "description": "Level-2 sub-category code (requires lclsSystm1). Example: 'AC01'=Hotels",
                    },
                    "lclsSystm3": {
                        "type": "string",
                        "description": "Level-3 sub-sub-category code (requires lclsSystm1 and lclsSystm2). Example: 'AC010100'=Hotels",
                    },
                    "lclsSystmListYn": {
                        "type": "string",
                        "description": "Y=get full hierarchy list (shows all 3 levels), N=get specific code info (default: N)",
                        "enum": ["Y", "N"],
                        "default": "N",
                    },
                    "numOfRows": {
                        "type": "integer",
                        "description": "Number of results per page (default: 100)",
                        "default": 100,
                    },
                    "pageNo": {
                        "type": "integer",
                        "description": "Page number (default: 1)",
                        "default": 1,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_area_codes",
            description=(
                "Get the old-style area codes used by Korean tourism APIs. "
                "Call without parameters to get all 17 provinces/metropolitan cities (code 1-39). "
                "Call with areaCode to get the districts (시군구) within that province. "
                "These codes can be used as the 'areaCode' and 'sigunguCode' parameters "
                "in search_tourism_by_area, search_tourism_by_keyword, search_festivals_and_events, and search_accommodations. "
                "Province codes: 1=Seoul, 2=Incheon, 3=Daejeon, 4=Daegu, 5=Gwangju, 6=Busan, 7=Ulsan, "
                "8=Sejong, 31=Gyeonggi-do, 32=Gangwon-do, 33=Chungcheongbuk-do, 34=Chungcheongnam-do, "
                "35=Gyeongsangbuk-do, 36=Gyeongsangnam-do, 37=Jeonbuk-do, 38=Jeollanam-do, 39=Jeju-do"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "areaCode": {
                        "type": "string",
                        "description": "Province code to get districts for. Leave empty to get all 17 provinces.",
                    },
                    "numOfRows": {
                        "type": "integer",
                        "description": "Number of results per page (default: 50)",
                        "default": 50,
                    },
                    "pageNo": {
                        "type": "integer",
                        "description": "Page number (default: 1)",
                        "default": 1,
                    },
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
                    "cat1": {
                        "type": "string",
                        "description": "Level-1 category code (e.g. 'A01', 'A02'). Leave empty to get all level-1 categories.",
                    },
                    "cat2": {
                        "type": "string",
                        "description": "Level-2 category code (e.g. 'A0101'). Requires cat1. Get level-3 subcategories.",
                    },
                    "contentTypeId": {
                        "type": "string",
                        "description": "Filter to categories used by this content type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                        "enum": ["75", "76", "78", "79", "80", "82", "85"],
                    },
                    "numOfRows": {
                        "type": "integer",
                        "description": "Number of results per page (default: 100)",
                        "default": 100,
                    },
                    "pageNo": {
                        "type": "integer",
                        "description": "Page number (default: 1)",
                        "default": 1,
                    },
                },
                "required": [],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool call handler
# ---------------------------------------------------------------------------

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = await _dispatch_tool(name, arguments)
        return [TextContent(type="text", text=format_result(result))]
    except RuntimeError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]
    except httpx.HTTPError as e:
        return [TextContent(type="text", text=json.dumps({"error": f"HTTP error calling VisitKorea API: {str(e)}"}))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Unexpected error: {str(e)}"}))]


async def _dispatch_tool(name: str, args: dict) -> dict:
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

    elif name == "search_tourism_by_location":
        return await call_api("locationBasedList2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "mapX": args["mapX"],
            "mapY": args["mapY"],
            "radius": args["radius"],
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    elif name == "search_tourism_by_keyword":
        return await call_api("searchKeyword2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "keyword": args["keyword"],
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    elif name == "search_festivals_and_events":
        return await call_api("searchFestival2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "eventStartDate": args["eventStartDate"],
            "eventEndDate": args.get("eventEndDate"),
            "modifiedtime": args.get("modifiedtime"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    elif name == "search_accommodations":
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

    elif name == "get_tourism_common_info":
        return await call_api("detailCommon2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
        })

    elif name == "get_tourism_intro_info":
        return await call_api("detailIntro2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "contentTypeId": args["contentTypeId"],
        })

    elif name == "get_tourism_detail_info":
        return await call_api("detailInfo2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "contentTypeId": args["contentTypeId"],
        })

    elif name == "get_tourism_images":
        return await call_api("detailImage2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "imageYN": args.get("imageYN", "Y"),
        })

    elif name == "get_sync_list":
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

    elif name == "get_legal_district_codes":
        return await call_api("ldongCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongListYn": args.get("lDongListYn", "N"),
        })

    elif name == "get_classification_codes":
        return await call_api("lclsSystmCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
            "lclsSystmListYn": args.get("lclsSystmListYn", "N"),
        })

    elif name == "get_area_codes":
        return await call_api("areaCode2", {
            "numOfRows": args.get("numOfRows", 50),
            "pageNo": args.get("pageNo", 1),
            "areaCode": args.get("areaCode"),
        })

    elif name == "get_category_codes":
        return await call_api("categoryCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "cat1": args.get("cat1"),
            "cat2": args.get("cat2"),
            "contentTypeId": args.get("contentTypeId"),
        })

    else:
        return {"error": f"Unknown tool: {name}"}


# ---------------------------------------------------------------------------
# Transport entry points
# ---------------------------------------------------------------------------

async def run_stdio():
    """Run in stdio mode — for Claude Desktop, Manus AI stdio config."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run_sse(host: str = "0.0.0.0", port: int = 3000):
    """Run as an SSE server — for web-based MCP clients."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )

    print(f"VisitKorea MCP Server (SSE) running at http://{host}:{port}/sse")
    uvicorn.run(app, host=host, port=port)


def run_http(host: str = "0.0.0.0", port: int = 3001):
    """Run as a Streamable HTTP server."""
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_mcp(request):
        await session_manager.handle_request(request.scope, request.receive, request._send)

    async def lifespan(app):
        async with session_manager.run():
            yield

    app = Starlette(
        routes=[Route("/mcp", endpoint=handle_mcp, methods=["GET", "POST", "DELETE"])],
        lifespan=lifespan,
    )

    print(f"VisitKorea MCP Server (HTTP) running at http://{host}:{port}/mcp")
    uvicorn.run(app, host=host, port=port)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VisitKorea MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run in SSE mode")
    parser.add_argument("--http", action="store_true", help="Run in Streamable HTTP mode")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (SSE/HTTP modes)")
    parser.add_argument("--port", type=int, help="Port to listen on (SSE: 3000, HTTP: 3001)")
    args = parser.parse_args()

    if args.sse:
        port = args.port or int(os.environ.get("PORT", 3000))
        run_sse(host=args.host, port=port)
    elif args.http:
        port = args.port or int(os.environ.get("PORT", 3001))
        run_http(host=args.host, port=port)
    else:
        # Default: stdio mode (for Claude Desktop / Manus AI local use)
        asyncio.run(run_stdio())
