from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet

router = DefaultRouter()
router.register(r'cart', CartItemViewSet, basename='cart')


urlpatterns = [
     path('cart/', CartItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='cart-list'),
     path('cart/<int:pk>/', CartItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='cart-detail'),
]
