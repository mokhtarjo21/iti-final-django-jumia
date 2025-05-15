from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Product
from .serializers import (
    ProductListSerializer, CategoryListSerializer, CategoryDetailSerializer, CategoryCreateUpdateSerializer,
    ProductCreateUpdateSerializer)
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

# Create your views here.

def get_descendant_ids(category):
    """Recursively get all descendant category IDs."""
    ids = [category.id]
    for child in category.children.all():
        ids.extend(get_descendant_ids(child))
    return ids

class CategoryProductsView(APIView):
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
            category_ids = get_descendant_ids(category)
            products = Product.objects.filter(category_id__in=category_ids)

            # Apply filters (all in DB, not Python)
            brand = request.GET.get('brand')
            if brand:
                brand_names = brand.split(',')
                products = products.filter(brand__name__in=brand_names)

            color = request.GET.get('color')
            if color:
                color_names = color.split(',')
                products = products.filter(colors__name__in=color_names)

            min_price = request.GET.get('min_price')
            if min_price:
                products = products.filter(price__gte=min_price)
            max_price = request.GET.get('max_price')
            if max_price:
                products = products.filter(price__lte=max_price)

            products = products.distinct()  # Avoid duplicates if filtering by M2M

            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 10
            paginated_products = paginator.paginate_queryset(products, request)
            serializer = ProductListSerializer(paginated_products, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

# List all categories as a tree
class CategoryTreeView(generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategoryListSerializer

# Retrieve category details by pk
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    lookup_field = 'pk'

# Retrieve category details by slug
class CategoryDetailBySlugView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug'

# Create a category
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer

# Update a category
class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    lookup_field = 'pk'

# Delete a category
class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    lookup_field = 'pk'

# # Product CRUD
# use 127.0.0.1:8000/api/category/shoes/products
# class ProductListView(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductListSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    lookup_field = 'pk'

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    lookup_field = 'pk'

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    lookup_field = 'pk'
