from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import extend_schema
from celery import current_app

from django.utils import timezone

from datetime import timedelta

from bookings.models import Booking, Status
from bookings.serializers import BookingIdSerializer, BookingSerializer
from bookings.tasks import clean_expired_booking


BOOKING_EXPIRY_MINUTES = 1


class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')

        if product.quantity < quantity:
            raise ValidationError('Not enough product in stock')
        
        product.quantity -= quantity
        product.save()

        booking = serializer.save()

        expiry_time = timezone.now() + timedelta(minutes=BOOKING_EXPIRY_MINUTES)
        task = clean_expired_booking.apply_async(
            args=[booking.id],
            eta=expiry_time
        )

        booking.celery_task_id = task.id
        booking.save(update_fields=["celery_task_id"])
        print(f"Scheduled expiration task for booking {booking.id} at {expiry_time}")


@extend_schema(
    request=BookingIdSerializer,
    responses=BookingSerializer,
    description="Confirm a booking by ID"
)
class BookingConfirmView(APIView):
    def post(self, request):
        booking_id = request.data.get("booking_id")
        if not booking_id:
            raise ValidationError("Booking id is required")
        
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            raise NotFound("Booking not found")
        
        if booking.status != Status.PENDING:
            raise ValidationError("Booking cannot be confirmed")
        
        if booking.celery_task_id:
            try:
                current_app.control.revoke(booking.celery_task_id, terminate=True)
                print(f"Canceled expiration task {booking.celery_task_id} for booking {booking.id}")
            except Exception as e:
                print(f"Failed to cancel task {booking.celery_task_id} for booking {booking.id}: {e}")
            booking.celery_task_id = None
            booking.save(update_fields=["celery_task_id"])
        
        booking.status = Status.CONFIRMED
        booking.save()

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@extend_schema(
    request=BookingIdSerializer,
    responses=BookingSerializer,
    description="Cancel a booking by ID"
)
class BookingCancelView(APIView):
    def post(self, request):
        booking_id = request.data.get("booking_id")
        if not booking_id:
            raise ValidationError("Booking id is required")
        
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            raise NotFound("Booking not found")
        
        if booking.status != Status.PENDING:
            raise ValidationError("Booking cannot be cancelled")
        
        if booking.celery_task_id:
            try:
                current_app.control.revoke(booking.celery_task_id, terminate=True)
                print(f"Canceled expiration task {booking.celery_task_id} for booking {booking.id}")
            except Exception as e:
                print(f"Failed to cancel task {booking.celery_task_id} for booking {booking.id}: {e}")
            booking.celery_task_id = None
            booking.save(update_fields=["celery_task_id"])
        
        product = booking.product
        product.quantity += booking.quantity
        product.save()

        booking.status = Status.CANCELED
        booking.save()

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
