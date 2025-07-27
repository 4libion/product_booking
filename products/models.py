from django.db import models

import uuid

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["unique_id"]),
        ]

    def __str__(self):
        return f"{self.name} (Unique id: {self.unique_id})"
