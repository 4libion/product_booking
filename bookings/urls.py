from django.urls import path

from bookings.views import (
    BookingCancelView,
    BookingConfirmView,
    BookingListCreateView,
)


app_name = 'bookings'

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),
    path('confirm/', BookingConfirmView.as_view(), name='booking-confirm'),
    path('cancel/', BookingCancelView.as_view(), name='booking-cancel'),
]
