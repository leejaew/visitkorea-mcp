import os
import unittest

from mcp_server.config import AppConfig
from mcp_server.observability.logging import configure_logging
from mcp_server.services.validation import validate_date


class SecurityBoundaryTests(unittest.TestCase):
    def test_configuration_requires_key_and_redacts_repr(self):
        old = os.environ.pop("VISITKOREA_API_KEY", None)
        try:
            with self.assertRaises(ValueError):
                AppConfig.from_env()
            os.environ["VISITKOREA_API_KEY"] = "top%2Fsecret"
            loaded = AppConfig.from_env()
            self.assertEqual(loaded.api_key, "top/secret")
            self.assertNotIn("top/secret", repr(loaded))
        finally:
            if old is None:
                os.environ.pop("VISITKOREA_API_KEY", None)
            else:
                os.environ["VISITKOREA_API_KEY"] = old

    def test_validation_and_logging(self):
        self.assertEqual(validate_date("20240229"), "20240229")
        with self.assertRaises(ValueError):
            validate_date("20230229")
        configure_logging()
