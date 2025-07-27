from django.db import models
from django.utils import timezone
from django.conf import settings

from products.models import Product

# Create your models here.
class Status(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    CANCELED = 'canceled', 'Canceled'
    EXPIRED = 'expired', 'Expired'


class Booking(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bookings')
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        return f"Booking #{self.id} for {self.product.name} [{self.status}]"
    