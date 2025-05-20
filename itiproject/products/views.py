from django.shortcuts import render
from django.db.models import Q, F, ExpressionWrapper, FloatField
from itertools import chain
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product, Brand
from .serializers import (
    ProductListSerializer, CategoryListSerializer, CategoryDetailSerializer, CategoryCreateUpdateSerializer,
    ProductCreateUpdateSerializer)
from rest_framework import generics
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
                brand_slugs = brand.split(',')
                products = products.filter(brand__slug__in=brand_slugs)

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
            
            products = products.annotate(
                discount_percentage=ExpressionWrapper(
                    (F('price') - F('sale_price')) / F('price') * 100,
                    output_field=FloatField()
                )
            )

            discount = request.GET.get('discount_min')
            if discount:
                products = products.filter(discount_percentage__gte=float(discount))

            featured = request.GET.get('is_featured')
            if featured:
                products = products.filter(is_featured=True)

            # Ordering logic (same as ProductListView)
            ordering = request.GET.get('ordering')
            if ordering == 'popularity':
                products = products.order_by('-quantity_sold')
            elif ordering == 'newest':
                products = products.order_by('-created_at')
            elif ordering == 'price_asc':
                products = products.order_by('price')
            elif ordering == 'price_desc':
                products = products.order_by('-price')
            elif ordering == 'rating':
                products = products.order_by('-rating_average')
            else:
                products = products.order_by('-quantity_sold')

            products = products.distinct()  # Avoid duplicates if filtering by M2M
            
            # total number of products to show in the response
            products_count = products.count()

            # Get all unique brands for this category and its subcategories
            category_brands = Brand.objects.filter(
                products__category_id__in=category_ids
            ).distinct().values('name', 'slug', 'image')

            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 10 # You can adjust this or make it configurable
            paginated_products = paginator.paginate_queryset(products, request)
            
            # Serialize the data
            product_serializer = ProductListSerializer(paginated_products, many=True)
            
            # Get pagination data
            pagination_data = {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'total_pages': paginator.page.paginator.num_pages,
            }
            
            response_data = {
                'products_count': products_count,
                'products': product_serializer.data,
                'brands': list(category_brands),
                'pagination': pagination_data
            }

            return Response(response_data)

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

# class ProductSearchView(APIView):
#     def get(self, request):
#         # Get the search query from URL parameters
#         search_query = request.GET.get('q', '')
        
#         if not search_query:
#             return Response({"error": "Please provide a search query"}, status=400)
            
#         # Search in multiple fields
#         products = Product.objects.filter(
#             Q(name__icontains=search_query) |
#             Q(description__icontains=search_query) |
#             Q(brand__name__icontains=search_query) |
#             Q(category__name__icontains=search_query)
#         ).distinct()
#             # Apply filters similar to CategoryProductsView
#         brand = request.GET.get('brand')
#         if brand:
#             brand_names = brand.split(',')
#             products = products.filter(brand__name__in=brand_names)

#         color = request.GET.get('color')
#         if color:
#             color_names = color.split(',')
#             products = products.filter(colors__name__in=color_names)

#         min_price = request.GET.get('min_price')
#         if min_price:
#             products = products.filter(price__gte=min_price)
        
#         max_price = request.GET.get('max_price')
#         if max_price:
#             products = products.filter(price__lte=max_price)

#         # appending total number of products to the response
#         total_count = products.count()
#         # Pagination
#         paginator = PageNumberPagination()
#         paginator.page_size = 4  # Number of products per page
#         paginated_products = paginator.paginate_queryset(products, request)
#         serializer = ProductListSerializer(paginated_products, many=True)
        
#         # Add total products to the response by creating a custom response
#         response_data = {
#             'count': total_count,  
#             'results': serializer.data,
#             'next': paginator.get_next_link(),
#             'previous': paginator.get_previous_link(),
#             'current_page': paginator.page.number,
#             'total_pages': paginator.page.paginator.num_pages,
#             'page_size': paginator.page_size
#         }
#         return Response(response_data)

class SearchSuggestionsView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:  # Only show suggestions after 2 characters
            return Response([])

        # Limit results per category
        limit = 2

        # Get matching products
        products = Product.objects.filter(
            name__icontains=query
        ).values('id', 'name', 'slug')[:limit]

        # Get matching categories
        categories = Category.objects.filter(
            name__icontains=query
        ).values('id', 'name', 'slug')[:limit]

        # Get matching brands
        brands = Brand.objects.filter(
            name__icontains=query
        ).values('id', 'name', 'slug', 'image')[:limit]

        # Prepare response with type identification
        suggestions = {
            'products': [{
                'id': p['id'],
                'name': p['name'],
                'slug': p['slug'],
                'type': 'product',
                'url': f'/product/{p["slug"]}'
            } for p in products],
            
            'categories': [{
                'id': c['id'],
                'name': c['name'],
                'slug': c['slug'],
                'type': 'category',
                'url': f'/category/{c["slug"]}'
            } for c in categories],
            
            'brands': [{
                'id': b['id'],
                'name': b['name'],
                'slug': b['slug'],
                'image': b['image'],
                'type': 'brand',
                'url': f'/brand/{b["slug"]}'
            } for b in brands]
        }

        return Response(suggestions)

# converted product search into a general view for listing, searching, and filtering by recentlyadded, sponsered
# , brand-slug, minprice, highprice and color in products
class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        # Search functionality
        search_query = request.GET.get('q', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            ).distinct()
        
        # Get sponsored products
        sponsored = request.GET.get('sponsored')
        if sponsored:
            products = products.filter(is_sponsored=True)
            
        # Get recently added products
        recent = request.GET.get('recent')
        if recent:
            try:
                limit = int(recent)
                products = products.order_by('-created_at')[:limit]
            except ValueError:
                pass
            
        # Get best sellers
        best_sellers = request.GET.get('best_sellers')
        if best_sellers:
            try:
                limit = int(best_sellers)
                # Order by quantity_sold field
                products = products.order_by('-quantity_sold')[:limit]
            except ValueError:
                pass
            
        # Apply filters
        brand = request.GET.get('brand')
        if brand:
            brand_slugs = brand.split(',')
            products = products.filter(brand__slug__in=brand_slugs)

        color = request.GET.get('color')
        if color:
            color_slugs = color.split(',')
            products = products.filter(colors__slug__in=color_slugs)

        min_price = request.GET.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        
        max_price = request.GET.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)

        # Calculate discount percentage (derived field)
        products = products.annotate(
            discount_percentage=ExpressionWrapper(
                (F('price') - F('sale_price')) / F('price') * 100,
                output_field=FloatField()
            )
        )
        # Filter by minimum discount
        discount = request.GET.get('discount_min')
        if discount:
            products = products.filter(discount_percentage__gte=float(discount))

        # filter by is_featured 
        featured = request.GET.get('is_featured')
        if featured:
            products = products.filter(is_featured=True)   

        # Ordering logic
        ordering = request.GET.get('ordering')
        if ordering == 'popularity':
            products = products.order_by('-quantity_sold')
        elif ordering == 'newest':
            products = products.order_by('-created_at')
        elif ordering == 'price_asc':
            products = products.order_by('price')
        elif ordering == 'price_desc':
            products = products.order_by('-price')
        elif ordering == 'rating':
            products = products.order_by('-rating_average')
        # Default ordering (optional)
        else:
            products = products.order_by('-quantity_sold')

        # Get total count before pagination
        total_count = products.count()
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(paginated_products, many=True)
        
        response_data = {
            'count': total_count,
            'results': serializer.data,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'current_page': paginator.page.number,
            'total_pages': paginator.page.paginator.num_pages,
            'page_size': paginator.page_size
        }
        
        return Response(response_data)
