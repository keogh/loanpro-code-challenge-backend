from django.test import TestCase
from calculator.models import Operation


class OperationModelTests(TestCase):

    def test_cost_default_value(self):
        """Test default value of cost."""
        operation = Operation(type='Maintenance')
        operation.save()
        self.assertEqual(operation.cost, 0)

    def test_unique_type_constraint(self):
        """Test that the type field must be unique."""
        Operation.objects.create(type='Maintenance', cost=100)
        with self.assertRaises(Exception):
            Operation.objects.create(type='Maintenance', cost=200)

    def test_field_properties(self):
        """Test the properties of model fields."""
        operation = Operation(type='Repair')
        operation.save()
        retrieved_operation = Operation.objects.get(type='Repair')

        # Test max_length attribute of type field
        self.assertEqual(Operation._meta.get_field('type').max_length, 100)

        # Check if cost is an instance of PositiveIntegerField
        self.assertIsInstance(retrieved_operation.cost, int)
        self.assertTrue(retrieved_operation.cost >= 0)

