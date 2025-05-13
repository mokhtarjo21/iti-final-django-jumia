from .views import *
from django.urls import path , include

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('check_email', check_email.as_view(), name='check_email'),
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path ('active', ActivationView.as_view(), name='activate'),
    path('resend', send_activation_email, name='active'),
    path ('who', who, name='who'),
    path('delete', DeleteUserView.as_view(), name='delete_user'),
  
]
