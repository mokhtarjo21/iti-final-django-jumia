from .views import *
from django.urls import path , include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path ('<int:id>/<str:activation_code>', ActivationView.as_view(), name='activate'),
    path('active/<int:id>', ResendActivationCodeView.as_view(), name='active'),
    path ('who', who, name='who'),
    path('delete', DeleteUserView.as_view(), name='delete_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh token
    path('login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('info/',userSaveInfo.as_view(), name='user_info'),

  
]
