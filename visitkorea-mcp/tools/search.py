"""
Search tool handlers — area-based, location-based, and keyword search.

Schema definitions live in schemas/search_schema.py.
"""
from __future__ import annotations

from typing import Optional

from schemas.search_schema import TOOLS
from utils.api_client import call_api
from utils.validation import validate_gps, validate_radius

__all__ = ["TOOLS", "handle"]


async def handle(name: str, args: dict) -> Optional[dict]:
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

    if name == "search_tourism_by_location":
        map_x, map_y = validate_gps(args["mapX"], args["mapY"])
        radius = validate_radius(args["radius"])
        return await call_api("locationBasedList2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "mapX": map_x,
            "mapY": map_y,
            "radius": radius,
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    if name == "search_tourism_by_keyword":
        return await call_api("searchKeyword2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "keyword": args.get("keyword"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    return None
