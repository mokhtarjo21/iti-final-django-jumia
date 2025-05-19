
from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea, TextInput, Select
from .models import (
    Category, Brand, Product, ProductImage, 
    Size, Color, FlashSale, FlashSaleItem
)

# ==================== INLINES ====================

class CategoryInline(admin.TabularInline):
    model = Category
    fields = ['name', 'is_active', 'image']
    extra = 0
    show_change_link = True

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ['image', 'alt_text', 'is_primary', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    extra = 1
    show_change_link = True
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "-"

class FlashSaleItemInline(admin.TabularInline):
    model = FlashSaleItem
    fields = ['product', 'discount_percentage', 'quantity_limit', 'quantity_sold']
    extra = 1
    show_change_link = True
    autocomplete_fields = ['product']

# ==================== MODEL ADMINS ====================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'product_count', 'display_image']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryInline]
    readonly_fields = ['display_image', 'created_at', 'updated_at']
    autocomplete_fields = ['parent']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'parent', 'is_active')
        }),
        ('Image', {
            'fields': ('image', 'display_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "-"
    display_image.short_description = 'Image Preview'
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'display_image']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['display_image', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug')
        }),
        ('Image', {
            'fields': ('image', 'display_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "-"
    display_image.short_description = 'Logo Preview'

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count']
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Used in Products'

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'product_count']
    search_fields = ['name']
    
    def color_preview(self, obj):
        return format_html('<div style="background-color: {}; width: 30px; height: 30px; border: 1px solid #000;"></div>', obj.name)
    color_preview.short_description = 'Color'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Used in Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'brand', 'price', 
        'sale_price', 'stock_status', 'is_featured', 'is_sponsored', 
        'rating_average', 'rating_count' ,'display_image'
    ]
    list_filter = [
        'category', 'brand', 'sizes', 'colors', 'is_featured', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'rating_average', 'rating_count', 'display_image']
    inlines = [ProductImageInline]
    filter_horizontal = ['sizes', 'colors']
    autocomplete_fields = ['category', 'brand']
    save_on_top = True
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Categorization', {
            'fields': ('category', 'brand')
        }),
        ('Product Options', {
            'fields': ('sizes', 'colors', 'material')
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
            'fields': ('is_featured',),
            'fields': ('is_sponsored',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('rating_average', 'rating_count', 'created_at', 'updated_at', 'launched_at'),
            'classes': ('collapse',)
        }),
        ('Preview', {
            'fields': ('display_image',)
        })
    )
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60})},
        models.JSONField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60})},
    }
    
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
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', primary.image.url)
        first_image = obj.images.first()
        if first_image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', first_image.image.url)
        return "-"
    display_image.short_description = 'Image Preview'
    
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
    autocomplete_fields = ['product']
    readonly_fields = ['display_image']
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 150px; max-width: 150px;" />', obj.image.url)
        return "-"
    display_image.short_description = 'Image Preview'

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_active', 'item_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [FlashSaleItemInline]
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

@admin.register(FlashSaleItem)
class FlashSaleItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'flash_sale', 'discount_percentage', 'quantity_limit', 'quantity_sold']
    list_filter = ['flash_sale']
    search_fields = ['product__name', 'flash_sale__name']
    autocomplete_fields = ['product', 'flash_sale']