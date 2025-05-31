from django.shortcuts import render
from rest_framework.views import APIView
from django.http import JsonResponse
import json
from openai import OpenAI
from openai import RateLimitError
from rest_framework.decorators import api_view
from .models import ChatMessage
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import csrf_exempt
from products.models import Product

def get_products_data():
    try:
        products = Product.objects.all()
        return "\n".join([f"{p.name} - {p.price} EGP" for p in products])
    except Exception:
        return "No products available yet."

def get_system_message():
    products_info = get_products_data()
    return f"""
أنت مساعد ذكي لموقع تجارة إلكترونية. عندك فقط البيانات التالية عن المنتجات:

{products_info}

لا تتحدث عن أي شيء خارج المنتجات. جاوب فقط باستخدام البيانات المعطاة.
"""

response = "Of course! Let's focus on product!"
history_anonymous = [{"role": "user", "content": get_system_message()}, {"role": "assistant", "content": response}]

@csrf_exempt 
@api_view(['POST'])
def api_request_response(request):
   message = request.data.get('message')
   print(message)
   user = request.user
  
   if isinstance(user, AnonymousUser):
      history_anonymous.append({"role": "user", "content": message})
      try:
         client = OpenAI(api_key="Api-your-key") 
         completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history_anonymous,
            max_tokens=100,
         )
         response = completion.choices[0].message.content
         print(response)
         history_anonymous.append({"role": "assistant", "content": response})
         
         return JsonResponse({'response': response})
      except RateLimitError:
         return JsonResponse({'error': 'You have exceeded your API quota. Please check your OpenAI plan.'}, status=429)
   else:
      if request.user.is_authenticated:
         chat_message, created = ChatMessage.objects.get_or_create(user=user, defaults={'messages': json.dumps(history_anonymous)})
         history = json.loads(chat_message.messages)
            
         history.append({"role": "user", "content": message})
         try:
            print(user)
            client = OpenAI(api_key="Api-your-key")
            completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            max_tokens=100,
            )
            response = completion.choices[0].message.content
            print(response)
            history.append({"role": "assistant", "content": response})
            
            # Save the chat message to the database
            chat_message.messages = json.dumps(history)
            chat_message.save()
            
            return JsonResponse({'response': response})
         except RateLimitError:
            return JsonResponse({'error': 'You have exceeded your API quota. Please check your OpenAI plan.'}, status=429)
      else:
         return JsonResponse({'error': 'User not authenticated'}, status=401)