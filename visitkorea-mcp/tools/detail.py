"""
Detail tool handlers — common info, intro info, type-specific detail, and images.

Schema definitions live in schemas/detail_schema.py.
"""
from __future__ import annotations

from typing import Optional

from schemas.detail_schema import TOOLS
from utils.api_client import call_api

__all__ = ["TOOLS", "handle"]

_EMPTY_HINT = (
    "No data was returned for this content ID. "
    "The item may not exist, may have been removed from the KTO dataset, "
    "or the content ID may have been derived from a different API service. "
    "Obtain content IDs from an active search tool call in the same session."
)


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "get_tourism_common_info":
        # detailCommon2 is a single-item by-ID lookup — numOfRows / pageNo are
        # not meaningful here and would fragment the cache unnecessarily.
        params: dict = {"contentId": args["contentId"]}
        for yn_field in (
            "defaultYN", "firstImageYN", "areacodeYN",
            "catcodeYN", "addrinfoYN", "mapinfoYN", "overviewYN",
        ):
            val = args.get(yn_field)
            if val is not None:
                params[yn_field] = val
            else:
                params[yn_field] = "Y"   # sensible default — return all fields
        # contentTypeId is optional; include only when explicitly supplied
        if args.get("contentTypeId"):
            params["contentTypeId"] = args["contentTypeId"]

        result = await call_api("detailCommon2", params)
        if result.get("success") and result.get("totalCount", 0) == 0:
            result["hint"] = _EMPTY_HINT
        return result

    if name == "get_tourism_intro_info":
        result = await call_api("detailIntro2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "contentTypeId": args["contentTypeId"],
        })
        if result.get("success") and result.get("totalCount", 0) == 0:
            result["hint"] = _EMPTY_HINT
        return result

    if name == "get_tourism_detail_info":
        result = await call_api("detailInfo2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "contentTypeId": args["contentTypeId"],
        })
        if result.get("success") and result.get("totalCount", 0) == 0:
            result["hint"] = _EMPTY_HINT
        return result

    if name == "get_tourism_images":
        result = await call_api("detailImage2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "contentId": args["contentId"],
            "imageYN": args.get("imageYN", "Y"),
        })
        if result.get("success") and result.get("totalCount", 0) == 0:
            result["hint"] = (
                "No images were found for this content ID. "
                "Not all KTO listings have associated images."
            )
        return result

    return None
