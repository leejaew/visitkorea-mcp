"""MCP Tool schema for search_accommodations → searchStay2."""
from mcp.types import Tool

TOOLS = [
    Tool(
        name="search_accommodations",
        description=(
            "Search Korean accommodations (hotels, pensions, hostels, motels, condominiums, camping, etc.). "
            "Returns a list with addresses, GPS coordinates, representative images, and content IDs. "
            "Use get_tourism_intro_info for detailed accommodation info like room types and facilities."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "numOfRows": {"type": "integer", "description": "Results per page (default 10)", "default": 10},
                "pageNo": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "arrange": {
                    "type": "string",
                    "description": "Sort: A=title, C=modified, D=created. With images: O/Q/R",
                    "enum": ["A", "C", "D", "O", "Q", "R"],
                },
                "modifiedtime": {"type": "string", "description": "Filter by modified date (YYYYMMDD)."},
                "lDongRegnCd": {"type": "string", "description": "Province code. Use get_legal_district_codes. Example: '11'=Seoul"},
                "lDongSignguCd": {"type": "string", "description": "City/county code (requires lDongRegnCd)."},
                "lclsSystm1": {"type": "string", "description": "Classification level-1 filter (e.g. 'AC' for accommodation types)."},
                "lclsSystm2": {"type": "string", "description": "Classification level-2 filter (requires lclsSystm1)."},
                "lclsSystm3": {"type": "string", "description": "Classification level-3 filter (requires lclsSystm1 + lclsSystm2)."},
            },
            "required": [],
        },
    ),
]
