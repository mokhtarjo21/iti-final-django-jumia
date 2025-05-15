from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models import Avg
import uuid
from django.core.exceptions import ValidationError

User = get_user_model()

class Category(models.Model):
    """Product categories with hierarchical structure"""
    name = models.CharField(max_length=200)

    slug = models.SlugField(unique=True, max_length=200)
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='children'
    )

    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    class Meta:
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate that a category doesn't reference itself as parent"""
        # Check direct self-reference
        if self.parent == self:
            raise ValidationError(_("A category cannot be its own parent."))
        
        # Check indirect circular reference
        if self.pk:  # Only check for existing categories
            parent = self.parent
            while parent is not None:
                if parent.pk == self.pk:
                    raise ValidationError(_("Circular reference detected in category hierarchy."))
                parent = parent.parent

    def save(self, *args, **kwargs):
        """Ensure validation runs when saving"""
        self.clean()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """Product brands"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='brand_images/', blank=True, null=True)
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class Size(models.Model):
    SIZE_CHOICES = [
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
        ("XXXL", "XXXL"),
    ]
    name = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    COLOR_CHOICES = [
        ("Red", "Red"),
        ("Blue", "Blue"),
        ("Green", "Green"),
        ("Black", "Black"),
        ("White", "White"),
        ("Yellow", "Yellow"),
        ("Orange", "Orange"),
        ("Purple", "Purple"),
        ("Gray", "Gray"),
        ("Brown", "Brown"),
    ]
    name = models.CharField(max_length=20, choices=COLOR_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Main product model"""
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # vendor = models.ForeignKey(
    #     'vendors.Vendor', 
    #     on_delete=models.CASCADE,
    #     related_name='products'
    # )
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=500)

    slug = models.SlugField(max_length=500, unique=True)
    
    # Categorization
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='products'
    )
    
    # Descriptions
    description = models.TextField()

    # Specifications
    specifications = models.JSONField(default=dict, blank=True)

    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Global/standard price")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_start_date = models.DateTimeField(null=True, blank=True)
    sale_end_date = models.DateTimeField(null=True, blank=True)
    
    # Inventory
    stock_quantity = models.IntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)
    
    # Shipping
    weight = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        null=True, 
        blank=True,
        help_text="Weight in KG"
    )
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status flags
    is_featured = models.BooleanField(default=False)

    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    launched_at = models.DateTimeField(null=True, blank=True)
    
    # Ratings cache (for performance)
    rating_average = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    rating_count = models.IntegerField(default=0)
    
    # New fields
    sizes = models.ManyToManyField(Size, blank=True, related_name='products')
    colors = models.ManyToManyField(Color, blank=True, related_name='products')
    material = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            # models.Index(fields=['vendor']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)

    # def update_rating(self):
    #     """Update cached rating from reviews"""
    #     from reviews.models import Review
    #     result = Review.objects.filter(
    #         product=self,
    #         is_approved=True
    #     ).aggregate(
    #         avg_rating=Avg('rating'),
    #         count=models.Count('id')
    #     )
    #     self.rating_average = result['avg_rating'] or 0
    #     self.rating_count = result['count'] or 0
    #     self.save(update_fields=['rating_average', 'rating_count'])


class ProductImage(models.Model):
    """Product images"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)



class FlashSale(models.Model):
    """Flash sales / time-limited deals"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time', 'is_active']),
        ]

    def __str__(self):
        return self.name


class FlashSaleItem(models.Model):
    """Products in flash sales"""
    flash_sale = models.ForeignKey(
        FlashSale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='flash_sales'
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    quantity_limit = models.IntegerField(default=0, help_text="0 for unlimited")
    quantity_sold = models.IntegerField(default=0)
    
    class Meta:
        unique_together = [['flash_sale', 'product']]

    def __str__(self):
        return f"{self.product.name} - {self.discount_percentage}% off"