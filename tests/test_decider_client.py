
import unittest
from unittest.mock import Mock, patch

import requests

from decider_client import DeciderClient


class TestDeciderClient(unittest.TestCase):
    @patch("decider_client.requests.post")
    def test_valid_response_returns_score(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "answers": {
                "contains_secret": {
                    "noul": 0.15
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = DeciderClient()
        result = client.evaluate_noul("Safe sample text")

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["noul_score"], 0.15)

    @patch("decider_client.requests.post")
    def test_server_error_fails_closed(self, mock_post):
        mock_post.side_effect = requests.Timeout()

        client = DeciderClient()
        result = client.evaluate_noul("Safe sample text")

        self.assertEqual(result["status"], "ERROR")
        self.assertIsNone(result["noul_score"])

    @patch("decider_client.requests.post")
    def test_malformed_response_fails_closed(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "format"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = DeciderClient()
        result = client.evaluate_noul("Safe sample text")

        self.assertEqual(result["status"], "ERROR")
        self.assertIsNone(result["noul_score"])


if __name__ == "__main__":
    unittest.main()
