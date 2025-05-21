from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from users.models import Vendor


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


class VendorOrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    customer_email = serializers.EmailField(source='order.user.email', read_only=True)
    shipping_address = serializers.CharField(source='order.shipping_address', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order_id',
            'customer_email',
            'shipping_address',
            'product_name',
            'product_price',
            'quantity',
            'status',
        ]
