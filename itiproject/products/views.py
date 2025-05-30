from django.shortcuts import render
from django.db.models import Q, F, ExpressionWrapper, FloatField, Min, Max
from itertools import chain
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product, Brand, Color, Size
from .serializers import (
    ProductListSerializer, CategoryListSerializer, CategoryDetailSerializer, CategoryCreateUpdateSerializer,
    ProductCreateUpdateSerializer, ProductImageSerializer, SizeSerializer, ColorSerializer, BrandListSerializer)
from rest_framework import generics
from rest_framework import status
# modules to handle auth
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F, ExpressionWrapper, FloatField, Min, Max, Sum
from users.models import User
# Add caching imports
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
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
                color_slugs = color.split(',')
                products = products.filter(colors__slug__in=color_slugs)

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

            # Filter by minimum rating stars unless sponsored is present
            min_stars = request.GET.get('min_stars')
            if min_stars:
                try:
                    min_stars_value = float(min_stars)
                    products = products.filter(Q(rating_average__gte=min_stars_value) | Q(is_sponsored=True))
                except ValueError:
                    pass

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

            # Get all unique colors for this category and its subcategories
            category_colors = products.values('colors__name', 'colors__slug').distinct()
            colors_list = [
                {'name': c['colors__name'], 'slug': c['colors__slug']}
                for c in category_colors if c['colors__name'] and c['colors__slug']
            ]

            # Get the minimum and maximum price for the filtered products
            price_range = products.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            )

            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 12 # You can adjust this or make it configurable
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
                'colors': colors_list,
                'min_price': price_range['min_price'],
                'max_price': price_range['max_price'],
                'pagination': pagination_data
            }

            return Response(response_data)

        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

# List all categories as a tree
@method_decorator(cache_page(60 * 10), name='get')  # Cache for 15 minutes
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


class SearchSuggestionsView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()


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
            } for p in products],
            
            'categories': [{
                'id': c['id'],
                'name': c['name'],
                'slug': c['slug'],
                'type': 'category',
            } for c in categories],
            
            'brands': [{
                'id': b['id'],
                'name': b['name'],
                'slug': b['slug'],
                'image': b['image'],
                'type': 'brand',
            } for b in brands]
        }

        return Response(suggestions)

# converted product search into a general view for listing, searching, and filtering by recentlyadded, sponsered
# , brand-slug, minprice, highprice and color in products
@method_decorator(cache_page(60 * 5), name='get')  # Cache for 5 minutes
@method_decorator(vary_on_headers("Authorization"), name='get')
@method_decorator(vary_on_cookie, name='get')
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

        # Filter by minimum discount percentage
        discount = request.GET.get('discount_min')
        if discount:
            products = products.filter(discount_percentage__gte=float(discount))

        # Filter for products with discounts only
        has_discount = request.GET.get('has_discount')
        if has_discount:
            products = products.filter(sale_price__isnull=False, sale_price__lt=F('price'))

        # filter by is_featured 
        featured = request.GET.get('is_featured')
        if featured:
            products = products.filter(is_featured=True)   

        # Filter by minimum rating stars unless sponsored is present
        min_stars = request.GET.get('min_stars')
        if min_stars:
            try:
                min_stars_value = float(min_stars)
                products = products.filter(Q(rating_average__gte=min_stars_value) | Q(is_sponsored=True))
            except ValueError:
                pass

        # Filter sponsored products
        sponsored = request.GET.get('sponsored')
        if sponsored:
            products = products.filter(is_sponsored=True)

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

        # Get all unique colors for the filtered products
        category_colors = products.values('colors__name', 'colors__slug').distinct()
        colors_list = [
            {'name': c['colors__name'], 'slug': c['colors__slug']}
            for c in category_colors if c['colors__name'] and c['colors__slug']
        ]

        # Get the minimum and maximum price for the filtered products
        price_range = products.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )

        # Handle best_sellers and recent products after all filters
        best_sellers = request.GET.get('best_sellers')
        if best_sellers:
            try:
                limit = int(best_sellers)
                products = products.order_by('-quantity_sold')[:limit]
                total_count = products.count()
                serializer = ProductListSerializer(products, many=True)
                pagination_data = {
                    'count': total_count,
                    'next': None,
                    'previous': None,
                    'current_page': 1,
                    'total_pages': 1,
                }
            except ValueError:
                pass
        else:
            # Get recently added products
            recent = request.GET.get('recent')
            if recent:
                try:
                    limit = int(recent)
                    products = products.order_by('-created_at')[:limit]
                except ValueError:
                    pass

            total_count = products.count()
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 12
            paginated_products = paginator.paginate_queryset(products, request)
            serializer = ProductListSerializer(paginated_products, many=True)
            pagination_data = {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'total_pages': paginator.page.paginator.num_pages,
            }
        
        response_data = {
            'products_count': total_count,
            'products': serializer.data,
            'colors': colors_list,
            'min_price': price_range['min_price'],
            'max_price': price_range['max_price'],
            'pagination': pagination_data
        }
        
        return Response(response_data)

class VendorProductsView(APIView):
    """
    API endpoint to list products for the currently logged-in vendor (staff user)
    """
    permission_classes = [IsAuthenticated]  # Ensures only authenticated staff users can access
    
    def get(self, request):
        # Get products for the current vendor
        products = Product.objects.filter(seller=request.user)
        
        # Apply filters if provided
        search_query = request.GET.get('q', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )
        
        # Filter by category
        category = request.GET.get('category')
        if category:
            products = products.filter(category__slug=category)
        
        # Filter by brand
        brand = request.GET.get('brand')
        if brand:
            products = products.filter(brand__slug=brand)
        
        # Filter by price range
        min_price = request.GET.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        
        max_price = request.GET.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Filter by stock status
        in_stock = request.GET.get('in_stock')
        if in_stock:
            products = products.filter(stock_quantity__gt=0)
        
        # Calculate discount percentage
        products = products.annotate(
            discount_percentage=ExpressionWrapper(
                (F('price') - F('sale_price')) / F('price') * 100,
                output_field=FloatField()
            )
        )
        
        # Filter by discount
        discount = request.GET.get('discount_min')
        if discount:
            products = products.filter(discount_percentage__gte=float(discount))
        
        # Ordering
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
            products = products.order_by('-created_at')  # Default ordering
        
        # Get price range for filtered products
        price_range = products.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 12
        paginated_products = paginator.paginate_queryset(products, request)
        
        # Serialize the data
        serializer = ProductListSerializer(paginated_products, many=True)
        
        # Prepare pagination data
        pagination_data = {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'current_page': paginator.page.number,
            'total_pages': paginator.page.paginator.num_pages,
        }
        
        # Prepare response data
        response_data = {
            'results': serializer.data,
            'min_price': price_range['min_price'],
            'max_price': price_range['max_price'],
            'pagination': pagination_data,
            'total_products': products.count(),
            'total_revenue': products.aggregate(
                total=Sum(F('price') * F('quantity_sold'))
            )['total'] or 0
        }
        
        return Response(response_data)


class getsizecolor(APIView):
    def get(self, request):
        colors = Color.objects.all()
        sizes = Size.objects.all()
        categories = Category.objects.all()
        brands = Brand.objects.all()
        print('colors')
        return Response({
            'colors': ColorSerializer(colors, many=True).data,
            'sizes': SizeSerializer(sizes, many=True).data,
            'categories': CategoryListSerializer(categories, many=True).data,
            'brands': BrandListSerializer(brands, many=True).data
        })
class updateProduct(APIView):
    def put(self, request, id):
        try:
            user = request.user
            product = Product.objects.get(id=id, seller=user)

           
            product.name = request.data.get('name', product.name)
            product.price = request.data.get('price', product.price)
            product.sale_price = request.data.get('sale_price', product.sale_price)
            product.stock_quantity = request.data.get('stock_quantity', product.stock_quantity)

            product.save()
          
            return Response({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "sale_price": product.sale_price,
                "stock_quantity": product.stock_quantity,
                "sku":product.sku,
                "category_name":product.category.name,
                "rating_average":product.rating_average,
                "message": "Product updated successfully"
            }, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({"error": "Product not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
