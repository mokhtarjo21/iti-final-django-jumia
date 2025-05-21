from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from users.models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'shopName']  # Add more if needed


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']  # You can expand this as needed


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
