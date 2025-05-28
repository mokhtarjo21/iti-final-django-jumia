from django.urls import path , include
from .views import *
urlpatterns = [
    path('', api_request_response, name='api_request_response'),
    
   
]