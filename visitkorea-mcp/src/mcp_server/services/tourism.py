"""Ordinary-Python tourism workflows used by MCP tool handlers."""
from __future__ import annotations

from typing import Any

from ..clients import KTOClient
from .validation import validate_date, validate_gps, validate_radius


class TourismService:
    def __init__(self, client: KTOClient) -> None:
        self.client = client

    async def search(self, name: str, args: dict[str, Any]) -> dict | None:
        if name == "search_tourism_by_area":
            return await self.client.call("areaBasedList2", {
                "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
                "arrange": args.get("arrange"), "contentTypeId": args.get("contentTypeId"),
                "lDongRegnCd": args.get("lDongRegnCd"), "lDongSignguCd": args.get("lDongSignguCd"),
                "lclsSystm1": args.get("lclsSystm1"), "lclsSystm2": args.get("lclsSystm2"),
                "lclsSystm3": args.get("lclsSystm3"), "modifiedtime": args.get("modifiedtime"),
                "areaCode": args.get("areaCode"), "sigunguCode": args.get("sigunguCode"),
                "cat1": args.get("cat1"), "cat2": args.get("cat2"), "cat3": args.get("cat3"),
            })
        if name == "search_tourism_by_location":
            map_x, map_y = validate_gps(args["mapX"], args["mapY"])
            return await self.client.call("locationBasedList2", {
                "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
                "arrange": args.get("arrange"), "contentTypeId": args.get("contentTypeId"),
                "mapX": map_x, "mapY": map_y, "radius": validate_radius(args["radius"]),
                "lDongRegnCd": args.get("lDongRegnCd"), "lDongSignguCd": args.get("lDongSignguCd"),
                "lclsSystm1": args.get("lclsSystm1"), "lclsSystm2": args.get("lclsSystm2"),
                "lclsSystm3": args.get("lclsSystm3"),
            })
        if name == "search_tourism_by_keyword":
            return await self.client.call("searchKeyword2", {
                "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
                "arrange": args.get("arrange"), "contentTypeId": args.get("contentTypeId"),
                "keyword": args.get("keyword"), "lDongRegnCd": args.get("lDongRegnCd"),
                "lDongSignguCd": args.get("lDongSignguCd"), "lclsSystm1": args.get("lclsSystm1"),
                "lclsSystm2": args.get("lclsSystm2"), "lclsSystm3": args.get("lclsSystm3"),
            })
        return None

    async def events(self, args: dict[str, Any]) -> dict:
        end = args.get("eventEndDate")
        return await self.client.call("searchFestival2", {
            "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"),
            "eventStartDate": validate_date(args["eventStartDate"]),
            "eventEndDate": validate_date(end) if end else None,
            "modifiedtime": args.get("modifiedtime"), "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"), "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"), "lclsSystm3": args.get("lclsSystm3"),
        })

    async def accommodations(self, args: dict[str, Any]) -> dict:
        return await self.client.call("searchStay2", {
            "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
            "arrange": args.get("arrange"), "modifiedtime": args.get("modifiedtime"),
            "lDongRegnCd": args.get("lDongRegnCd"), "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"), "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    async def detail(self, name: str, args: dict[str, Any]) -> dict | None:
        empty_hint = (
            "No data was returned for this content ID. The item may not exist, may have been "
            "removed from the KTO dataset, or the content ID may have been derived from a "
            "different API service. Obtain content IDs from an active search tool call in the same session."
        )
        if name == "get_tourism_common_info":
            params = {"contentId": args["contentId"]}
            for field in ("defaultYN", "firstImageYN", "areacodeYN", "catcodeYN",
                          "addrinfoYN", "mapinfoYN", "overviewYN"):
                params[field] = args.get(field, "Y")
            if args.get("contentTypeId"):
                params["contentTypeId"] = args["contentTypeId"]
            result = await self.client.call("detailCommon2", params)
        elif name in ("get_tourism_intro_info", "get_tourism_detail_info"):
            endpoint = "detailIntro2" if name.endswith("intro_info") else "detailInfo2"
            result = await self.client.call(endpoint, {
                "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
                "contentId": args["contentId"], "contentTypeId": args["contentTypeId"],
            })
        elif name == "get_tourism_images":
            result = await self.client.call("detailImage2", {
                "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
                "contentId": args["contentId"], "imageYN": args.get("imageYN", "Y"),
            })
            if result.get("success") and result.get("totalCount", 0) == 0:
                result["hint"] = "No images were found for this content ID. Not all KTO listings have associated images."
            return result
        else:
            return None
        if result.get("success") and result.get("totalCount", 0) == 0:
            result["hint"] = empty_hint
        return result

    async def sync(self, args: dict[str, Any]) -> dict:
        return await self.client.call("areaBasedSyncList2", {
            "numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1),
            "modifiedtime": args.get("modifiedtime"), "showflag": args.get("showflag"),
            "arrange": args.get("arrange"), "contentTypeId": args.get("contentTypeId"),
            "oldContentid": args.get("oldContentid"), "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"), "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"), "lclsSystm3": args.get("lclsSystm3"),
        })

    async def codes(self, name: str, args: dict[str, Any]) -> dict | None:
        endpoints = {
            "get_legal_district_codes": ("ldongCode2", {"numOfRows": args.get("numOfRows", 100),
                "pageNo": args.get("pageNo", 1), "lDongRegnCd": args.get("lDongRegnCd"),
                "lDongListYn": args.get("lDongListYn", "N")}),
            "get_classification_codes": ("lclsSystmCode2", {"numOfRows": args.get("numOfRows", 100),
                "pageNo": args.get("pageNo", 1), "lclsSystm1": args.get("lclsSystm1"),
                "lclsSystm2": args.get("lclsSystm2"), "lclsSystm3": args.get("lclsSystm3"),
                "lclsSystmListYn": args.get("lclsSystmListYn", "N")}),
            "get_area_codes": ("areaCode2", {"numOfRows": args.get("numOfRows", 50),
                "pageNo": args.get("pageNo", 1), "areaCode": args.get("areaCode")}),
            "get_category_codes": ("categoryCode2", {"numOfRows": args.get("numOfRows", 100),
                "pageNo": args.get("pageNo", 1), "cat1": args.get("cat1"),
                "cat2": args.get("cat2"), "contentTypeId": args.get("contentTypeId")}),
        }
        selected = endpoints.get(name)
        return await self.client.call(*selected) if selected else None