from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from calculator.views import RecordViews
from calculator.models import Record, Operation


class RecordEntryPointTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_plural_endpoint_get(self):
        request = self.factory.get('/fake-url')
        request.user = self.user

        response = RecordViews.plural_endpoint(request)
        self.assertEqual(response.status_code, 200)

    def test_plural_endpoint_post(self):
        request = self.factory.post(
            '/fake-url',
            {'data': 'value'},
            content_type='application/json'
        )
        request.user = self.user

        response = RecordViews.plural_endpoint(request)
        self.assertEqual(response.status_code, 400)

    def test_plural_endpoint_invalid_method(self):
        # Test invalid method, e.g., PUT
        request = self.factory.put('/fake-url', {})
        request.user = self.user

        response = RecordViews.plural_endpoint(request)
        self.assertEqual(response.status_code, 405)

    def test_singular_endpoint_delete(self):
        operation = Operation.objects.create(type='Addition', cost=100)
        record = Record.objects.create(
            operation=operation,
            user=self.user,
            amount=100,
            user_balance=2000,
            operation_response=10
        )

        request = self.factory.delete('/fake-url')
        request.user = self.user

        response = RecordViews.singular_endpoint(request, record_id=record.id)
        self.assertEqual(response.status_code, 200)

    def test_singular_endpoint_invalid_method(self):
        # Test invalid method, e.g., GET
        request = self.factory.get('/fake-url')
        request.user = self.user

        # Call the method
        response = RecordViews.singular_endpoint(request, record_id=1)

        # Check that the response is a 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
