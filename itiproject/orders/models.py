from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from users.models import Vendor
from django.utils import timezone

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('paymob', 'Paymob'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders')
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_completed = models.BooleanField(default=False)
    paymob_order_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name='vendor_orders')  ####


    def __str__(self):
        return f"Order #{self.id} by {self.user.email if self.user else 'Unknown'}"

    def check_status(self):
        if all(item.status == 'accepted' for item in self.items.all()):
            self.status = 'processing'
            self.save()


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    order = models.ForeignKey(Order, related_name='items', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.product.name if self.product else 'Deleted product'} - Order #{self.order.id if self.order else 'N/A'}"
