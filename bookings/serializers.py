from bookings.models import Booking
from rest_framework import serializers


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ['status', 'expired_at', 'created_at', 'celery_task_id']


class BookingIdSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
