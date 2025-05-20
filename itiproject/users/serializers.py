from .models import User
from django.contrib.auth.hashers import make_password
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone','city','address']

   
