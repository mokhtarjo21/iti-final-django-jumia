from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import HeroSlider ,Category, Banner, Product

admin.site.register(HeroSlider)
admin.site.register(Category)
admin.site.register(Banner)
admin.site.register(Product)
