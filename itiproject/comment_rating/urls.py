from .views import *
from django.urls import path , include

urlpatterns = [
    path('', CommentAPIView.as_view(), name='CommentView'),
    path('/<int:id>', CommentAPIView.as_view(), name='CommentView'),
    path('/rate/<int:id>', RateAPIView.as_view(), name='getrate'),
    path('/rate', RateAPIView.as_view(), name='rate'),
     
]