from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductVariantType, ProductVariantValue, ProductVariant,
    FlashSale, FlashSaleItem
)

# ==================== INLINES ====================

class CategoryInline(admin.TabularInline):
    model = Category
    fields = ['name', 'is_active']
    extra = 0
    show_change_link = True

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ['image', 'alt_text', 'is_primary', 'order']
    extra = 1
    show_change_link = True

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    fields = ['sku', 'price', 'stock_quantity', 'is_active']
    extra = 0
    show_change_link = True

class FlashSaleItemInline(admin.TabularInline):
    model = FlashSaleItem
    fields = ['product', 'discount_percentage', 'quantity_limit']
    extra = 1
    show_change_link = True

# ==================== MODEL ADMINS ====================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'product_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryInline]
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'display_image']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    display_image.short_description = 'Logo'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'brand', 'price', 
        'sale_price', 'stock_status', 'is_featured', 'display_image'
    ]
    list_filter = [
        'category', 'brand', 'is_featured', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'rating_average', 'rating_count']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Categorization', {
            'fields': ('category', 'brand')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price', 'sale_start_date', 'sale_end_date')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'track_inventory', 'allow_backorder')
        }),
        ('Shipping', {
            'fields': ('weight', 'length', 'width', 'height')
        }),
        ('Specifications', {
            'fields': ('specifications',)
        }),
        ('Status', {
            'fields': ('is_featured',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('rating_average', 'rating_count', 'created_at', 'updated_at', 'launched_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        if obj.track_inventory:
            if obj.stock_quantity > 0:
                return format_html('<span style="color: green;">In Stock ({0})</span>', obj.stock_quantity)
            elif obj.allow_backorder:
                return format_html('<span style="color: orange;">Backorder</span>')
            else:
                return format_html('<span style="color: red;">Out of Stock</span>')
        return format_html('<span style="color: blue;">Not Tracked</span>')
    stock_status.short_description = 'Stock'
    
    def display_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return format_html('<img src="{}" width="50" height="50" />', primary.image.url)
        first_image = obj.images.first()
        if first_image:
            return format_html('<img src="{}" width="50" height="50" />', first_image.image.url)
        return "-"
    display_image.short_description = 'Image'
    
    # For bulk actions
    actions = ['mark_featured', 'mark_not_featured']
    
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_featured.short_description = "Mark selected products as featured"
    
    def mark_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
    mark_not_featured.short_description = "Mark selected products as not featured"

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'display_image', 'is_primary', 'order']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    display_image.short_description = 'Image'

@admin.register(ProductVariantType)
class ProductVariantTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductVariantValue)
class ProductVariantValueAdmin(admin.ModelAdmin):
    list_display = ['value', 'variant_type', 'color_display', 'order']
    list_filter = ['variant_type']
    search_fields = ['value', 'variant_type__name']
    
    def color_display(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="background-color: {}; width: 20px; height: 20px; border: 1px solid #000;"></div>',
                obj.color_code
            )
        return "-"
    color_display.short_description = 'Color'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price', 'stock_quantity', 'is_active']
    list_filter = ['is_active']
    search_fields = ['product__name', 'sku']
    filter_horizontal = ['variant_values', 'images']

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_active', 'item_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [FlashSaleItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

@admin.register(FlashSaleItem)
class FlashSaleItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'flash_sale', 'discount_percentage', 'quantity_limit', 'quantity_sold']
    list_filter = ['flash_sale']
    search_fields = ['product__name', 'flash_sale__name']