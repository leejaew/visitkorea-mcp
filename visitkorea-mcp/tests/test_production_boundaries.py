import os
import unittest
from unittest.mock import AsyncMock

import httpx

from config import AppConfig
from tools import _ALL_MODULES
from utils import cache
from utils.api_client import KTOClient
from utils.validation import validate_date


def config(key="secret%2Fvalue"):
    return AppConfig(api_key=key.replace("%2F", "/"))


class ConfigurationTests(unittest.TestCase):
    def test_env_is_required_and_decoded_without_leaking(self):
        old = os.environ.get("VISITKOREA_API_KEY")
        try:
            os.environ["VISITKOREA_API_KEY"] = "top%2Fsecret"
            loaded = AppConfig.from_env()
            self.assertEqual(loaded.api_key, "top/secret")
            self.assertNotIn("top/secret", repr(loaded))  # dataclass repr must not expose credentials
        finally:
            if old is None:
                os.environ.pop("VISITKOREA_API_KEY", None)
            else:
                os.environ["VISITKOREA_API_KEY"] = old

    def test_missing_key_fails(self):
        old = os.environ.pop("VISITKOREA_API_KEY", None)
        try:
            with self.assertRaises(ValueError):
                AppConfig.from_env()
        finally:
            if old is not None:
                os.environ["VISITKOREA_API_KEY"] = old


class ValidationTests(unittest.TestCase):
    def test_calendar_date(self):
        self.assertEqual(validate_date("20240229"), "20240229")
        with self.assertRaises(ValueError):
            validate_date("20230229")
        with self.assertRaises(ValueError):
            validate_date("20241301")


class EnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.client = KTOClient(config("private-key"))

    def envelope(self, code="00", item=None, total=1, msg="ok"):
        return {"response": {"header": {"resultCode": code, "resultMsg": msg},
                "body": {"numOfRows": 1, "pageNo": 1, "totalCount": total,
                         "items": {"item": item if item is not None else {"id": 1}}}}}

    def test_list_single_and_empty(self):
        self.assertEqual(self.client.parse_envelope(self.envelope(item=[{"id": 1}]))["items"], [{"id": 1}])
        self.assertEqual(self.client.parse_envelope(self.envelope(item={"id": 1}))["items"], [{"id": 1}])
        empty = self.client.parse_envelope(self.envelope("03", total=0))
        self.assertEqual(empty["items"], [])
        self.assertEqual(empty["totalCount"], 0)

    def test_errors_and_redaction_are_safe(self):
        with self.assertRaises(PermissionError):
            self.client.parse_envelope(self.envelope("30", msg="private-key"))
        with self.assertRaises(RuntimeError) as caught:
            self.client.parse_envelope({"response": {"header": {"resultCode": "00"}, "body": []}})
        self.assertEqual(str(caught.exception), "Korea Tourism API returned a malformed response.")
        self.assertNotIn("private-key", str(caught.exception))


class ClientRequestTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        cache._store.clear()

    def response(self, **kwargs):
        return httpx.Response(request=httpx.Request("GET", "http://x"), **kwargs)

    async def test_timeout_non_json_and_retry(self):
        fake = AsyncMock()
        fake.get.side_effect = httpx.TimeoutException("details")
        client = KTOClient(config(), fake)
        result = await client.call("endpoint")
        self.assertFalse(result["success"])
        self.assertNotIn("details", result["error"])

        bad = self.response(status_code=200, content=b"not json")
        fake.get.side_effect = [bad]
        with self.assertRaisesRegex(RuntimeError, "invalid response"):
            await client.call("bad-json", {"x": 1})

        good = self.response(status_code=200, json={"response": {"header": {"resultCode": "00", "resultMsg": "ok"},
            "body": {"totalCount": 1, "items": {"item": {"x": 1}}}}})
        fake.reset_mock()
        fake.get.side_effect = [httpx.RequestError("temporary", request=httpx.Request("GET", "http://x")), good]
        result = await client.call("retry")
        self.assertEqual(result["items"], [{"x": 1}])
        self.assertEqual(fake.get.call_count, 2)

    async def test_only_nonempty_results_are_cached(self):
        fake = AsyncMock()
        empty = self.response(status_code=200, json={"response": {"header": {"resultCode": "00", "resultMsg": "ok"},
            "body": {"totalCount": 0, "items": {}}}})
        nonempty = self.response(status_code=200, json={"response": {"header": {"resultCode": "00", "resultMsg": "ok"},
            "body": {"totalCount": 1, "items": {"item": {"x": 1}}}}})
        fake.get.side_effect = [empty, empty, nonempty, nonempty]
        client = KTOClient(config(), fake)
        await client.call("empty")
        await client.call("empty")
        self.assertEqual(fake.get.call_count, 2)
        await client.call("full")
        await client.call("full")
        self.assertEqual(fake.get.call_count, 3)


class PublicContractTests(unittest.TestCase):
    def test_exact_ordered_tools(self):
        expected = [
            "search_tourism_by_area", "search_tourism_by_location", "search_tourism_by_keyword",
            "search_festivals_and_events", "search_accommodations", "get_tourism_common_info",
            "get_tourism_intro_info", "get_tourism_detail_info", "get_tourism_images",
            "get_sync_list", "get_legal_district_codes", "get_classification_codes",
            "get_area_codes", "get_category_codes",
        ]
        actual = [tool.name for module in _ALL_MODULES for tool in module.TOOLS]
        self.assertEqual(actual, expected)