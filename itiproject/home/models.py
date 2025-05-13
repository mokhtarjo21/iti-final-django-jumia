from django.db import models

# Create your models here.
from django.db import models

class HeroSlider(models.Model):
    image = models.ImageField(upload_to="hero/")
    link = models.URLField()

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="categories/")

class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="banners/")
    link = models.URLField()

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_flash_sale = models.BooleanField(default=False)
    is_top_product = models.BooleanField(default=False)
