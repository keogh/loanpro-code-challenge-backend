from django.db import models


class Operation(models.Model):
    type = models.CharField(max_length=100, unique=True)
    cost = models.PositiveIntegerField(default=0, null=False)
