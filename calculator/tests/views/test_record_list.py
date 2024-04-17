from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from calculator.models import Record, Operation
from calculator.views import RecordViews
import json
import random


class RecordListTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='user', password='pass')
        self.operation = Operation.objects.create(type='Addition', cost=10)
        for i in range(15):
            Record.objects.create(
                user=self.user,
                operation=self.operation,
                amount=100 + i,
                user_balance=1000 - i,
                operation_response=random.randint(1, 100),
                created_at='2024-04-01 00:00:00'
            )

    def test_list_no_params(self):
        request = self.factory.get('/fake-url')
        request.user = self.user
        response = RecordViews.list(request)
        data = json.loads(response.content)

        self.assertEqual(len(data['records']), 10)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['total_pages'], 2)

    def test_list_sorting_and_direction(self):
        request = self.factory.get('/fake-url?sort_by=amount&direction=asc')
        request.user = self.user
        response = RecordViews.list(request)
        data = json.loads(response.content)

        # Check if sorting by amount ascending works
        self.assertTrue(
            all(
                data['records'][i]['amount'] <= data['records'][i + 1]['amount'] for i in range(len(data['records']) - 1)
            )
        )

    def test_list_pagination(self):
        request = self.factory.get('/fake-url?page=2&per_page=5')
        request.user = self.user
        response = RecordViews.list(request)
        data = json.loads(response.content)

        self.assertEqual(data['pagination']['page'], '2')
        self.assertEqual(len(data['records']), 5)

    def test_list_search_filter(self):
        # Adding a specific record to test search
        operation2 = Operation.objects.create(type='specific', cost=10)
        Record.objects.create(
            user=self.user,
            operation=operation2,
            amount=777,
            user_balance=777,
            operation_response=23,
            created_at='2024-04-01 00:00:00'
        )
        request = self.factory.get('/fake-url?search=specific')
        request.user = self.user
        response = RecordViews.list(request)
        data = json.loads(response.content)

        # Expect to find only the specific searched record
        self.assertEqual(len(data['records']), 1)
        self.assertEqual(data['records'][0]['operation_type'], 'specific')
