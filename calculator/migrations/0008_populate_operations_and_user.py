from django.db import migrations
from django.contrib.auth.models import User
from calculator.models import Record, Operation
import random


def create_user_and_operations(apps, schema_editor):
    # Create a new user
    new_user = User.objects.create(username='testuser')
    new_user.set_password('123qweasd')
    new_user.save()

    user_profile = new_user.userprofile
    user_profile.balance = 7000
    user_profile.save()

    # Create a thousand random records
    operations = Operation.objects.all()
    for _ in range(1000):
        operation = random.choice(operations)

        record = Record.objects.create(
            user=new_user,
            operation=operation,
            amount=operation.cost,
            user_balance=user_profile.balance - operation.cost,
            operation_response=random.randint(1, 100)
        )

        # Calculate new balance after each operation
        user_profile.balance = record.user_balance
        user_profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0007_operation_name'),
    ]

    operations = [
        migrations.RunPython(create_user_and_operations),
    ]
