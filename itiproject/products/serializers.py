# products/serializers.py
from rest_framework import serializers
from django.utils.text import slugify
from .models import (
    Category, Brand, Product, ProductImage, Size, Color,
    FlashSale, FlashSaleItem, RecentlyViewedProduct
)
# ==================== CATEGORY SERIALIZERS ====================

class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing categories"""
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'product_count', 'description', 'children']
    
    def get_children(self, obj):
        # Get all direct children of this category
        children = obj.children.all()
        # Recursively serialize children
        return CategoryListSerializer(children, many=True).data
    
    def get_product_count(self, obj):
        # Get all descendant categories (including the current category)
        def get_descendant_categories(category):
            descendants = [category]
            for child in category.children.all():
                descendants.extend(get_descendant_categories(child))
            return descendants
        
        # Get all categories in the hierarchy
        all_categories = get_descendant_categories(obj)
        
        # Count products across all categories
        return Product.objects.filter(category__in=all_categories).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed category view"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    parent_slug = serializers.CharField(source='parent.slug', read_only=True)
    children = CategoryListSerializer(many=True, read_only=True, source='children.all')
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'parent_name', 'parent_slug', 
            'image', 'is_active', 'created_at', 'updated_at', 
            'description', 'children', 'product_count'
        ]
    
    def get_product_count(self, obj):
        # Get all descendant categories (including the current category)
        def get_descendant_categories(category):
            descendants = [category]
            for child in category.children.all():
                descendants.extend(get_descendant_categories(child))
            return descendants
        
        # Get all categories in the hierarchy
        all_categories = get_descendant_categories(obj)
        
        # Count products across all categories
        return Product.objects.filter(category__in=all_categories).count()


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating categories"""
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Category
        fields = ['name', 'parent', 'image', 'is_active', 'description']
    
    def validate_parent(self, value):
        """Validate parent category"""
        if value:
            # Check if trying to set parent to self
            if self.instance and value.id == self.instance.id:
                raise serializers.ValidationError("A category cannot be its own parent.")
            
            # Check for circular references
            if self.instance:
                parent = value
                while parent is not None:
                    if parent.id == self.instance.id:
                        raise serializers.ValidationError("Circular reference detected in category hierarchy.")
                    parent = parent.parent
        return value
    
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


# ==================== PRODUCT SERIALIZERS ====================

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    product_images = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    sizes = SizeSerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    material = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'price', 'sale_price', 'seller',
            'category_name', 'category_slug', 'brand_name', 'product_images',
            'rating_average', 'rating_count', 'discount_percentage',
            'stock_quantity', 'quantity_sold', 'is_featured', 'is_sponsored', 'sizes', 'colors', 'material',
            'description', 'specifications', 'updated_at'
        ]

    def get_product_images(self, obj):
        all_images = obj.images.all()
        if all_images:
            return ProductImageSerializer(all_images, many=True).data
        return None

    def get_discount_percentage(self, obj):
        if obj.sale_price and obj.price > obj.sale_price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            return round(discount, 0)
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    brand = BrandListSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    material = serializers.CharField(read_only=True)
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'category', 'brand', 'seller',
            'description', 'specifications', 'price', 'sale_price',
            'sale_start_date', 'sale_end_date', 'stock_quantity',
            'track_inventory', 'allow_backorder', 'weight', 'length', 
            'width', 'height', 'is_featured', 'meta_title',
            'meta_description', 'meta_keywords', 'rating_average', 
            'rating_count', 'images', 'sizes', 'colors', 'material', 'discount_percentage',
            'created_at', 'updated_at', 'launched_at'
        ]

    def get_discount_percentage(self, obj):
        if obj.sale_price and obj.price > obj.sale_price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            return round(discount, 0)
        return None

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    images_data = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    brand_name = serializers.CharField(required=False, write_only=True)
    sizes = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), many=True, required=False)
    colors = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), many=True, required=False)
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    sku = serializers.CharField(required=True)
    material = serializers.CharField(required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'brand_name', 'description',
            'specifications', 'price', 'sale_price', 'sale_start_date',
            'sale_end_date', 'stock_quantity', 'track_inventory',
            'allow_backorder', 'weight', 'length', 'width', 'height',
            'is_featured', 'meta_title', 'meta_description', 'meta_keywords',
            'images_data', 'sizes', 'colors', 'material', 'seller', 'sku'
        ]

    def validate(self, data):
        # Validate sale price
        if data.get('sale_price') and data.get('sale_price') >= data.get('price', 0):
            raise serializers.ValidationError("Sale price must be less than original price.")
        
        # Validate sale dates
        sale_start = data.get('sale_start_date')
        sale_end = data.get('sale_end_date')
        if sale_start and sale_end and sale_start >= sale_end:
            raise serializers.ValidationError("Sale start date must be before sale end date.")
        
        # Validate SKU uniqueness
        sku = data.get('sku')
        if sku:
            if self.instance:  # Update case
                if Product.objects.filter(sku=sku).exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError("A product with this SKU already exists.")
            else:  # Create case
                if Product.objects.filter(sku=sku).exists():
                    raise serializers.ValidationError("A product with this SKU already exists.")
        
        return data

    def create(self, validated_data):
        brand_name = validated_data.pop('brand_name', None)
        brand_id = validated_data.pop('brand', None)
        images_data = validated_data.pop('images_data', [])
        sizes = validated_data.pop('sizes', [])
        colors = validated_data.pop('colors', [])

        if brand_name and not brand_id:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': slugify(brand_name)}
            )
            validated_data['brand'] = brand

        # Set the seller to the current user
        validated_data['seller'] = self.context['request'].user

        # Generate slug if not provided
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(f"{validated_data['name']}-{validated_data['sku']}")

        product = Product.objects.create(**validated_data)
        if sizes:
            product.sizes.set(sizes)
        if colors:
            product.colors.set(colors)

        for index, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image_data,
                is_primary=(index == 0),
                order=index
            )
        return product

    def update(self, instance, validated_data):
        brand_name = validated_data.pop('brand_name', None)
        images_data = validated_data.pop('images_data', None)
        sizes = validated_data.pop('sizes', None)
        colors = validated_data.pop('colors', None)

        if brand_name and not validated_data.get('brand'):
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': slugify(brand_name)}
            )
            validated_data['brand'] = brand

        # Ensure seller cannot be changed during update
        if 'seller' in validated_data:
            validated_data.pop('seller')

        # Update slug if name or SKU changes
        if ('name' in validated_data or 'sku' in validated_data) and not validated_data.get('slug'):
            name = validated_data.get('name', instance.name)
            sku = validated_data.get('sku', instance.sku)
            validated_data['slug'] = slugify(f"{name}-{sku}")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if sizes is not None:
            instance.sizes.set(sizes)
        if colors is not None:
            instance.colors.set(colors)

        if images_data is not None:
            instance.images.all().delete()
            for index, image_data in enumerate(images_data):
                ProductImage.objects.create(
                    product=instance,
                    image=image_data,
                    is_primary=(index == 0),
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


# ==================== RECENTLY VIEWED PRODUCTS SERIALIZER ====================

class RecentlyViewedProductSerializer(serializers.ModelSerializer):
    """Serializer for recently viewed products"""
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = RecentlyViewedProduct
        fields = ['id', 'product', 'viewed_at']