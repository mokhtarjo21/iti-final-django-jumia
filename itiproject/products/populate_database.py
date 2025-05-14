# products/populate_database.py
import os
import django
import random
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itiproject.settings')
django.setup()

# Import models after Django setup
from products.models import Category, Brand, Product, ProductImage, Size, Color

class DatabasePopulator:
    """Class to populate the database with product data"""
    
    def run(self):
        print('Seeding data...')
        
        # Create categories
        self.create_categories()
        
        # Create brands
        self.create_brands()
        
        # Create variant types and values
        self.create_variant_types()
        
        # Create products with variants
        self.create_products()
        
        print('Successfully seeded database!')
    
    def create_categories(self):
        # Main categories
        main_categories = [
            {"name": "Electronics", "children": ["Smartphones", "Laptops", "Audio", "Cameras"]},
            {"name": "Fashion", "children": ["Men's Clothing", "Women's Clothing", "Shoes", "Accessories"]},
            {"name": "Home & Kitchen", "children": ["Furniture", "Appliances", "Kitchenware", "Decor"]},
            {"name": "Beauty", "children": ["Skincare", "Makeup", "Haircare", "Fragrances"]}
        ]
        
        for main in main_categories:
            parent, created = Category.objects.get_or_create(
                name=main["name"],
                defaults={"slug": slugify(main["name"])}
            )
            print(f"{'Created' if created else 'Found'} category: {parent.name}")
            
            # Create child categories
            for child_name in main["children"]:
                child, created = Category.objects.get_or_create(
                    name=child_name,
                    parent=parent,
                    defaults={"slug": slugify(child_name)}
                )
                print(f"  {'Created' if created else 'Found'} subcategory: {child.name}")
    
    def create_brands(self):
        brands = ["Apple", "Samsung", "Nike", "Adidas", "LG", "Sony", "Philips", "Dell", "HP", "Bosch"]
        
        for brand_name in brands:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={"slug": slugify(brand_name)}
            )
            print(f"{'Created' if created else 'Found'} brand: {brand.name}")
    
    def create_variant_types(self):
        # Create variant types
        color_type, _ = ProductVariantType.objects.get_or_create(
            name="Color", 
            defaults={"slug": "color", "order": 1}
        )
        
        size_type, _ = ProductVariantType.objects.get_or_create(
            name="Size", 
            defaults={"slug": "size", "order": 2}
        )
        
        # Create variant values
        colors = [
            {"name": "Red", "code": "#FF0000"},
            {"name": "Blue", "code": "#0000FF"},
            {"name": "Green", "code": "#00FF00"},
            {"name": "Black", "code": "#000000"},
            {"name": "White", "code": "#FFFFFF"}
        ]
        
        for color in colors:
            ProductVariantValue.objects.get_or_create(
                variant_type=color_type,
                value=color["name"],
                defaults={
                    "slug": slugify(color["name"]),
                    "color_code": color["code"],
                    "order": colors.index(color) + 1
                }
            )
        
        sizes = ["S", "M", "L", "XL", "XXL"]
        for size in sizes:
            ProductVariantValue.objects.get_or_create(
                variant_type=size_type,
                value=size,
                defaults={
                    "slug": slugify(size),
                    "order": sizes.index(size) + 1
                }
            )
    
    def create_products(self):
        # Get all categories, brands, and variant values
        categories = list(Category.objects.filter(parent__isnull=False))  # Only subcategories
        brands = list(Brand.objects.all())
        colors = list(ProductVariantValue.objects.filter(variant_type__name="Color"))
        sizes = list(ProductVariantValue.objects.filter(variant_type__name="Size"))
        
        # Sample product data
        products = [
            {
                "name": "Premium Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation.",
                "category_name": "Audio",
                "brand_name": "Sony",
                "price": 199.99,
                "has_variants": True,
                "variant_type": "Color"
            },
            {
                "name": "Ultra HD Smart TV",
                "description": "65-inch 4K Ultra HD Smart TV with HDR.",
                "category_name": "Electronics",
                "brand_name": "Samsung",
                "price": 899.99,
                "has_variants": False
            },
            {
                "name": "Men's Running Shoes",
                "description": "Lightweight running shoes with cushioned soles.",
                "category_name": "Shoes",
                "brand_name": "Nike",
                "price": 89.99,
                "has_variants": True,
                "variant_type": "Size"
            },
            {
                "name": "Smartphone Pro Max",
                "description": "Latest smartphone with advanced camera system and all-day battery life.",
                "category_name": "Smartphones",
                "brand_name": "Apple",
                "price": 1099.99,
                "has_variants": True,
                "variant_type": "Color"
            },
            {
                "name": "Gaming Laptop",
                "description": "Powerful gaming laptop with high-refresh display and RGB keyboard.",
                "category_name": "Laptops",
                "brand_name": "Dell",
                "price": 1299.99,
                "has_variants": False
            }
        ]
        
        for product_data in products:
            # Find the right category and brand
            try:
                category = next((c for c in categories if c.name == product_data["category_name"]), None)
                if not category:
                    # Try to find the category as a parent category
                    parent_category = Category.objects.filter(name=product_data["category_name"]).first()
                    if parent_category:
                        # Use the first child of this parent
                        category = Category.objects.filter(parent=parent_category).first()
                    else:
                        # If still not found, use a random category
                        category = random.choice(categories)
            except Exception:
                # If any error, use a random category
                category = random.choice(categories)
            
            try:
                brand = next((b for b in brands if b.name == product_data["brand_name"]), None)
                if not brand:
                    # If not found, use a random brand
                    brand = random.choice(brands)
            except Exception:
                # If any error, use a random brand
                brand = random.choice(brands)
            
            # Create base product
            sku = f"{brand.name[:3].upper()}-{product_data['name'][:3].upper()}-{random.randint(1000, 9999)}"
            
            # Check if product with this name already exists
            existing_product = Product.objects.filter(name=product_data["name"]).first()
            if existing_product:
                print(f"Product already exists: {product_data['name']}")
                product = existing_product
            else:
                try:
                    product = Product.objects.create(
                        name=product_data["name"],
                        slug=slugify(product_data["name"]),
                        sku=sku,
                        category=category,
                        brand=brand,
                        description=product_data["description"],
                        price=product_data["price"],
                        sale_price=product_data["price"] * 0.9 if random.choice([True, False]) else None,
                        sale_start_date=timezone.now() if random.choice([True, False]) else None,
                        sale_end_date=timezone.now() + timedelta(days=30) if random.choice([True, False]) else None,
                        stock_quantity=random.randint(10, 100),
                        is_featured=random.choice([True, False]),
                        specifications={"features": ["Feature 1", "Feature 2", "Feature 3"]}
                    )
                    print(f"Created product: {product.name}")
                    
                    # Create a product image
                    # Note: In a real scenario, you'd upload actual images
                    # This is just a placeholder for the database structure
                    ProductImage.objects.create(
                        product=product,
                        image="products/default.jpg",  # You'll need a default image in your media folder
                        alt_text=f"{product.name} image",
                        is_primary=True,
                        order=1
                    )
                    
                    # Create product variants if needed
                    if product_data.get("has_variants", False):
                        if product_data["variant_type"] == "Color":
                            variant_values = colors
                        else:
                            variant_values = sizes
                        
                        for i, variant_value in enumerate(variant_values[:3]):  # Create 3 variants
                            variant_sku = f"{sku}-{variant_value.value[:2].upper()}"
                            variant = ProductVariant.objects.create(
                                product=product,
                                sku=variant_sku,
                                price=product_data["price"] + (i * 10),  # Increase price slightly for each variant
                                stock_quantity=random.randint(5, 30),
                                is_active=True
                            )
                            variant.variant_values.add(variant_value)
                            print(f"  Created variant: {variant}")
                except Exception as e:
                    print(f"Error creating product {product_data['name']}: {str(e)}")

# Execute the script when run directly
if __name__ == "__main__":
    populator = DatabasePopulator()
    populator.run()