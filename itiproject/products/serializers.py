# products/serializers.py
from rest_framework import serializers
from django.utils.text import slugify
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductVariantType, ProductVariantValue, ProductVariant,
    FlashSale, FlashSaleItem
)

# ==================== CATEGORY SERIALIZERS ====================

class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing categories"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'product_count']
    
    def get_product_count(self, obj):
        return obj.products.count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed category view"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children = CategoryListSerializer(many=True, read_only=True, source='children.all')
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'parent_name', 
            'image', 'is_active', 'created_at', 'updated_at',
            'children', 'product_count'
        ]
    
    def get_product_count(self, obj):
        return obj.products.count()


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'parent', 'image', 'is_active']
    
    def create(self, validated_data):
        # Auto-generate slug
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Update slug if name changes
        if 'name' in validated_data and validated_data['name'] != instance.name:
            instance.slug = slugify(validated_data['name'])
        return super().update(instance, validated_data)


# ==================== BRAND SERIALIZERS ====================

class BrandListSerializer(serializers.ModelSerializer):
    """Serializer for listing brands"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'image', 'product_count']
    
    def get_product_count(self, obj):
        return obj.products.count()


class BrandDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed brand view"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'image',
            'created_at', 'updated_at', 'product_count'
        ]
    
    def get_product_count(self, obj):
        return obj.products.count()


class BrandCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating brands"""
    
    class Meta:
        model = Brand
        fields = ['name', 'image']
    
    def create(self, validated_data):
        # Auto-generate slug
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Update slug if name changes
        if 'name' in validated_data and validated_data['name'] != instance.name:
            instance.slug = slugify(validated_data['name'])
        return super().update(instance, validated_data)


# ==================== PRODUCT IMAGE SERIALIZERS ====================

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


# ==================== VARIANT SERIALIZERS ====================

class ProductVariantTypeSerializer(serializers.ModelSerializer):
    """Serializer for variant types"""
    
    class Meta:
        model = ProductVariantType
        fields = ['id', 'name', 'slug', 'order']


class ProductVariantValueSerializer(serializers.ModelSerializer):
    """Serializer for variant values"""
    type_name = serializers.CharField(source='variant_type.name', read_only=True)
    
    class Meta:
        model = ProductVariantValue
        fields = ['id', 'variant_type', 'value', 'slug', 'color_code', 'type_name', 'order']
    
    def create(self, validated_data):
        # Auto-generate slug
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['value'])
        return super().create(validated_data)


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants"""
    variant_values = ProductVariantValueSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'variant_values', 'price', 'compare_price',
            'stock_quantity', 'images', 'is_active', 'display_name'
        ]
    
    def get_display_name(self, obj):
        """Get formatted variant name"""
        values = obj.variant_values.all()
        value_str = ", ".join([f"{v.variant_type.name}: {v.value}" for v in values])
        return value_str


# ==================== PRODUCT SERIALIZERS ====================

class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product listings"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    has_variants = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'price', 'sale_price',
            'category_name', 'brand_name', 'primary_image',
            'rating_average', 'rating_count', 'discount_percentage',
            'stock_quantity', 'is_featured', 'has_variants'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image"""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return ProductImageSerializer(primary).data
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None
    
    def get_discount_percentage(self, obj):
        """Calculate discount percentage"""
        if obj.sale_price and obj.price > obj.sale_price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            return round(discount, 0)
        return None
    
    def get_has_variants(self, obj):
        """Check if product has variants"""
        return obj.variants.exists()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view"""
    category = CategoryListSerializer(read_only=True)
    brand = BrandListSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'category', 'brand',
            'description', 'specifications', 'price', 'sale_price',
            'sale_start_date', 'sale_end_date', 'stock_quantity',
            'track_inventory', 'allow_backorder', 'weight', 'length', 
            'width', 'height', 'is_featured', 'meta_title',
            'meta_description', 'meta_keywords', 'rating_average', 
            'rating_count', 'images', 'variants', 'discount_percentage',
            'created_at', 'updated_at', 'launched_at'
        ]
    
    def get_discount_percentage(self, obj):
        """Calculate discount percentage"""
        if obj.sale_price and obj.price > obj.sale_price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            return round(discount, 0)
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    images_data = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    brand_name = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'brand_name', 'description',
            'specifications', 'price', 'sale_price', 'sale_start_date',
            'sale_end_date', 'stock_quantity', 'track_inventory',
            'allow_backorder', 'weight', 'length', 'width', 'height',
            'is_featured', 'meta_title', 'meta_description', 'meta_keywords',
            'images_data'
        ]
    
    def create(self, validated_data):
        """Create product with images"""
        brand_name = validated_data.pop('brand_name', None)
        brand_id = validated_data.get('brand', None)
        images_data = validated_data.pop('images_data', [])
        
        # If brand_name is provided but brand_id is not, create a new brand
        if brand_name and not brand_id:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': slugify(brand_name)}
            )
            validated_data['brand'] = brand
        
        # Create the product
        product = Product.objects.create(**validated_data)
        
        # Create product images
        for index, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image_data,
                is_primary=(index == 0),  # First image is primary
                order=index
            )
        
        return product
    
    def update(self, instance, validated_data):
        """Update product and associated data"""
        brand_name = validated_data.pop('brand_name', None)
        images_data = validated_data.pop('images_data', None)
        
        # Handle brand creation if needed
        if brand_name and not validated_data.get('brand'):
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': slugify(brand_name)}
            )
            validated_data['brand'] = brand
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle images if provided
        if images_data is not None:
            # Clear existing images
            instance.images.all().delete()
            # Create new images
            for index, image_data in enumerate(images_data):
                ProductImage.objects.create(
                    product=instance,
                    image=image_data,
                    is_primary=(index == 0),  # First image is primary
                    order=index
                )
        
        return instance


# ==================== FLASH SALE SERIALIZERS ====================

class FlashSaleItemSerializer(serializers.ModelSerializer):
    """Serializer for flash sale items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = FlashSaleItem
        fields = [
            'id', 'product', 'product_name', 'product_image',
            'discount_percentage', 'quantity_limit', 'quantity_sold'
        ]
    
    def get_product_image(self, obj):
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class FlashSaleListSerializer(serializers.ModelSerializer):
    """Serializer for listing flash sales"""
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FlashSale
        fields = [
            'id', 'name', 'slug', 'start_time', 'end_time',
            'is_active', 'created_at', 'item_count'
        ]
    
    def get_item_count(self, obj):
        return obj.items.count()


class FlashSaleDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed flash sale view"""
    items = FlashSaleItemSerializer(many=True, read_only=True, source='items.all')
    
    class Meta:
        model = FlashSale
        fields = [
            'id', 'name', 'slug', 'description', 'start_time', 
            'end_time', 'is_active', 'created_at', 'items'
        ]


class FlashSaleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating flash sales"""
    
    class Meta:
        model = FlashSale
        fields = ['name', 'description', 'start_time', 'end_time', 'is_active']
    
    def create(self, validated_data):
        # Auto-generate slug
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class FlashSaleItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating flash sale items"""
    
    class Meta:
        model = FlashSaleItem
        fields = ['flash_sale', 'product', 'discount_percentage', 'quantity_limit']