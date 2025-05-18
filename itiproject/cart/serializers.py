from rest_framework import serializers
from .models import CartItem
from products.serializers import ProductListSerializer as ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # ✅ return full product info

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'description', 'color', 'size']
