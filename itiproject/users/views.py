
from django.core.mail import send_mail
from django.conf import settings

from django.conf import settings
from django.utils.timezone import now 
from django.contrib.auth.models import AnonymousUser
from django.views import View
from users.models import *
import random
import string
from datetime import datetime, timedelta
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .serializers import RegisterSerializer
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
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({'username': self.user.username})
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    print("CustomTokenObtainPairView")
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
    def get(self,request):
        
        vendor = request.user.is_staff
        if vendor:
            return Response({'user':'1'},status=status.HTTP_200_OK)
        return Response({'user':'0'},status=status.HTTP_200_OK)
class check_vendor(APIView):        
    def post(self,request):
        email = request.data.get('email')
        print("Email:", email)
        exists = User.objects.filter(email=email).exists()
        if exists:
            user = User.objects.get(email=email)
            stuf = user.is_staff
            print("Email:", email)
            print("stuf:", stuf)
            if stuf:
                print
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
class RegisterVendor(APIView):
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
        User.objects.create(email=email, is_staff=True)
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['get'])
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

class userSaveInfo(APIView):
    

    def post(self, request):
        user = User.objects.get(email=request.data.get('email')) 
        print("User:", user)
        
            
        data = request.data

        user.first_name = data.get('firstName', user.first_name)
        user.last_name = data.get('lastName', user.last_name)
        user.Birthdate = data.get('dob', user.Birthdate)
       
        user.phone = data.get('phone', user.phone)
        user.address = data.get('address', user.address)
        user.city = data.get('city', user.city)
        user.countrycode = data.get('countrycode', user.countrycode)
        

        if 'password' in data:
            password = data['password']
            if password:
                user.password = make_password(password)

        if 'picture' in request.FILES:
            user.picture = request.FILES['picture']
        if 'accountType' in data:
            accountType = data['accountType']
            shopName = data.get('shopName')
            shippingZone = data.get('shippingZone')
            referralSource = data.get('referralSource')
            Vendor.objects.update_or_create(
                user=user,
                defaults={
                    'accountType': accountType,
                    'shopName': shopName,
                    'shippingZone': shippingZone,
                    'referralSource': referralSource
                }
            )
        user.save()

        return Response({'message': 'User information updated successfully.'}, status=status.HTTP_200_OK)



class profile(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        users = request.user
        serializer = RegisterSerializer(users, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            user = request.user
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
