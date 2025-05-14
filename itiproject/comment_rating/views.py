from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *

import copy
from django.http import JsonResponse
import json

class CommentAPIView(APIView):
   
    def post(self, request):
        content = request.data.get('contents')
        print(content,'content')
        product_id = request.data.get('id')
        product = product.objects.get(id=product_id)
        user = request.user
        print(user,'user')
        # Create a new comment
        comment = Comment.objects.create(
            content=content,
            product=product,
            user=user
        )
        return Response({'state': 'success'}, status=status.HTTP_201_CREATED)
    def put(self, request, pk, *args, **kwargs):
        """
        Update an existing comment.
        """
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def get(self, request,id):
        
       
        comments_list = []
        comment_dict =[]
        user = request.user
        comments_list.append([user.picture.url,user.id])
        comments = Comment.objects.filter(product=id)
        for comment in comments:
            user_profile = User.objects.get(id=comment.user.id)
            comment_dict.append( {
                'id': comment.id,  # Include the comment ID or any other fields you need
                'fname': user_profile.frist_name,
                'user_photo': user_profile.picture.url,
                'content': comment.content,
                
                'created_at': comment.created_at,
                
            })
            
        # Add the comment dictionary to the list
        comments_list.append(comment_dict)
        
        return JsonResponse(comments_list, safe=False, status=status.HTTP_200_OK)
        # return JsonResponse({comments}, status=status.HTTP_200_OK)
        

class RateAPIView(APIView):
    def post(self, request):
        rate = request.data.get('rate')
        user = request.user
        product_id = request.data.get('id')
        if Rating.objects.filter(user=user.id,product=product_id ).exists():
            current_rete = Rating.objects.get(user=user.id,product=product_id )
            current_rete.value = rate
            current_rete.save()
        else :
            product = product.objects.get(id=product_id)
            new_rate = Rating.objects.create(
                user=user,
                product=product,
                value=rate
            )
        return Response({'state': 'success'}, status=status.HTTP_201_CREATED)
    def get(self, request, id):
        rates = Rating.objects.filter(product=id)
        rate_list = []
        for rate in rates:
            user_profile = User.objects.get(id=rate.user.id)
            rate_list.append({
                'id': rate.id,
                'fname': user_profile.fname,
                'user_photo': user_profile.picture.url,
                'rate': rate.value
            })
       
        return JsonResponse(rate_list, safe=False, status=status.HTTP_200_OK)
