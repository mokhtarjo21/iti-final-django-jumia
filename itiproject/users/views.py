
from django.core.mail import send_mail
from django.conf import settings

from django.conf import settings
from django.utils.timezone import now 
from django.contrib.auth.models import AnonymousUser
from django.views import View
from users.models import User ,User_active
import random
import string
from datetime import datetime, timedelta
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
# from .savers import UserSerializer
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
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({'username': self.user.username})
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class check_email(APIView):
    def post(self,request):
        email = request.data.get('email')
        exists = User.objects.filter(email=email).exists()
        print("Email:", email)
        if exists:
            user = User.objects.get(email=email)
            active = user.active_email
            print("Email:", email)
        
            if active:
                return Response({'user': '1'}, status=status.HTTP_200_OK)

        return Response({'user': '0'}, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            csrf_token = get_token(request)  # اختياري لأنك سترسله ككوكي تلقائيًا
            return Response({'message': 'Login successful'}, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
    def get(self, request):
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token})
       
class RegisterView(APIView):
    def post(self, request):
   
        email = request.data.get('email')
        
        
        print("Email:", email)

        if not email :
            
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if User_active.objects.filter(user=user).exists():
                send(email)
       
            return Response({'error': 'Email already exists.'}, status=status.HTTP_200_OK)

       # hashed_password = make_password(password)
        User.objects.create(email=email)
        user = User.objects.get(email=email)

        activation_code = ''.join(random.choices(string.digits, k=4))
        User_active.objects.create(user=user, active=activation_code)
        send(email)
        #token, created = Token.objects.get_or_create(user=user)

        return Response({'state': 'done'}, status=status.HTTP_201_CREATED)
def send(email):
    user = User.objects.get(email=email)
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
@api_view(['post'])
def send_activation_email(request):
    email = request.data.get('email')
    user = User.objects.get(email=email)
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

    
class ActivationView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        print("code:", code)
        user = User.objects.get(email=email)
        use_active = User_active.objects.get(user=user)
        if use_active.active == code and now() - use_active.time_send < timedelta(days=1):
            user.active_email = True
            user.save()
            return Response({'message': 'Your account has been activated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Activation code is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)
 


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
