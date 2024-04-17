from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from calculator.models import Operation
from calculator.models import Record

User = get_user_model()


class RecordModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.operation = Operation.objects.create(type='Addition', cost=100)

    def test_record_creation(self):
        record = Record.objects.create(
            operation=self.operation,
            user=self.user,
            amount=500,
            user_balance=1500,
            operation_response=10,
            created_at=timezone.now()
        )
        self.assertEqual(record.operation.type, 'Addition')
        self.assertEqual(record.user.username, 'testuser')
        self.assertEqual(record.amount, 500)
        self.assertEqual(record.user_balance, 1500)
        self.assertEqual(record.operation_response, 10)

    def test_record_default_time(self):
        # Test the default time of created_at
        record = Record.objects.create(
            operation=self.operation,
            user=self.user,
            amount=100,
            user_balance=2000,
            operation_response=10
        )
        self.assertAlmostEqual(record.created_at, timezone.now(), delta=timezone.timedelta(seconds=1))

    def test_cascade_delete_user(self):
        # Test cascading delete on user
        record = Record.objects.create(
            operation=self.operation,
            user=self.user,
            amount=300,
            user_balance=500,
            operation_response='Processed'
        )
        self.user.delete()
        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(pk=record.pk)

    def test_cascade_delete_operation(self):
        record = Record.objects.create(
            operation=self.operation,
            user=self.user,
            amount=100,
            user_balance=250,
            operation_response='Completed'
        )
        self.operation.delete()
        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(pk=record.pk)
