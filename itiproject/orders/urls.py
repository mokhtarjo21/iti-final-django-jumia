from django.urls import path
from .views import *



urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path("vendor-items/", VendorOrderItemsView.as_view()),
    path("vendor-items/<int:pk>/", VendorOrderItemsView.as_view()),  # PATCH endpoint
    path('paymob/', PaymobPaymentView.as_view(), name='paymob-payment'),
    path('check/<slug:product_id>/',UserOrder.as_view(),name='check-order')

]
