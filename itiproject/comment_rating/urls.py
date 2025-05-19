from .views import *
from django.urls import path , include

urlpatterns = [
    path('', CommentAPIView.as_view(), name='CommentView'),
    path('<slug:id>', CommentAPIView.as_view(), name='CommentView'),
    path('rate/<slug:slug>/', RateAPIView.as_view(), name='getrate'),
    path('rate', RateAPIView.as_view(), name='rate'),
     
]