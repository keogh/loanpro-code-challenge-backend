from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from calculator.models import Record, Operation, UserProfile
from calculator.views import RecordViews
from django.utils import timezone
import json


class RecordDeleteTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='user', password='pass')
        self.user_profile = self.user.userprofile
        self.operation = Operation.objects.create(type='Addition', cost=10)
        self.record = Record.objects.create(
            user=self.user,
            operation=self.operation,
            amount=100,
            user_balance=2400,
            operation_response=12,
            created_at=timezone.now()
        )

    def test_delete_record_success(self):
        request = self.factory.delete('/fake-url')
        request.user = self.user
        response = RecordViews.singular_endpoint(request, record_id=self.record.id)
        self.record.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(self.record.deleted_at)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('Record deleted successfully', data['message'])

    def test_delete_nonexistent_record(self):
        request = self.factory.delete('/fake-url')
        request.user = self.user
        response = RecordViews.singular_endpoint(request, record_id=9999)  # Non-existent record ID

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Record not found', data['error'])

    def test_delete_unauthorized_user(self):
        # Assuming the user can only delete their own records
        another_user = User.objects.create_user(username='another_user', password='pass')
        request = self.factory.delete('/fake-url')
        request.user = another_user  # Different user
        response = RecordViews.singular_endpoint(request, record_id=self.record.id)

        self.assertEqual(response.status_code, 404)
        self.record.refresh_from_db()
        self.assertIsNone(self.record.deleted_at)  # Record should not be deleted

    def test_cascade_update_balance(self):
        # Create a subsequent record to test cascade updates
        subsequent_record = Record.objects.create(
            user=self.user,
            operation=self.operation,
            amount=200,
            user_balance=4900,  # This should get updated
            operation_response='Success',
            created_at=timezone.now() + timezone.timedelta(hours=1)
        )

        request = self.factory.delete('/fake-url')
        request.user = self.user
        response = RecordViews.singular_endpoint(request, record_id=self.record.id)

        subsequent_record.refresh_from_db()
        self.assertEqual(subsequent_record.user_balance, 5000)  # Check if balance is updated correctly
