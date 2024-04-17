import json
from django.test import TestCase, RequestFactory
from codechallenge.views import OperationViews
from calculator.models import Operation


class OperationViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        Operation.objects.all().delete()
        for i in range(20):
            Operation.objects.create(
                type=f'Operation_{i}',
                cost=i * 10,
                name=f'Operation Name {i}'
            )

    def test_list_operations(self):
        request = self.factory.get('/operations', {'page': '2', 'per_page': '5', 'sort_by': 'cost', 'direction': 'asc'})
        response = OperationViews.list(request)
        data = json.loads(response.content.decode('utf-8'))  # Correctly parsing the JSON response

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['operations']), 5)
        self.assertEqual(data['pagination']['page'], 2)
        self.assertEqual(data['pagination']['total_pages'], 4)
        self.assertEqual(data['operations'][0]['cost'], 50)

    def test_operation_filtering(self):
        request = self.factory.get('/operations', {'search': 'Name 1'})
        response = OperationViews.list(request)
        data = json.loads(response.content.decode('utf-8'))

        self.assertTrue(all('Name 1' in operation['name'] for operation in data['operations']))
