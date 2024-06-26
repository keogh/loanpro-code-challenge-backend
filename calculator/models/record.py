from django.db import models
from django.conf import settings
from django.utils import timezone


class Record(models.Model):
    operation = models.ForeignKey('calculator.Operation', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(null=False)
    user_balance = models.IntegerField(null=False)
    operation_response = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now, null=False)
    deleted_at = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return f"Record {self.pk} - User: {self.user.username} - Operation: {self.operation.type}"