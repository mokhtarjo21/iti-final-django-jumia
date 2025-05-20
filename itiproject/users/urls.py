from .views import *
from django.urls import path , include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('check_email', check_email.as_view(), name='check_email'),
    path('check_vendor', check_vendor.as_view(), name='check_vendor'),
    path('register', RegisterView.as_view(), name='register'),
    path('register_vendor', RegisterVendor.as_view(), name='register_vendor'),
    path('logout', LogoutView.as_view(), name='logout'),
    path ('active', ActivationView.as_view(), name='activate'),
    path('resend', send_activation_email, name='active'),
    path ('who', who, name='who'),
    path('delete', DeleteUserView.as_view(), name='delete_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh token
    path('login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('info/',userSaveInfo.as_view(), name='user_info'),
    path('profile/',profile.as_view(), name='user_update_info'),

  
]
