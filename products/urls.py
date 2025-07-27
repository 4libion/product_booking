from django.urls import path

from products.views import (
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
)


app_name = 'products'

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
]