from django.urls import path
from .views import CheckoutView, VendorOrderItemsView

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path("vendor-items/", VendorOrderItemsView.as_view()),
    path("vendor-items/<int:pk>/", VendorOrderItemsView.as_view()),  # PATCH endpoint
]
