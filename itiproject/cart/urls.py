from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet

router = DefaultRouter()
router.register(r'cart', CartItemViewSet, basename='cart')

urlpatterns = router.urls
