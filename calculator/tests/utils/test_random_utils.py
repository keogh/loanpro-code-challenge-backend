from django.test import TestCase
from unittest.mock import patch
from calculator.utils import get_random_string


class TestUtils(TestCase):
    @patch('requests.post')
    def test_get_random_string_success(self, mock_post):
        # Mock the API response to be successful
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "random": {
                    "data": ["abc123"]
                }
            }
        }

        result = get_random_string(6, "abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(result, "abc123")

    @patch('requests.post')
    def test_get_random_string_api_failure(self, mock_post):
        # Mock an API failure response
        mock_response = mock_post.return_value
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}

        result = get_random_string(6, "abcdefghijklmnopqrstuvwxyz")
        self.assertIsNone(result)

    @patch('requests.post')
    def test_get_random_string_bad_response(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"some": "wrongdata"}

        result = get_random_string(6, "abcdefghijklmnopqrstuvwxyz")
        self.assertIsNone(result)
