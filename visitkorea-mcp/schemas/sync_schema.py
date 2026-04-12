"""MCP Tool schema for get_sync_list → areaBasedSyncList2."""
from mcp.types import Tool

TOOLS = [
    Tool(
        name="get_sync_list",
        description=(
            "Retrieve tourism content updated since a given modification timestamp. "
            "Useful for incrementally syncing a local cached copy of KTO data. "
            "Returns content IDs, modification times, display flags, and old content IDs."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "modifiedtime": {"type": "string", "description": "Return items modified on/after this date (YYYYMMDD)."},
                "showflag": {
                    "type": "string",
                    "description": "Filter by display flag: '1'=displayed, '0'=hidden. Omit for all.",
                    "enum": ["0", "1"],
                },
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified, D=created. With images: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "contentTypeId": {
                    "type": "string",
                    "description": "Filter by type: 75=Leisure, 76=Attraction, 78=Cultural, 79=Shopping, 80=Stay, 82=Food, 85=Event",
                    "enum": ["75", "76", "78", "79", "80", "82", "85"],
                },
                "oldContentid": {"type": "string", "description": "Look up the new content ID for a given legacy content ID."},
                "lDongRegnCd": {"type": "string", "description": "Province code filter."},
                "lDongSignguCd": {"type": "string", "description": "City/county code filter (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 + lclsSystm2)."},
            },
            "required": [],
        },
    ),
]
