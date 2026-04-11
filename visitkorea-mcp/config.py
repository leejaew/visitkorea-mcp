"""
Global constants for the VisitKorea MCP server.

All API endpoints are relative to BASE_URL.
"""

BASE_URL = "https://apis.data.go.kr/B551011/EngService2"

MOBILE_OS = "ETC"
MOBILE_APP = "VisitKoreaMCP"

CONTENT_TYPE_MAP: dict[str, str] = {
    "75": "Leisure/Sports (레포츠)",
    "76": "Tourist Attraction (관광지)",
    "78": "Cultural Facility (문화시설)",
    "79": "Shopping (쇼핑)",
    "80": "Accommodation (숙박)",
    "82": "Restaurant/Food (음식점)",
    "85": "Festival/Performance/Event (축제공연행사)",
}

CONTENT_TYPE_IDS = list(CONTENT_TYPE_MAP.keys())
