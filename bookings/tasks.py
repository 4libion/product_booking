from django.utils import timezone
from bookings.models import Booking, Status
from celery import shared_task


@shared_task
def clean_expired_booking(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, status=Status.PENDING)
        booking.status = Status.EXPIRED
        booking.expired_at = timezone.now()
        booking.save()

        product = booking.product
        product.quantity += booking.quantity
        product.save()
    except Booking.DoesNotExist:
        pass
