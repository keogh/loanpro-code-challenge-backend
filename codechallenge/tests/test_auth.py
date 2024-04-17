from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from codechallenge.views import AuthViews
import json
from django.conf import settings
import jwt


class AuthViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='correctpassword')

    @patch('django.contrib.auth.authenticate')
    @patch('jwt.encode')
    def test_sign_in_success(self, mock_jwt_encode, mock_authenticate):
        # Setup mocks
        mock_authenticate.return_value = self.user
        mock_jwt_encode.return_value = 'fakejwttoken'

        # Create a POST request with correct credentials
        request = self.factory.post('/sign-in', json.dumps({
            'username': 'testuser',
            'password': 'correctpassword'
        }), content_type='application/json')

        response = AuthViews.sign_in(request)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['token'], 'fakejwttoken')

    @patch('django.contrib.auth.authenticate')
    def test_sign_in_invalid_credentials(self, mock_authenticate):
        # Setup mock
        mock_authenticate.return_value = None

        # Create a POST request with incorrect credentials
        request = self.factory.post('/sign-in', json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }), content_type='application/json')

        response = AuthViews.sign_in(request)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'Invalid Credentials')

    def test_sign_in_requires_post(self):
        # Create a GET request
        request = self.factory.get('/sign-in')

        response = AuthViews.sign_in(request)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'POST request required.')
