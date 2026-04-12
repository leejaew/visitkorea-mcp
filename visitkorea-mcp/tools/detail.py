"""
Detail tool handlers — common info, intro info, type-specific detail, and images.

Schema definitions live in schemas/detail_schema.py.
"""
from __future__ import annotations

from typing import Optional

from schemas.detail_schema import TOOLS
from utils.api_client import call_api

__all__ = ["TOOLS", "handle"]


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
