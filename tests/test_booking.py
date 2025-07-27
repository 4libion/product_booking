from django.utils import timezone

from bookings.serializers import BookingSerializer
from bookings.tasks import clean_expired_booking
from bookings.models import Booking, Status

from unittest.mock import patch
from datetime import datetime
from datetime import timedelta
import pytest
import logging
import time

from rest_framework.exceptions import ErrorDetail


logger = logging.getLogger(__name__)

BOOKING_LIST_CREATE_URL = 'bookings:booking-list-create'
BOOKING_CONFIRM_URL = 'bookings:booking-confirm'
BOOKING_CANCEL_URL = 'bookings:booking-cancel'



@pytest.mark.django_db
def test_create_booking(
    client,
    create_product,
):
    product = create_product()
    url = BOOKING_LIST_CREATE_URL
    data = {
        'product': product.id,
        'quantity': 5
    }

    response = client(
        url=url,
        method='post',
        data=data
    )
    assert response.status_code == 201
    assert Booking.objects.count() == 1

    booking = Booking.objects.first()
    assert booking.product == product
    assert booking.quantity == 5
    assert booking.status == Status.PENDING
    assert booking.celery_task_id is not None
    assert booking.expired_at is None
    assert isinstance(booking.created_at, datetime)

@pytest.mark.django_db
def test_get_bookings(
    client,
    create_product,
    create_booking,
):
    product = create_product()
    booking_1 = create_booking(product=product, quantity=5)
    booking_2 = create_booking(product=product, quantity=10)
    booking_3 = create_booking(product=product, quantity=15)
    
    url = BOOKING_LIST_CREATE_URL
    response = client(
        url=url,
        method='get',
    )
    assert response.status_code == 200
    assert len(response.data) == 3

    expected_data = BookingSerializer([booking_1, booking_2, booking_3], many=True).data
    assert response.data == expected_data

@pytest.mark.django_db
def test_product_quantity_after_booking(
    client,
    create_product,
    create_booking,
):
    product = create_product()
    create_booking(product=product, quantity=5)
    product.refresh_from_db()
    assert product.quantity == 95

@pytest.mark.django_db
def test_confirm_booking(
    client,
    create_product,
    create_booking,
):
    product = create_product()
    booking = create_booking(product=product)

    url = BOOKING_CONFIRM_URL
    data={'booking_id': booking.id}
    response = client(
        url=url,
        method='post',
        data=data,
    )

    assert response.status_code == 200
    assert response.data['status'] == 'confirmed'
    booking.refresh_from_db()
    assert booking.status == Status.CONFIRMED

@pytest.mark.django_db
def test_cancel_booking(client, create_product, create_booking):
    product = create_product()
    booking = create_booking(product=product)

    url = BOOKING_CANCEL_URL
    data={'booking_id': booking.id}
    response = client(
        url=url,
        method='post',
        data=data,
    )

    assert response.status_code == 200
    assert response.data['status'] == 'canceled'
    booking.refresh_from_db()
    assert booking.status == Status.CANCELED

@pytest.mark.django_db
def test_confirm_booking_invalid_id(client):
    url = BOOKING_CONFIRM_URL
    data={'booking_id': 999}
    response = client(
        url=url,
        method='post',
        data=data,
    )

    assert response.status_code == 404

@pytest.mark.django_db
def test_confirm_expired_booking(
        client,
        create_product,
        create_booking,
        expire_booking,
):
    product = create_product()
    booking = create_booking(product=product)
    expired_booking = expire_booking(booking=booking)

    url = BOOKING_CONFIRM_URL
    data={'booking_id': expired_booking.id}
    response = client(
        url=url,
        method='post',
        data=data,
    )

    assert response.status_code == 400
    assert response.data == [ErrorDetail(string='Booking cannot be confirmed', code='invalid')]

@pytest.mark.django_db
def test_cancel_expired_booking(
        client,
        create_product,
        create_booking,
        expire_booking,
):
    product = create_product()
    booking = create_booking(product=product)
    expired_booking = expire_booking(booking=booking)

    url = BOOKING_CANCEL_URL
    data={'booking_id': expired_booking.id}
    response = client(
        url=url,
        method='post',
        data=data,
    )

    assert response.status_code == 400
    assert response.data == [ErrorDetail(string='Booking cannot be cancelled', code='invalid')]

@pytest.mark.django_db
def test_clean_expired_booking(create_product, create_booking):
    product = create_product()
    booking = create_booking(product=product, quantity=10)

    assert product.quantity == 90
    assert booking.status == Status.PENDING

    clean_expired_booking(booking.id)

    booking.refresh_from_db()
    product.refresh_from_db()

    assert booking.status == Status.EXPIRED
    assert booking.expired_at is not None
    assert product.quantity == 100
