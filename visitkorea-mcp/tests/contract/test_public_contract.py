import asyncio
import hashlib
import json
import unittest
from mcp_server.clients import KTOClient
from mcp_server.config import AppConfig
from mcp_server.server import create_server
from mcp_server.services import TourismService
from mcp_server.tools.registry import ToolRegistry
from mcp_server.tools.registry import _ALL_MODULES


EXPECTED_TOOLS = [
    "search_tourism_by_area", "search_tourism_by_location", "search_tourism_by_keyword",
    "search_festivals_and_events", "search_accommodations", "get_tourism_common_info",
    "get_tourism_intro_info", "get_tourism_detail_info", "get_tourism_images",
    "get_sync_list", "get_legal_district_codes", "get_classification_codes",
    "get_area_codes", "get_category_codes",
]

SCHEMA_DIGESTS = {
    "search_tourism_by_area": "79b3a590601f4b542354cc9bebb724186578b732856d06bba1bde07c23333c61",
    "search_tourism_by_location": "0c548bd7c09ab0b7d203b5529b6fa51b3a21d1ded1d0cf3fb4a69af27e72dfc5",
    "search_tourism_by_keyword": "3568b3ffecdc8942d48cfd99545309498a7c58c853a447676142b7e35854be08",
    "search_festivals_and_events": "5bbf7ae44782c21929033fd016d221d14fd47b16a9820f4ddfee439baeb566d9",
    "search_accommodations": "febda94bb7f20a67fff08b55abb53efdabd3d2de16852ed6d6deda5a1ecbffcf",
    "get_tourism_common_info": "4c42802af0529cf6cfc77141c89ea6fac4bee58a04f29b0d93bfbbb655ac0fb4",
    "get_tourism_intro_info": "7cd137637d26cea781b665d3ae771b1738ad92f9239a8fd908023633469f2fdd",
    "get_tourism_detail_info": "b577a56321aa0af6f18be0a080f0b382465009b781d07fae32632b82ae3cd4cb",
    "get_tourism_images": "7962080ffcf644f828f0a7023eda1973c523ce96b96d43b864e32ad66998e91d",
    "get_sync_list": "fb2e54064ac209bc5e9e3b55441bd43b2ac142d513919088aab9e614ce7a84a6",
    "get_legal_district_codes": "ecb7235adb6534716d043b7d10f951cc0dac3473b70ebabba703880a9f1758f2",
    "get_classification_codes": "bcd15f1f19bcf811157c2f1e9cf444618be54c083319503d76612435970d0030",
    "get_area_codes": "98fc98820471a40e753761ce9067115cf8e672c19ffde3af585daba394b7a650",
    "get_category_codes": "a6099d8332b84ba9542cae1fae5ff6d3860413f45024f499167d34b07383bb0c",
}


def expected_params(name, args):
    common = {"numOfRows": args.get("numOfRows", 10), "pageNo": args.get("pageNo", 1)}
    if name == "search_tourism_by_area":
        return {**common, **{key: args[key] for key in (
            "arrange", "contentTypeId", "lDongRegnCd", "lDongSignguCd", "lclsSystm1",
            "lclsSystm2", "lclsSystm3", "modifiedtime", "areaCode", "sigunguCode",
            "cat1", "cat2", "cat3",
        )}}
    if name == "search_tourism_by_location":
        return {**common, **{key: args[key] for key in (
            "arrange", "contentTypeId", "mapX", "mapY", "radius", "lDongRegnCd",
            "lDongSignguCd", "lclsSystm1", "lclsSystm2", "lclsSystm3",
        )}}
    if name == "search_tourism_by_keyword":
        return {**common, **{key: args[key] for key in (
            "arrange", "contentTypeId", "keyword", "lDongRegnCd", "lDongSignguCd",
            "lclsSystm1", "lclsSystm2", "lclsSystm3",
        )}}
    if name == "search_festivals_and_events":
        return {**common, **{key: args[key] for key in (
            "arrange", "eventStartDate", "eventEndDate", "modifiedtime", "lDongRegnCd",
            "lDongSignguCd", "lclsSystm1", "lclsSystm2", "lclsSystm3",
        )}}
    if name == "search_accommodations":
        return {**common, **{key: args[key] for key in (
            "arrange", "modifiedtime", "lDongRegnCd", "lDongSignguCd",
            "lclsSystm1", "lclsSystm2", "lclsSystm3",
        )}}
    if name == "get_tourism_common_info":
        return {"contentId": args["contentId"], **{
            key: args[key] for key in (
                "defaultYN", "firstImageYN", "areacodeYN", "catcodeYN",
                "addrinfoYN", "mapinfoYN", "overviewYN",
            )
        }, "contentTypeId": args["contentTypeId"]}
    if name in {"get_tourism_intro_info", "get_tourism_detail_info"}:
        return {**common, "contentId": args["contentId"], "contentTypeId": args["contentTypeId"]}
    if name == "get_tourism_images":
        return {**common, "contentId": args["contentId"], "imageYN": args["imageYN"]}
    if name == "get_sync_list":
        return {**common, **{key: args[key] for key in (
            "modifiedtime", "showflag", "arrange", "contentTypeId", "oldContentid",
            "lDongRegnCd", "lDongSignguCd", "lclsSystm1", "lclsSystm2", "lclsSystm3",
        )}}
    if name == "get_legal_district_codes":
        return {"numOfRows": args["numOfRows"], "pageNo": args["pageNo"],
                "lDongRegnCd": args["lDongRegnCd"], "lDongListYn": args["lDongListYn"]}
    if name == "get_classification_codes":
        return {"numOfRows": args["numOfRows"], "pageNo": args["pageNo"],
                "lclsSystm1": args["lclsSystm1"], "lclsSystm2": args["lclsSystm2"],
                "lclsSystm3": args["lclsSystm3"], "lclsSystmListYn": args["lclsSystmListYn"]}
    if name == "get_area_codes":
        return {"numOfRows": args["numOfRows"], "pageNo": args["pageNo"], "areaCode": args["areaCode"]}
    if name == "get_category_codes":
        return {"numOfRows": args["numOfRows"], "pageNo": args["pageNo"],
                "cat1": args["cat1"], "cat2": args["cat2"], "contentTypeId": args["contentTypeId"]}
    raise AssertionError(name)


class ContractTests(unittest.TestCase):
    def test_exact_ordered_tools(self):
        tools = [tool for module in _ALL_MODULES for tool in module.TOOLS]
        self.assertEqual([tool.name for tool in tools], EXPECTED_TOOLS)
        self.assertEqual(set(SCHEMA_DIGESTS), set(EXPECTED_TOOLS))
        for tool in tools:
            encoded = json.dumps(
                tool.model_dump(), sort_keys=True, ensure_ascii=False, separators=(",", ":"),
            ).encode()
            self.assertEqual(hashlib.sha256(encoded).hexdigest(), SCHEMA_DIGESTS[tool.name])
            self.assertEqual(tool.inputSchema["type"], "object")
            self.assertIn("properties", tool.inputSchema)

    def test_registry_maps_all_tools_to_exact_endpoints(self):
        class FakeClient:
            def __init__(self):
                self.calls = []

            async def call(self, endpoint, params):
                self.calls.append((endpoint, params))
                return {"success": True, "resultCode": "00", "resultMsg": "ok",
                        "numOfRows": 1, "pageNo": 1, "totalCount": 1, "items": [{"id": "x"}]}

        fake = FakeClient()
        service = TourismService(fake)
        cases = [
            ("search_tourism_by_area", "areaBasedList2", {
                "numOfRows": 7, "pageNo": 2, "arrange": "A", "contentTypeId": "75",
                "lDongRegnCd": "11", "lDongSignguCd": "110", "lclsSystm1": "AC",
                "lclsSystm2": "AC01", "lclsSystm3": "AC0101", "modifiedtime": "20260102",
                "areaCode": "1", "sigunguCode": "1", "cat1": "A01", "cat2": "A0101",
                "cat3": "A01010100",
            }),
            ("search_tourism_by_location", "locationBasedList2", {
                "mapX": 126.9784, "mapY": 37.5665, "radius": 1234, "numOfRows": 8,
                "pageNo": 3, "arrange": "C", "contentTypeId": "76", "lDongRegnCd": "26",
                "lDongSignguCd": "260", "lclsSystm1": "TR", "lclsSystm2": "TR01",
                "lclsSystm3": "TR0101",
            }),
            ("search_tourism_by_keyword", "searchKeyword2", {
                "keyword": "Gyeongbokgung", "numOfRows": 9, "pageNo": 4, "arrange": "D",
                "contentTypeId": "78", "lDongRegnCd": "27", "lDongSignguCd": "270",
                "lclsSystm1": "VE", "lclsSystm2": "VE01", "lclsSystm3": "VE0101",
            }),
            ("search_festivals_and_events", "searchFestival2", {
                "eventStartDate": "20260101", "eventEndDate": "20260131", "numOfRows": 11,
                "pageNo": 5, "arrange": "O", "modifiedtime": "20260103", "lDongRegnCd": "28",
                "lDongSignguCd": "280", "lclsSystm1": "EV", "lclsSystm2": "EV01",
                "lclsSystm3": "EV0101",
            }),
            ("search_accommodations", "searchStay2", {
                "numOfRows": 12, "pageNo": 6, "arrange": "Q", "modifiedtime": "20260104",
                "lDongRegnCd": "29", "lDongSignguCd": "290", "lclsSystm1": "AC",
                "lclsSystm2": "AC02", "lclsSystm3": "AC0201",
            }),
            ("get_tourism_common_info", "detailCommon2", {
                "contentId": "1001", "contentTypeId": "80", "defaultYN": "N",
                "firstImageYN": "N", "areacodeYN": "N", "catcodeYN": "N",
                "addrinfoYN": "N", "mapinfoYN": "N", "overviewYN": "N",
            }),
            ("get_tourism_intro_info", "detailIntro2", {
                "contentId": "1002", "contentTypeId": "82", "numOfRows": 13, "pageNo": 7,
            }),
            ("get_tourism_detail_info", "detailInfo2", {
                "contentId": "1003", "contentTypeId": "85", "numOfRows": 14, "pageNo": 8,
            }),
            ("get_tourism_images", "detailImage2", {
                "contentId": "1004", "numOfRows": 15, "pageNo": 9, "imageYN": "N",
            }),
            ("get_sync_list", "areaBasedSyncList2", {
                "numOfRows": 16, "pageNo": 10, "modifiedtime": "20260105", "showflag": "1",
                "arrange": "R", "contentTypeId": "85", "oldContentid": "legacy-1",
                "lDongRegnCd": "30", "lDongSignguCd": "300", "lclsSystm1": "FO",
                "lclsSystm2": "FO01", "lclsSystm3": "FO0101",
            }),
            ("get_legal_district_codes", "ldongCode2", {
                "numOfRows": 17, "pageNo": 11, "lDongRegnCd": "31", "lDongListYn": "Y",
            }),
            ("get_classification_codes", "lclsSystmCode2", {
                "numOfRows": 18, "pageNo": 12, "lclsSystm1": "SH", "lclsSystm2": "SH01",
                "lclsSystm3": "SH0101", "lclsSystmListYn": "Y",
            }),
            ("get_area_codes", "areaCode2", {
                "numOfRows": 19, "pageNo": 13, "areaCode": "39",
            }),
            ("get_category_codes", "categoryCode2", {
                "numOfRows": 20, "pageNo": 14, "cat1": "A02", "cat2": "A0201",
                "contentTypeId": "76",
            }),
        ]

        async def exercise():
            for name, _endpoint, arguments in cases:
                result = await ToolRegistry(service).call_tool(name, arguments)
                self.assertEqual(json.loads(result[0].text)["success"], True)

        asyncio.run(exercise())
        self.assertEqual(
            fake.calls,
            [(endpoint, expected_params(name, arguments)) for name, endpoint, arguments in cases],
        )

    def test_server_is_constructible_and_unknown_tool_is_safe(self):
        server, client = create_server(AppConfig(api_key="secret"))
        registry = ToolRegistry(TourismService(client))
        self.assertEqual(server.name, "visitkorea-mcp")
        result = asyncio.run(registry.call_tool("unknown", {}))
        self.assertEqual(json.loads(result[0].text), {"error": "Unknown tool: unknown"})
        asyncio.run(client.close())

    def test_servers_have_isolated_clients_and_caches(self):
        first = create_server(AppConfig(api_key="one"))
        second = create_server(AppConfig(api_key="two"))
        self.assertIsNot(first[1], second[1])
        self.assertIsNot(first[1].cache, second[1].cache)
        asyncio.run(first[1].close())
        asyncio.run(second[1].close())

    def test_registry_maps_expected_safe_errors(self):
        class FailingClient:
            async def call(self, endpoint, params):
                raise PermissionError("private upstream detail")

        registry = ToolRegistry(TourismService(FailingClient()))
        result = asyncio.run(registry.call_tool("get_area_codes", {}))
        self.assertEqual(json.loads(result[0].text), {"error": "Upstream authentication failed."})
