# products/populate_database.py
import os
import django
import random
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itiproject.settings')

django.setup()

# Import models after Django setup
from products.models import Category, Brand, Product, ProductImage, Size, Color, FlashSale, FlashSaleItem

class DatabasePopulator:
    """Class to populate the database with product data"""
    
    def __init__(self):
        self.created_products = []
    
    def run(self):
        print('Seeding data...')
        
        # Create sizes and colors
        self.create_sizes()
        self.create_colors()
        
        # Create categories
        self.create_categories()
        
        # Create brands
        self.create_brands()
        
        # Create products
        self.create_products()
        
        # Create flash sales
        self.create_flash_sales()
        
        print('Successfully seeded database!')
    
    def create_sizes(self):
        """Create size records using model choices"""
        for size_choice, _ in Size.SIZE_CHOICES:
            size, created = Size.objects.get_or_create(name=size_choice)
            print(f"{'Created' if created else 'Found'} size: {size.name}")
    
    def create_colors(self):
        """Create color records using model choices"""
        for color_choice, _ in Color.COLOR_CHOICES:
            color, created = Color.objects.get_or_create(name=color_choice)
            print(f"{'Created' if created else 'Found'} color: {color.name}")
    
    def create_categories(self):
        """Create a comprehensive category hierarchy"""
        categories_structure = {
            "Electronics": {
                "children": {
                    "Smartphones": ["Android Phones", "iPhones", "Budget Phones", "Gaming Phones"],
                    "Laptops": ["Gaming Laptops", "Business Laptops", "Ultrabooks", "2-in-1 Laptops"],
                    "Audio": ["Headphones", "Earbuds", "Speakers", "Soundbars"],
                    "Cameras": ["DSLR", "Mirrorless", "Compact", "Action Cameras"],
                    "Tablets": ["Android Tablets", "iPads", "E-readers", "Graphics Tablets"],
                    "Gaming": ["Gaming Consoles", "Gaming Accessories", "VR Headsets", "Gaming Chairs"],
                }
            },
            "Fashion": {
                "children": {
                    "Men's Clothing": ["T-shirts", "Shirts", "Jeans", "Suits", "Hoodies", "Jackets"],
                    "Women's Clothing": ["Dresses", "Tops", "Pants", "Skirts", "Blouses", "Coats"],
                    "Shoes": ["Running Shoes", "Casual Shoes", "Formal Shoes", "Boots", "Sandals"],
                    "Accessories": ["Bags", "Wallets", "Belts", "Watches", "Sunglasses", "Jewelry"],
                    "Sportswear": ["Activewear", "Gym Clothing", "Sports Shoes", "Yoga Wear"],
                }
            },
            "Home & Kitchen": {
                "children": {
                    "Furniture": ["Sofas", "Beds", "Tables", "Chairs", "Wardrobes", "TV Units"],
                    "Kitchen Appliances": ["Refrigerators", "Microwaves", "Coffee Makers", "Blenders", "Ovens"],
                    "Kitchenware": ["Cookware", "Cutlery", "Storage Containers", "Bakeware"],
                    "Home Decor": ["Wall Art", "Rugs", "Cushions", "Lamps", "Curtains", "Vases"],
                    "Bedding": ["Bed Sheets", "Pillows", "Blankets", "Comforters", "Mattresses"],
                }
            },
            "Beauty & Personal Care": {
                "children": {
                    "Skincare": ["Moisturizers", "Cleansers", "Serums", "Sunscreen", "Face Masks"],
                    "Makeup": ["Foundation", "Lipstick", "Eyeshadow", "Mascara", "Concealer"],
                    "Haircare": ["Shampoo", "Conditioner", "Hair Oil", "Hair Styling", "Hair Treatment"],
                    "Fragrances": ["Perfumes", "Deodorants", "Body Mists", "Cologne"],
                    "Personal Care": ["Body Wash", "Body Lotion", "Hand Care", "Oral Care"],
                }
            },
            "Sports & Outdoors": {
                "children": {
                    "Exercise & Fitness": ["Gym Equipment", "Yoga Mats", "Weights", "Fitness Trackers"],
                    "Outdoor Recreation": ["Camping Gear", "Hiking Equipment", "Cycling", "Water Sports"],
                    "Sports Equipment": ["Cricket", "Football", "Basketball", "Tennis", "Badminton"],
                    "Athletic Clothing": ["Running Wear", "Compression Wear", "Sports Bras", "Athletic Shoes"],
                }
            },
            "Books & Media": {
                "children": {
                    "Books": ["Fiction", "Non-fiction", "Educational", "Comics", "Children's Books"],
                    "Movies & TV": ["DVDs", "Blu-ray", "Digital Downloads", "Box Sets"],
                    "Music": ["CDs", "Vinyl Records", "Digital Music", "Musical Instruments"],
                    "Gaming": ["Video Games", "Board Games", "Card Games", "Puzzles"],
                }
            }
        }
        
        for main_name, main_data in categories_structure.items():
            # Create main category with unique slug
            main_slug = slugify(main_name)
            main_cat, created = Category.objects.get_or_create(
                name=main_name,
                defaults={"slug": main_slug, "is_active": True}
            )
            print(f"{'Created' if created else 'Found'} main category: {main_cat.name}")
            
            # Create subcategories
            for sub_name, children in main_data["children"].items():
                # Create unique slug for subcategory
                sub_slug = f"{main_slug}-{slugify(sub_name)}"
                sub_cat, created = Category.objects.get_or_create(
                    name=sub_name,
                    parent=main_cat,
                    defaults={"slug": sub_slug, "is_active": True}
                )
                print(f"  {'Created' if created else 'Found'} subcategory: {sub_cat.name}")
                
                # Create third-level categories
                for child_name in children:
                    # Create unique slug for child category
                    child_slug = f"{sub_slug}-{slugify(child_name)}"
                    child_cat, created = Category.objects.get_or_create(
                        name=child_name,
                        parent=sub_cat,
                        defaults={"slug": child_slug, "is_active": True}
                    )
                    print(f"    {'Created' if created else 'Found'} child category: {child_cat.name}")
    
    def create_brands(self):
        """Create diverse brands across different categories"""
        brands_by_category = {
            "Electronics": ["Apple", "Samsung", "Sony", "LG", "Xiaomi", "OnePlus", "Dell", "HP", "Lenovo", "Asus"],
            "Fashion": ["Nike", "Adidas", "Zara", "H&M", "Uniqlo", "Gap", "Levi's", "Calvin Klein", "Tommy Hilfiger", "Gucci"],
            "Home": ["IKEA", "Philips", "Bosch", "Whirlpool", "Dyson", "Cuisinart", "KitchenAid", "Tupperware"],
            "Beauty": ["L'Oreal", "Maybelline", "MAC", "Estee Lauder", "Clinique", "Neutrogena", "Nivea", "Dove"],
            "Sports": ["Nike", "Adidas", "Puma", "Reebok", "Under Armour", "New Balance", "Fila", "Asics"],
        }
        
        for category_group, brand_names in brands_by_category.items():
            for brand_name in brand_names:
                brand, created = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={"slug": slugify(brand_name)}
                )
                print(f"{'Created' if created else 'Found'} brand: {brand.name}")
    
    def create_products(self):
        """Create diverse products with realistic data"""
        # Get all third-level categories
        leaf_categories = Category.objects.filter(children__isnull=True, parent__parent__isnull=False)
        brands = list(Brand.objects.all())
        colors = list(Color.objects.all())
        sizes = list(Size.objects.all())
        
        product_templates = [
            # Electronics
            {
                "category_name": "Android Phones",
                "brand_names": ["Samsung", "Xiaomi", "OnePlus"],
                "products": [
                    {"name": "Galaxy S23 Ultra", "price": 1199.99, "has_sizes": False, "has_colors": True},
                    {"name": "Mi 13 Pro", "price": 899.99, "has_sizes": False, "has_colors": True},
                    {"name": "OnePlus 11", "price": 699.99, "has_sizes": False, "has_colors": True},
                ]
            },
            {
                "category_name": "Gaming Laptops",
                "brand_names": ["Dell", "HP", "Asus"],
                "products": [
                    {"name": "Alienware m16", "price": 2499.99, "has_sizes": False, "has_colors": False},
                    {"name": "ROG Strix G16", "price": 1899.99, "has_sizes": False, "has_colors": False},
                    {"name": "Omen 16", "price": 1699.99, "has_sizes": False, "has_colors": False},
                ]
            },
            {
                "category_name": "Headphones",
                "brand_names": ["Sony", "Apple", "Samsung"],
                "products": [
                    {"name": "WH-1000XM5", "price": 399.99, "has_sizes": False, "has_colors": True},
                    {"name": "AirPods Max", "price": 549.99, "has_sizes": False, "has_colors": True},
                    {"name": "Galaxy Buds Pro", "price": 229.99, "has_sizes": False, "has_colors": True},
                ]
            },
            # Fashion
            {
                "category_name": "T-shirts",
                "brand_names": ["Nike", "Adidas", "Gap"],
                "products": [
                    {"name": "Classic Logo Tee", "price": 29.99, "has_sizes": True, "has_colors": True},
                    {"name": "Sport Performance Tee", "price": 39.99, "has_sizes": True, "has_colors": True},
                    {"name": "Vintage Graphic Tee", "price": 24.99, "has_sizes": True, "has_colors": True},
                ]
            },
            {
                "category_name": "Running Shoes",
                "brand_names": ["Nike", "Adidas", "New Balance"],
                "products": [
                    {"name": "Air Zoom Pegasus", "price": 129.99, "has_sizes": True, "has_colors": True},
                    {"name": "Ultraboost 22", "price": 179.99, "has_sizes": True, "has_colors": True},
                    {"name": "Fresh Foam 1080", "price": 159.99, "has_sizes": True, "has_colors": True},
                ]
            },
            {
                "category_name": "Dresses",
                "brand_names": ["Zara", "H&M", "Uniqlo"],
                "products": [
                    {"name": "Floral Summer Dress", "price": 49.99, "has_sizes": True, "has_colors": True},
                    {"name": "Little Black Dress", "price": 69.99, "has_sizes": True, "has_colors": False},
                    {"name": "Maxi Beach Dress", "price": 59.99, "has_sizes": True, "has_colors": True},
                ]
            },
            # Home & Kitchen
            {
                "category_name": "Coffee Makers",
                "brand_names": ["Philips", "Cuisinart", "KitchenAid"],
                "products": [
                    {"name": "Espresso Machine Pro", "price": 299.99, "has_sizes": False, "has_colors": False},
                    {"name": "Drip Coffee Maker", "price": 79.99, "has_sizes": False, "has_colors": True},
                    {"name": "French Press Deluxe", "price": 49.99, "has_sizes": False, "has_colors": False},
                ]
            },
            {
                "category_name": "Sofas",
                "brand_names": ["IKEA"],
                "products": [
                    {"name": "EKTORP 3-seat Sofa", "price": 599.99, "has_sizes": False, "has_colors": True},
                    {"name": "KIVIK Corner Sofa", "price": 899.99, "has_sizes": False, "has_colors": True},
                    {"name": "SÖDERHAMN Modular Sofa", "price": 799.99, "has_sizes": False, "has_colors": True},
                ]
            },
            # Beauty
            {
                "category_name": "Moisturizers",
                "brand_names": ["L'Oreal", "Neutrogena", "Clinique"],
                "products": [
                    {"name": "Hydra-Boost Daily Moisturizer", "price": 24.99, "has_sizes": False, "has_colors": False},
                    {"name": "Anti-Aging Night Cream", "price": 49.99, "has_sizes": False, "has_colors": False},
                    {"name": "Oil-Free Face Lotion", "price": 19.99, "has_sizes": False, "has_colors": False},
                ]
            },
            {
                "category_name": "Lipstick",
                "brand_names": ["MAC", "Maybelline", "L'Oreal"],
                "products": [
                    {"name": "Matte Lipstick Collection", "price": 22.99, "has_sizes": False, "has_colors": True},
                    {"name": "Long-Lasting Lip Color", "price": 14.99, "has_sizes": False, "has_colors": True},
                    {"name": "Moisturizing Lipstick", "price": 18.99, "has_sizes": False, "has_colors": True},
                ]
            },
        ]
        
        for template in product_templates:
            # Find category
            category = Category.objects.filter(name=template["category_name"]).first()
            if not category:
                continue
                
            for product_data in template["products"]:
                # Find appropriate brand
                brand = Brand.objects.filter(name__in=template["brand_names"]).order_by('?').first()
                if not brand:
                    brand = random.choice(brands)
                
                # Generate unique SKU
                sku = f"{brand.name[:3].upper()}-{product_data['name'][:5].replace(' ', '').upper()}-{random.randint(10000, 99999)}"
                
                # Create product
                try:
                    # Calculate prices
                    base_price = Decimal(str(product_data["price"]))
                    sale_price = None
                    sale_start = None
                    sale_end = None
                    
                    # 30% chance of being on sale
                    if random.random() < 0.3:
                        discount_percentage = random.uniform(10, 40)
                        sale_price = base_price * Decimal(1 - discount_percentage/100)
                        sale_price = sale_price.quantize(Decimal('0.01'))
                        sale_start = timezone.now() - timedelta(days=random.randint(0, 7))
                        sale_end = timezone.now() + timedelta(days=random.randint(7, 30))
                    
                    product = Product.objects.create(
                        name=f"{brand.name} {product_data['name']}",
                        slug=slugify(f"{brand.name}-{product_data['name']}-{sku}"),
                        sku=sku,
                        category=category,
                        brand=brand,
                        description=f"High-quality {product_data['name']} from {brand.name}. "
                                  f"This premium product combines style and functionality to meet your needs. "
                                  f"Featuring the latest technology and design innovations.",
                        price=base_price,
                        sale_price=sale_price,
                        sale_start_date=sale_start,
                        sale_end_date=sale_end,
                        stock_quantity=random.randint(20, 200),
                        is_featured=random.random() < 0.2,  # 20% chance of being featured
                        specifications={
                            "warranty": f"{random.choice([1, 2, 3])} years",
                            "material": random.choice(["Premium", "Standard", "Eco-friendly"]),
                            "origin": random.choice(["USA", "China", "Germany", "Japan", "Korea"]),
                        },
                        weight=Decimal(random.uniform(0.1, 5.0)).quantize(Decimal('0.001')),
                        meta_title=f"Buy {brand.name} {product_data['name']} Online",
                        meta_description=f"Shop for {brand.name} {product_data['name']} at the best prices. "
                                       f"Free shipping available. 100% authentic products.",
                    )
                    
                    # Add sizes if applicable
                    if product_data.get("has_sizes", False):
                        # Add relevant sizes based on category
                        if "Shoes" in category.name:
                            # For shoes, use all sizes
                            product.sizes.set(sizes)
                        else:
                            # For clothing, use common sizes
                            common_sizes = ["S", "M", "L", "XL", "XXL"]
                            selected_sizes = Size.objects.filter(name__in=common_sizes)
                            product.sizes.set(selected_sizes)
                    
                    # Add colors if applicable
                    if product_data.get("has_colors", False):
                        # Select 2-5 random colors
                        num_colors = random.randint(2, 5)
                        selected_colors = random.sample(colors, min(num_colors, len(colors)))
                        product.colors.set(selected_colors)
                    
                    # Set material if it's a fashion product
                    if category.parent and category.parent.parent and category.parent.parent.name == "Fashion":
                        materials = ["Cotton", "Polyester", "Wool", "Leather", "Denim", "Silk", "Linen"]
                        product.material = random.choice(materials)
                        product.save()
                    
                    # Create product images (use default image)
                    for i in range(random.randint(3, 5)):
                        ProductImage.objects.create(
                            product=product,
                            image="product_images/default.jpg",
                            alt_text=f"{product.name} - Image {i+1}",
                            is_primary=(i == 0),
                            order=i
                        )
                    
                    self.created_products.append(product)
                    print(f"Created product: {product.name}")
                    
                except Exception as e:
                    print(f"Error creating product {product_data['name']}: {str(e)}")
    
    def create_flash_sales(self):
        """Create flash sales with some products"""
        if not self.created_products:
            print("No products available for flash sales")
            return
            
        flash_sales_data = [
            {
                "name": "Mega Electronics Sale",
                "description": "Huge discounts on electronics! Limited time only.",
                "duration_hours": 48,
                "discount_range": (20, 50)
            },
            {
                "name": "Fashion Friday",
                "description": "Exclusive deals on fashion items every Friday!",
                "duration_hours": 24,
                "discount_range": (30, 70)
            },
            {
                "name": "Home Essentials Deal",
                "description": "Transform your home with these amazing deals.",
                "duration_hours": 72,
                "discount_range": (15, 40)
            },
        ]
        
        for sale_data in flash_sales_data:
            start_time = timezone.now() + timedelta(hours=random.randint(0, 24))
            end_time = start_time + timedelta(hours=sale_data["duration_hours"])
            
            flash_sale = FlashSale.objects.create(
                name=sale_data["name"],
                slug=slugify(sale_data["name"]),
                description=sale_data["description"],
                start_time=start_time,
                end_time=end_time,
                is_active=True
            )
            
            # Add 5-10 random products to the flash sale
            num_products = random.randint(5, min(10, len(self.created_products)))
            selected_products = random.sample(self.created_products, num_products)
            
            for product in selected_products:
                discount = random.randint(*sale_data["discount_range"])
                FlashSaleItem.objects.create(
                    flash_sale=flash_sale,
                    product=product,
                    discount_percentage=discount,
                    quantity_limit=random.randint(10, 50),
                    quantity_sold=random.randint(0, 10)
                )
            
            print(f"Created flash sale: {flash_sale.name} with {num_products} products")


# Execute the script when run directly
if __name__ == "__main__":
    populator = DatabasePopulator()
    populator.run()

# for runnign the script 
# cd /media/king/16D8CD34D8CD1343/projects\ ITI/final-project/back-end/iti-final-django-jumia/
# DJANGO_SETTINGS_MODULE=itiproject.settings python itiproject/products/populate_database.py