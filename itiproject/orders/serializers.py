from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from users.models import Vendor,User


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'shopName']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'vendor', 'status']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'shipping_address',
            'total_price',
            'payment_method',
            'payment_completed',
            'paymob_order_id',
            'items',
        ]
        read_only_fields = ['user', 'payment_completed', 'items']



from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'first_name', 'last_name', 'email', 'phone']
class VendorOrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    customer_name = serializers.CharField(source='order.user.first_name', read_only=True)
    shipping_address = serializers.CharField(source='order.shipping_address', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    payment_method = serializers.CharField(source='order.payment_method', read_only=True)
    created_at = serializers.DateTimeField(source='order.created_at', read_only=True)
    customer = CustomerSerializer(source='order.user', read_only=True)
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order_id',
            'customer_name',
            'customer',
            'shipping_address',
            'product_name',
            'product_price',
            'quantity',
            'status',
            'payment_method',
            'created_at',
        ]