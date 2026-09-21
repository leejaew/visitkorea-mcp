"""Pure validation helpers for MCP inputs."""
from __future__ import annotations

import re
from datetime import datetime

VALID_ARRANGE_CODES = frozenset({"A", "C", "D", "O", "Q", "R"})
_LON_MIN, _LON_MAX = 124.0, 132.0
_LAT_MIN, _LAT_MAX = 33.0, 39.0


def validate_pagination(num_of_rows: int, page_no: int) -> tuple[int, int]:
    """Clamp numOfRows to [1, 100] and pageNo to >= 1."""
    return max(1, min(int(num_of_rows), 100)), max(1, int(page_no))


def validate_date(value: str) -> str:
    original = value
    text = value.strip()
    if not re.fullmatch(r"\d{8}", text):
        raise ValueError(
            f"Date '{original}' must be in YYYYMMDD format (e.g. 20260101)."
        )
    try:
        datetime.strptime(text, "%Y%m%d")
    except ValueError:
        raise ValueError(f"Date '{original}' is not a valid calendar date.") from None
    return text


def validate_gps(map_x: float, map_y: float) -> tuple[float, float]:
    x, y = float(map_x), float(map_y)
    if not _LON_MIN <= x <= _LON_MAX:
        raise ValueError(
            f"mapX (longitude) {x} is outside South Korea bounds "
            f"({_LON_MIN}–{_LON_MAX})."
        )
    if not _LAT_MIN <= y <= _LAT_MAX:
        raise ValueError(
            f"mapY (latitude) {y} is outside South Korea bounds "
            f"({_LAT_MIN}–{_LAT_MAX})."
        )
    return x, y


def validate_arrange(arrange: str) -> str:
    """Validate sort-order code."""
    code = arrange.strip().upper()
    if code not in VALID_ARRANGE_CODES:
        raise ValueError(
            f"Invalid arrange '{arrange}'. "
            f"Must be one of: {', '.join(sorted(VALID_ARRANGE_CODES))}"
        )
    return code


def validate_radius(value: int) -> int:
    radius = int(value)
    if not 1 <= radius <= 20_000:
        raise ValueError(
            f"radius must be between 1 and 20,000 metres, got {value}."
        )
    return radius
