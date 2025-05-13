from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import HeroSlider, Category, Banner, Product
from .serializers import HeroSliderSerializer, CategorySerializer, BannerSerializer, ProductSerializer

@api_view(['GET'])
def get_hero_sliders(request):
    sliders = HeroSlider.objects.all()
    serializer = HeroSliderSerializer(sliders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_banners(request):
    banners = Banner.objects.all()
    serializer = BannerSerializer(banners, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)