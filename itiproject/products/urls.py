from django.urls import path
from .views import (
    CategoryProductsView, CategoryTreeView, CategoryDetailView, CategoryDetailBySlugView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView,
)

urlpatterns = [
    # Category endpoints
    path('category/<slug:slug>/products', CategoryProductsView.as_view(), name='category-products'),
    path('category/tree/', CategoryTreeView.as_view(), name='category-tree'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail-pk'),
    path('category/<slug:slug>/', CategoryDetailBySlugView.as_view(), name='category-detail-slug'),
    path('category/create/', CategoryCreateView.as_view(), name='category-create'),
    path('category/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),

    # Product endpoints
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<uuid:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<uuid:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

]