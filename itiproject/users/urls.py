from .views import *
from django.urls import path , include

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path ('<int:id>/<str:activation_code>', ActivationView.as_view(), name='activate'),
    path('active/<int:id>', ResendActivationCodeView.as_view(), name='active'),
    path ('who', who, name='who'),
    path('delete', DeleteUserView.as_view(), name='delete_user'),
  
]
