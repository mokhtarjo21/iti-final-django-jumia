from django.urls import path
from .views import (
    CategoryProductsView, CategoryTreeView, CategoryDetailView, CategoryDetailBySlugView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView,
)

urlpatterns = [
    # Category endpoints
    # get products of certain category e.g.: localhost:8000/api/category/electronics/
    path('category/<slug:slug>/products/', CategoryProductsView.as_view(), name='category-products'),
    # get category tree for displaying in home page
    path('category/tree/', CategoryTreeView.as_view(), name='category-tree'),
    # get certain category detail by slug or id
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail-pk'),
    path('category/<slug:slug>/', CategoryDetailBySlugView.as_view(), name='category-detail-slug'),
    # post to create, update or delete category by admin
    path('category/create/', CategoryCreateView.as_view(), name='category-create'),
    path('category/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),

    # Product endpoints
    # get product detail by id
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
    # post to create product by admin
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    # put to update product by admin
    path('products/<uuid:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<uuid:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

]