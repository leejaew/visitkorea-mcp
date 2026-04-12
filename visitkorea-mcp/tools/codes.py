"""
Reference code lookup tool handlers — all responses cached for 1 hour.

Schema definitions live in schemas/codes_schema.py.
"""
from __future__ import annotations

from typing import Optional

from schemas.codes_schema import TOOLS
from utils.api_client import call_api

__all__ = ["TOOLS", "handle"]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "get_legal_district_codes":
        return await call_api("ldongCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongListYn": args.get("lDongListYn", "N"),
        })

    if name == "get_classification_codes":
        return await call_api("lclsSystmCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
            "lclsSystmListYn": args.get("lclsSystmListYn", "N"),
        })

    if name == "get_area_codes":
        return await call_api("areaCode2", {
            "numOfRows": args.get("numOfRows", 50),
            "pageNo": args.get("pageNo", 1),
            "areaCode": args.get("areaCode"),
        })

    if name == "get_category_codes":
        return await call_api("categoryCode2", {
            "numOfRows": args.get("numOfRows", 100),
            "pageNo": args.get("pageNo", 1),
            "cat1": args.get("cat1"),
            "cat2": args.get("cat2"),
            "contentTypeId": args.get("contentTypeId"),
        })

    return None
