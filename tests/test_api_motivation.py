import unittest
from unittest.mock import patch
from program_files.api_client import MotivationAPI

class TestMotivationAPI(unittest.TestCase):
    @patch("api_client.requests.get")
    def test_get_quote_success(self, mock_get):
        mock_resp = mock_get.return_value
        mock_resp.json.return_value = {"content": "Вперёд!"}
        self.assertEqual(MotivationAPI.get_quote(), "Вперёд!")
