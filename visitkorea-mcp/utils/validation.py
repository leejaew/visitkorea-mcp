"""
Input validation for MCP tool parameters.

Validates and sanitises values before they are forwarded to the upstream
data.go.kr API. Invalid inputs are rejected early with a clear error message
rather than producing cryptic upstream API error codes.
"""
from __future__ import annotations

import re

VALID_ARRANGE_CODES = frozenset({"A", "C", "D", "O", "Q", "R"})

# WGS84 bounding box for South Korea
_LON_MIN, _LON_MAX = 124.0, 132.0
_LAT_MIN, _LAT_MAX = 33.0, 39.0


def validate_pagination(num_of_rows: int, page_no: int) -> tuple[int, int]:
    """Clamp numOfRows to [1, 100] and pageNo to >= 1."""
    num_of_rows = max(1, min(int(num_of_rows), 100))
    page_no = max(1, int(page_no))
    return num_of_rows, page_no


def validate_radius(radius: int) -> int:
    """Enforce the API's 20 km hard maximum and reject non-positive values."""
    r = int(radius)
    if not (1 <= r <= 20_000):
        raise ValueError(
            f"radius must be between 1 and 20,000 metres, got {radius}."
        )
    return r


def validate_gps(map_x: float, map_y: float) -> tuple[float, float]:
    """Validate WGS84 coordinates are within South Korea's bounding box."""
    x, y = float(map_x), float(map_y)
    if not (_LON_MIN <= x <= _LON_MAX):
        raise ValueError(
            f"mapX (longitude) {x} is outside South Korea bounds "
            f"({_LON_MIN}–{_LON_MAX})."
        )
    if not (_LAT_MIN <= y <= _LAT_MAX):
        raise ValueError(
            f"mapY (latitude) {y} is outside South Korea bounds "
            f"({_LAT_MIN}–{_LAT_MAX})."
        )
    return x, y


def validate_date(date_str: str) -> str:
    """Validate YYYYMMDD format."""
    s = date_str.strip()
    if not re.fullmatch(r"\d{8}", s):
        raise ValueError(
            f"Date '{date_str}' must be in YYYYMMDD format (e.g. 20260101)."
        )
    return s


def validate_arrange(arrange: str) -> str:
    """Validate sort-order code."""
    code = arrange.strip().upper()
    if code not in VALID_ARRANGE_CODES:
        raise ValueError(
            f"Invalid arrange '{arrange}'. "
            f"Must be one of: {', '.join(sorted(VALID_ARRANGE_CODES))}"
        )
    return code
