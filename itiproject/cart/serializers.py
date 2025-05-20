

from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product,ProductImage  
from products.serializers import ProductImageSerializer
class ProductSerializer(serializers.ModelSerializer):
    product_images = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'sale_price', 'product_images']
    def get_product_images(self, obj):
        all_images = obj.images.all()
        if all_images:
            return ProductImageSerializer(all_images, many=True).data
        return None
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'colors', 'size']
