from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from calculator.models import Record, Operation, UserProfile
from calculator.views import RecordViews
import json


class RecordCreateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='user', password='pass')
        self.operation, _ = Operation.objects.get_or_create(type='addition')

    def test_create_success(self):
        request = self.factory.post('/fake-url', json.dumps({
            'operation_id': self.operation.id,
            'operator1': 10,
            'operator2': 5
        }), content_type='application/json')
        request.user = self.user

        response = RecordViews.create(request)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['user_balance'], 2500 - self.operation.cost)  # 2500 - 10 (operation cost)

    def test_create_missing_fields(self):
        # Missing operation_id
        request = self.factory.post('/fake-url', json.dumps({
            'operator1': 10,
            'operator2': 5
        }), content_type='application/json')
        request.user = self.user

        response = RecordViews.create(request)
        self.assertEqual(response.status_code, 400)

    def test_create_insufficient_balance(self):
        self.user.userprofile.balance = 1  # Not enough for the operation cost of 10
        request = self.factory.post('/fake-url', json.dumps({
            'operation_id': self.operation.id,
            'operator1': 10,
            'operator2': 5
        }), content_type='application/json')
        request.user = self.user

        response = RecordViews.create(request)
        self.assertEqual(response.status_code, 403)

    def test_create_invalid_json(self):
        request = self.factory.post('/fake-url', '{"bad json": "true"', content_type='application/json')
        request.user = self.user

        response = RecordViews.create(request)
        self.assertEqual(response.status_code, 400)

    def test_create_operation_not_found(self):
        # Providing an invalid operation ID
        request = self.factory.post('/fake-url', json.dumps({
            'operation_id': 9999,  # Non-existent ID
            'operator1': 10,
            'operator2': 5
        }), content_type='application/json')
        request.user = self.user

        response = RecordViews.create(request)
        self.assertEqual(response.status_code, 404)
