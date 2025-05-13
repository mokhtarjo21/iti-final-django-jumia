from django.shortcuts import render ,redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now 
from django.contrib.auth.models import AnonymousUser
from django.views import View
from users.models import User ,User_active
import random
import string
from datetime import datetime, timedelta


from django.http import JsonResponse
import json
from openai import OpenAI ,RateLimitError
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import check_password, make_password
from .serializers import RegisterSerializer



class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print("Email:", email)

        try:
            current_user = User.objects.get(email=email)
            print('check user is exist')
        except User.DoesNotExist:
            return Response({'error': 'Account does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, current_user.password):
            print('check password')
            if not current_user.active_email:
                return Response({'redirect': 'for active email'}, status=status.HTTP_403_FORBIDDEN)
            token, created = Token.objects.get_or_create(user=current_user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email or password is incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)
class RegisterView(APIView):
    def post(self, request):
   
        email = request.data.get('email')
        password = request.data.get('password')

        
        print("Email:", email)
        print("Password:", password)

        if not email or not password:
            print("Error: Missing email or password")
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = make_password(password)
        User.objects.create(email=email, password=hashed_password)
        user = User.objects.get(email=email)

        activation_code = ''.join(random.choices(string.digits, k=4))
        User_active.objects.create(user=user, active=activation_code)

        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

class ActivationView(APIView):
    def get(self, request, id, activation_code):
        try:
            user = User.objects.get(id=id)
            use_active = User_active.objects.get(user=user)

            if use_active.active == activation_code and now() - use_active.time_send < timedelta(days=1):
                user.active_email = True
                user.save()
                return Response({'message': 'Your account has been activated successfully.'}, status=status.HTTP_200_OK)

            return Response({'message': 'Activation link is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except User_active.DoesNotExist:
            return Response({'error': 'Activation record does not exist.'}, status=status.HTTP_404_NOT_FOUND)

class ResendActivationCodeView(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            use_active = User_active.objects.get(user=user)

            if now() - use_active.time_send > timedelta(days=1):
                activation_code = ''.join(random.choices(string.digits, k=4))
                use_active.active = activation_code
                use_active.time_send = now()
                use_active.save()

            activation_code = use_active.active
            subject = 'Account Activation'
            message = f'Your activation code is: {activation_code}'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            return Response({'message': 'Please check your email to activate your account.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except User_active.DoesNotExist:
            return Response({'error': 'Activation record does not exist.'}, status=status.HTTP_404_NOT_FOUND)



class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


@api_view(['post'])
def who(request):
    userw = request.user
    if isinstance(userw, AnonymousUser):
        return JsonResponse({'response':{'state': False}})
    else:
        user_data = {
            'state': True,
            'id': userw.id,
            'email': userw.email,
            'first_name': userw.first_name,
            'last_name': userw.last_name,
            'pciture': userw.picture.url if userw.picture else None
        }
        if request.user.is_superuser:
            user_data['superuser'] = True
        else:
            user_data['superuser'] = False
        return JsonResponse({'response': user_data})
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        password = request.data.get('password')
        user = request.user

       
        if not user.check_password(password):
            return Response({'error': 'Password is incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)

        user.delete()
        return Response({'message': 'Your account has been deleted.'}, status=status.HTTP_204_NO_CONTENT)
