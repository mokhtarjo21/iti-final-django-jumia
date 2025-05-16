from django.db import models
from django.conf import settings
# from products.models import Product  # wait for real version

#  Temporary placeholder to avoid error
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False  # prevents Django from trying to create a DB table
        app_label = 'products'  # keeps naming consistent

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
