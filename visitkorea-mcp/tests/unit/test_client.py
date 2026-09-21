import unittest
from unittest.mock import AsyncMock

import httpx

from mcp_server.clients import KTOClient
from mcp_server.clients.cache import make_key
from mcp_server.config import AppConfig
from mcp_server.services.validation import (
    validate_arrange,
    validate_date,
    validate_gps,
    validate_pagination,
    validate_radius,
)


def config(key="secret%2Fvalue"):
    return AppConfig(api_key=key.replace("%2F", "/"))


class ClientTests(unittest.IsolatedAsyncioTestCase):
    def envelope(self, code="00", item=None, total=1, msg="ok"):
        return {"response": {"header": {"resultCode": code, "resultMsg": msg},
                "body": {"numOfRows": 1, "pageNo": 1, "totalCount": total,
                         "items": {"item": item if item is not None else {"id": 1}}}}}

    def test_envelope_normalization_and_safe_errors(self):
        client = KTOClient(config("private-key"))
        self.assertEqual(client.parse_envelope(self.envelope(item={"id": 1}))["items"], [{"id": 1}])
        self.assertEqual(client.parse_envelope(self.envelope("03", total=0))["items"], [])
        with self.assertRaises(PermissionError):
            client.parse_envelope(self.envelope("30", msg="private-key"))
        self.assertNotIn("private-key", str(client.parse_envelope(self.envelope("00"))))

    async def test_timeout_and_retry(self):
        fake = AsyncMock()
        fake.get.side_effect = httpx.TimeoutException("details")
        client = KTOClient(config(), fake)
        result = await client.call("endpoint")
        self.assertFalse(result["success"])
        good = httpx.Response(
            status_code=200,
            request=httpx.Request("GET", "http://x"),
            json={"response": {"header": {"resultCode": "00", "resultMsg": "ok"},
                "body": {"totalCount": 1, "items": {"item": {"x": 1}}}}},
        )
        fake.get.side_effect = [
            httpx.RequestError("temporary", request=httpx.Request("GET", "http://x")),
            good,
        ]
        result = await client.call("retry")
        self.assertEqual(result["items"], [{"x": 1}])

    async def test_non_json_malformed_and_nonempty_cache_behavior(self):
        fake = AsyncMock()
        bad = httpx.Response(
            status_code=200,
            request=httpx.Request("GET", "http://x"),
            content=b"not json",
        )
        fake.get.side_effect = [bad]
        with self.assertRaisesRegex(RuntimeError, "invalid response"):
            await KTOClient(config(), fake).call("bad-json")

        malformed = httpx.Response(
            status_code=200,
            request=httpx.Request("GET", "http://x"),
            json={"response": {"header": {"resultCode": "00"}, "body": []}},
        )
        fake.get.side_effect = [malformed]
        with self.assertRaisesRegex(RuntimeError, "malformed response"):
            await KTOClient(config(), fake).call("malformed")

        empty = httpx.Response(
            status_code=200,
            request=httpx.Request("GET", "http://x"),
            json={"response": {"header": {"resultCode": "00", "resultMsg": "ok"},
                "body": {"totalCount": 0, "items": {}}},
            },
        )
        full = httpx.Response(
            status_code=200,
            request=httpx.Request("GET", "http://x"),
            json={"response": {"header": {"resultCode": "00", "resultMsg": "ok"},
                "body": {"totalCount": 1, "items": {"item": {"x": 1}}}}},
        )
        fake.get.side_effect = [empty, empty, full, full]
        client = KTOClient(config(), fake)
        fake.reset_mock()
        await client.call("empty")
        await client.call("empty")
        self.assertEqual(fake.get.call_count, 2)
        await client.call("full")
        await client.call("full")
        self.assertEqual(fake.get.call_count, 3)

    def test_cache_key_is_secret_free_and_canonical(self):
        encoded = "raw%2Fkey"
        plain = "raw/key"
        first = make_key("search", {
            "serviceKey": plain, "VISITKOREA_API_KEY": encoded,
            "pageNo": 1, "keyword": "Seoul",
        })
        second = make_key("search", {
            "keyword": "Seoul", "pageNo": 1,
            "serviceKey": plain, "VISITKOREA_API_KEY": encoded,
        })
        self.assertEqual(first, second)
        self.assertNotIn(plain, first)
        self.assertNotIn(encoded, first)
        self.assertEqual(len(first.rsplit(":", 1)[1]), 16)

    def test_validation_matches_public_contract(self):
        self.assertEqual(validate_date("20240229"), "20240229")
        with self.assertRaisesRegex(ValueError, "not a valid calendar date"):
            validate_date("20230229")
        with self.assertRaisesRegex(ValueError, "YYYYMMDD"):
            validate_date("2024-02-29")
        self.assertEqual(validate_gps(126.9784, 37.5665), (126.9784, 37.5665))
        with self.assertRaisesRegex(ValueError, "South Korea bounds"):
            validate_gps(10, 37.5)
        with self.assertRaisesRegex(ValueError, "South Korea bounds"):
            validate_gps(126.9, 50)
        self.assertEqual(validate_radius(20_000), 20_000)
        with self.assertRaisesRegex(ValueError, "1 and 20,000"):
            validate_radius(20_001)
        self.assertEqual(validate_pagination(0, 0), (1, 1))
        self.assertEqual(validate_pagination(500, -2), (100, 1))
        self.assertEqual(validate_arrange(" c "), "C")
