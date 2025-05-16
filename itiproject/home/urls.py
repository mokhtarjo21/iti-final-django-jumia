
from django.urls import path
from .views import get_hero_sliders, get_banners, get_products, get_categories

urlpatterns = [
    path('hero-sliders/', get_hero_sliders),
    path('banners/', get_banners),
    path('products/', get_products),
    path('categories/', get_categories),

]
