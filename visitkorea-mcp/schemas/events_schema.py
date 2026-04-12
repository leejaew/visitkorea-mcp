"""MCP Tool schema for search_festivals_and_events → searchFestival2."""
from mcp.types import Tool

TOOLS = [
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
                "eventEndDate": {"type": "string", "description": "Event end date in YYYYMMDD format. Example: '20261231'"},
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified, D=created. With images: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "modifiedtime": {"type": "string", "description": "Filter by content modified date (YYYYMMDD)."},
                "lDongRegnCd": {"type": "string", "description": "Province code filter. Use get_legal_district_codes."},
                "lDongSignguCd": {"type": "string", "description": "City/county code filter (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter (e.g. 'EV' for events)."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 + lclsSystm2)."},
            },
            "required": ["eventStartDate"],
        },
    ),
]
