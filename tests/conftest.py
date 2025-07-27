from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from bookings.tasks import clean_expired_booking
from rest_framework.test import APIClient
import pytest
from datetime import timedelta

from bookings.models import Booking, Status
from products.models import Product


@pytest.fixture
def client():
    def _client(
        url,
        method,
        data=None,
        content_type='json',
        kwargs=None,
    ):
        client = APIClient()
        url = reverse(url, kwargs=kwargs)

        method = method.lower()
        if method == 'get':
            return client.get(path=url)
        elif method == 'post':
            return client.post(path=url, data=data, format=content_type)
        elif method == 'put':
            return client.put(path=url, data=data, format=content_type)
        elif method == 'patch':
            return client.patch(path=url, data=data, format=content_type)
        elif method == 'delete':
            return client.delete(path=url, data=data, format=content_type)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    return _client

@pytest.fixture
def create_product():
    def _create_product(
        name="Test Product",
        quantity=100,
    ):
        return Product.objects.create(
            name=name,
            quantity=quantity,
        )
    return _create_product

@pytest.fixture
def create_booking():
    def _create_booking(
        product,
        quantity=10,
        status=Status.PENDING,
        celery_task_id=None,
        schedule_task=False,
        expired_at=None,
    ):
        booking = Booking.objects.create(
            product=product,
            quantity=quantity,
            status=status,
            celery_task_id=celery_task_id,
            expired_at=expired_at,
        )
        product.quantity -= booking.quantity
        product.save()
    
        if schedule_task:
            expiry_time = timezone.now() + timedelta(seconds=7)
            task = clean_expired_booking.apply_async(
                args=[booking.id],
                eta=expiry_time,
            )
            booking.celery_task_id = task.id
            booking.save(update_fields=['celery_task_id'])
        return booking
    return _create_booking

@pytest.fixture
def expire_booking():
    def _expire_booking(
        booking
    ):
        booking.status = Status.EXPIRED
        booking.expired_at = timezone.now()
        booking.save()
        return booking
    return _expire_booking