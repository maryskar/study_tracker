import unittest
from unittest.mock import patch
from program_files.api_client import WorldTimeAPI
from datetime import datetime

class TestWorldTimeAPI(unittest.TestCase):
    @patch("program_files.api_client.requests.get")
    def test_get_formatted_time_success(self, mock_get):
        payload = {"datetime": "2025-04-30T09:30:00+03:00"}
        mock_get.return_value.json.return_value = payload
        result = WorldTimeAPI.get_formatted_time()
        # Должен содержать дату и время
        self.assertIn("2025-04-30", result)
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    @patch("program_files.api_client.requests.get", side_effect=Exception("nope"))
    def test_get_formatted_time_fallback(self, _):
        result = WorldTimeAPI.get_formatted_time()
        # Снова должен вернуть строку времени
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
