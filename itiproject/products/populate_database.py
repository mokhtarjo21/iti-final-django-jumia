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
                    "Smartphones": {
                        "children": [
                            "Android Phones",
                            "iPhones",
                            "Budget Phones",
                            "Gaming Phones",
                            "Foldable Phones",
                            "Business Phones"
                        ]
                    },
                    "Laptops": {
                        "children": [
                            "Gaming Laptops",
                            "Business Laptops",
                            "Ultrabooks",
                            "2-in-1 Laptops",
                            "Student Laptops",
                            "Workstation Laptops"
                        ]
                    },
                    "Audio": {
                        "children": [
                            "Headphones",
                            "Earbuds",
                            "Speakers",
                            "Soundbars",
                            "Home Theater",
                            "Professional Audio"
                        ]
                    },
                    "Cameras": {
                        "children": [
                            "DSLR",
                            "Mirrorless",
                            "Compact",
                            "Action Cameras",
                            "Video Cameras",
                            "Security Cameras"
                        ]
                    },
                    "Tablets": {
                        "children": [
                            "Android Tablets",
                            "iPads",
                            "E-readers",
                            "Graphics Tablets",
                            "Kids Tablets",
                            "Professional Tablets"
                        ]
                    },
                    "Gaming": {
                        "children": [
                            "Gaming Consoles",
                            "Gaming Accessories",
                            "VR Headsets",
                            "Gaming Chairs",
                            "Gaming Monitors",
                            "Gaming Keyboards"
                        ]
                    }
                }
            },
            "Fashion": {
                "children": {
                    "Men's Clothing": {
                        "children": [
                            "T-shirts",
                            "Shirts",
                            "Jeans",
                            "Suits",
                            "Hoodies",
                            "Jackets",
                            "Pants",
                            "Shorts",
                            "Sweaters",
                            "Formal Wear"
                        ]
                    },
                    "Women's Clothing": {
                        "children": [
                            "Dresses",
                            "Tops",
                            "Pants",
                            "Skirts",
                            "Blouses",
                            "Coats",
                            "Sweaters",
                            "Activewear",
                            "Swimwear",
                            "Lingerie"
                        ]
                    },
                    "Shoes": {
                        "children": [
                            "Running Shoes",
                            "Casual Shoes",
                            "Formal Shoes",
                            "Boots",
                            "Sandals",
                            "Sneakers",
                            "Sports Shoes",
                            "Heels",
                            "Flats",
                            "Slippers"
                        ]
                    },
                    "Accessories": {
                        "children": [
                            "Bags",
                            "Wallets",
                            "Belts",
                            "Watches",
                            "Sunglasses",
                            "Jewelry",
                            "Hats",
                            "Scarves",
                            "Gloves",
                            "Ties"
                        ]
                    },
                    "Sportswear": {
                        "children": [
                            "Activewear",
                            "Gym Clothing",
                            "Sports Shoes",
                            "Yoga Wear",
                            "Swimwear",
                            "Team Sports",
                            "Outdoor Gear",
                            "Fitness Accessories"
                        ]
                    }
                }
            },
            "Home & Kitchen": {
                "children": {
                    "Furniture": {
                        "children": [
                            "Sofas",
                            "Beds",
                            "Tables",
                            "Chairs",
                            "Wardrobes",
                            "TV Units",
                            "Bookshelves",
                            "Office Furniture",
                            "Outdoor Furniture",
                            "Kids Furniture"
                        ]
                    },
                    "Kitchen Appliances": {
                        "children": [
                            "Refrigerators",
                            "Microwaves",
                            "Coffee Makers",
                            "Blenders",
                            "Ovens",
                            "Dishwashers",
                            "Mixers",
                            "Toasters",
                            "Food Processors",
                            "Air Fryers"
                        ]
                    },
                    "Kitchenware": {
                        "children": [
                            "Cookware",
                            "Cutlery",
                            "Storage Containers",
                            "Bakeware",
                            "Kitchen Tools",
                            "Dinnerware",
                            "Drinkware",
                            "Kitchen Gadgets",
                            "Kitchen Storage",
                            "Kitchen Linens"
                        ]
                    },
                    "Home Decor": {
                        "children": [
                            "Wall Art",
                            "Rugs",
                            "Cushions",
                            "Lamps",
                            "Curtains",
                            "Vases",
                            "Mirrors",
                            "Clocks",
                            "Photo Frames",
                            "Decorative Items"
                        ]
                    },
                    "Bedding": {
                        "children": [
                            "Bed Sheets",
                            "Pillows",
                            "Blankets",
                            "Comforters",
                            "Mattresses",
                            "Duvets",
                            "Bed Skirts",
                            "Pillowcases",
                            "Quilts",
                            "Bed Covers"
                        ]
                    }
                }
            },
            "Beauty & Personal Care": {
                "children": {
                    "Skincare": {
                        "children": [
                            "Moisturizers",
                            "Cleansers",
                            "Serums",
                            "Sunscreen",
                            "Face Masks",
                            "Eye Care",
                            "Acne Treatment",
                            "Anti-aging",
                            "Body Care",
                            "Hand & Foot Care"
                        ]
                    },
                    "Makeup": {
                        "children": [
                            "Foundation",
                            "Lipstick",
                            "Eyeshadow",
                            "Mascara",
                            "Concealer",
                            "Blush",
                            "Bronzer",
                            "Eyeliner",
                            "Makeup Brushes",
                            "Makeup Sets"
                        ]
                    },
                    "Haircare": {
                        "children": [
                            "Shampoo",
                            "Conditioner",
                            "Hair Oil",
                            "Hair Styling",
                            "Hair Treatment",
                            "Hair Color",
                            "Hair Tools",
                            "Hair Accessories",
                            "Hair Masks",
                            "Hair Serums"
                        ]
                    },
                    "Fragrances": {
                        "children": [
                            "Perfumes",
                            "Deodorants",
                            "Body Mists",
                            "Cologne",
                            "Fragrance Sets",
                            "Room Fragrances",
                            "Car Fragrances",
                            "Essential Oils",
                            "Scented Candles",
                            "Aromatherapy"
                        ]
                    },
                    "Personal Care": {
                        "children": [
                            "Body Wash",
                            "Body Lotion",
                            "Hand Care",
                            "Oral Care",
                            "Shaving",
                            "Bath & Shower",
                            "Feminine Care",
                            "Men's Grooming",
                            "Foot Care",
                            "Travel Size"
                        ]
                    }
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
            for sub_name, sub_data in main_data["children"].items():
                # Create unique slug for subcategory
                sub_slug = f"{main_slug}-{slugify(sub_name)}"
                sub_cat, created = Category.objects.get_or_create(
                    name=sub_name,
                    parent=main_cat,
                    defaults={"slug": sub_slug, "is_active": True}
                )
                print(f"  {'Created' if created else 'Found'} subcategory: {sub_cat.name}")
                
                # Create third-level categories
                for child_name in sub_data["children"]:
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
            # Electronics - Smartphones
            {
                "category_name": "Android Phones",
                "brand_names": ["Samsung", "Xiaomi", "OnePlus", "Google", "Motorola"],
                "products": [
                    {"name": "Galaxy S23 Ultra", "price": 1199.99, "has_sizes": False, "has_colors": True},
                    {"name": "Mi 13 Pro", "price": 899.99, "has_sizes": False, "has_colors": True},
                    {"name": "OnePlus 11", "price": 699.99, "has_sizes": False, "has_colors": True},
                    {"name": "Pixel 7 Pro", "price": 899.99, "has_sizes": False, "has_colors": True},
                    {"name": "Edge 30 Ultra", "price": 799.99, "has_sizes": False, "has_colors": True},
                ]
            },
            {
                "category_name": "iPhones",
                "brand_names": ["Apple"],
                "products": [
                    {"name": "iPhone 15 Pro Max", "price": 1199.99, "has_sizes": False, "has_colors": True},
                    {"name": "iPhone 15 Pro", "price": 999.99, "has_sizes": False, "has_colors": True},
                    {"name": "iPhone 15 Plus", "price": 899.99, "has_sizes": False, "has_colors": True},
                    {"name": "iPhone 15", "price": 799.99, "has_sizes": False, "has_colors": True},
                    {"name": "iPhone 14", "price": 699.99, "has_sizes": False, "has_colors": True},
                ]
            },
            # Electronics - Laptops
            {
                "category_name": "Gaming Laptops",
                "brand_names": ["Dell", "HP", "Asus", "MSI", "Lenovo"],
                "products": [
                    {"name": "Alienware m16", "price": 2499.99, "has_sizes": False, "has_colors": False},
                    {"name": "ROG Strix G16", "price": 1899.99, "has_sizes": False, "has_colors": False},
                    {"name": "Omen 16", "price": 1699.99, "has_sizes": False, "has_colors": False},
                    {"name": "GE76 Raider", "price": 2299.99, "has_sizes": False, "has_colors": False},
                    {"name": "Legion Pro 7", "price": 1999.99, "has_sizes": False, "has_colors": False},
                ]
            },
            # Fashion - Men's Clothing
            {
                "category_name": "T-shirts",
                "brand_names": ["Nike", "Adidas", "Gap", "H&M", "Uniqlo"],
                "products": [
                    {"name": "Classic Logo Tee", "price": 29.99, "has_sizes": True, "has_colors": True},
                    {"name": "Sport Performance Tee", "price": 39.99, "has_sizes": True, "has_colors": True},
                    {"name": "Vintage Graphic Tee", "price": 24.99, "has_sizes": True, "has_colors": True},
                    {"name": "Essential Crew Neck", "price": 19.99, "has_sizes": True, "has_colors": True},
                    {"name": "Premium Cotton Tee", "price": 34.99, "has_sizes": True, "has_colors": True},
                ]
            },
            {
                "category_name": "Jeans",
                "brand_names": ["Levi's", "Wrangler", "Lee", "Calvin Klein", "Tommy Hilfiger"],
                "products": [
                    {"name": "501 Original Fit", "price": 69.99, "has_sizes": True, "has_colors": True},
                    {"name": "Classic Straight Fit", "price": 59.99, "has_sizes": True, "has_colors": True},
                    {"name": "Slim Fit Stretch", "price": 64.99, "has_sizes": True, "has_colors": True},
                    {"name": "Premium Denim", "price": 79.99, "has_sizes": True, "has_colors": True},
                    {"name": "Relaxed Fit", "price": 54.99, "has_sizes": True, "has_colors": True},
                ]
            },
            # Fashion - Women's Clothing
            {
                "category_name": "Dresses",
                "brand_names": ["Zara", "H&M", "Uniqlo", "Forever 21", "Mango"],
                "products": [
                    {"name": "Floral Summer Dress", "price": 49.99, "has_sizes": True, "has_colors": True},
                    {"name": "Little Black Dress", "price": 69.99, "has_sizes": True, "has_colors": False},
                    {"name": "Maxi Beach Dress", "price": 59.99, "has_sizes": True, "has_colors": True},
                    {"name": "Casual Wrap Dress", "price": 44.99, "has_sizes": True, "has_colors": True},
                    {"name": "Evening Gown", "price": 89.99, "has_sizes": True, "has_colors": True},
                ]
            },
            # Home & Kitchen
            {
                "category_name": "Sofas",
                "brand_names": ["IKEA", "Ashley", "Pottery Barn", "West Elm", "Crate & Barrel"],
                "products": [
                    {"name": "EKTORP 3-seat Sofa", "price": 599.99, "has_sizes": False, "has_colors": True},
                    {"name": "KIVIK Corner Sofa", "price": 899.99, "has_sizes": False, "has_colors": True},
                    {"name": "SÖDERHAMN Modular Sofa", "price": 799.99, "has_sizes": False, "has_colors": True},
                    {"name": "Modern Sectional", "price": 1299.99, "has_sizes": False, "has_colors": True},
                    {"name": "Leather Recliner Sofa", "price": 1499.99, "has_sizes": False, "has_colors": True},
                ]
            },
            # Beauty & Personal Care
            {
                "category_name": "Moisturizers",
                "brand_names": ["L'Oreal", "Neutrogena", "Clinique", "CeraVe", "La Roche-Posay"],
                "products": [
                    {"name": "Hydra-Boost Daily Moisturizer", "price": 24.99, "has_sizes": False, "has_colors": False},
                    {"name": "Anti-Aging Night Cream", "price": 49.99, "has_sizes": False, "has_colors": False},
                    {"name": "Oil-Free Face Lotion", "price": 19.99, "has_sizes": False, "has_colors": False},
                    {"name": "Ceramide Moisturizing Cream", "price": 29.99, "has_sizes": False, "has_colors": False},
                    {"name": "Hydrating Face Cream", "price": 34.99, "has_sizes": False, "has_colors": False},
                ]
            },
            {
                "category_name": "Lipstick",
                "brand_names": ["MAC", "Maybelline", "L'Oreal", "Revlon", "NYX"],
                "products": [
                    {"name": "Matte Lipstick Collection", "price": 22.99, "has_sizes": False, "has_colors": True},
                    {"name": "Long-Lasting Lip Color", "price": 14.99, "has_sizes": False, "has_colors": True},
                    {"name": "Moisturizing Lipstick", "price": 18.99, "has_sizes": False, "has_colors": True},
                    {"name": "Liquid Lipstick", "price": 16.99, "has_sizes": False, "has_colors": True},
                    {"name": "Satin Finish Lipstick", "price": 20.99, "has_sizes": False, "has_colors": True},
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
                    
                    # Generate realistic description based on category and product
                    description = self.generate_product_description(category, product_data["name"], brand)
                    
                    # Generate specifications based on category
                    specifications = self.generate_product_specifications(category, product_data["name"])
                    
                    product = Product.objects.create(
                        name=f"{brand.name} {product_data['name']}",
                        slug=slugify(f"{brand.name}-{product_data['name']}-{sku}"),
                        sku=sku,
                        category=category,
                        brand=brand,
                        description=description,
                        price=base_price,
                        sale_price=sale_price,
                        sale_start_date=sale_start,
                        sale_end_date=sale_end,
                        stock_quantity=random.randint(20, 200),
                        is_featured=random.random() < 0.2,  # 20% chance of being featured
                        specifications=specifications,
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
    
    def generate_product_description(self, category, product_name, brand):
        """Generate a realistic product description based on category and product"""
        descriptions = {
            "Electronics": [
                f"Experience the latest technology with the {brand.name} {product_name}. "
                f"This cutting-edge device combines powerful performance with sleek design. "
                f"Perfect for both work and entertainment, it features advanced specifications "
                f"and innovative features that set new standards in the industry.",
                
                f"The {brand.name} {product_name} represents the pinnacle of technological innovation. "
                f"With its premium build quality and state-of-the-art features, this device "
                f"delivers an exceptional user experience that exceeds expectations.",
                
                f"Discover the future of technology with the {brand.name} {product_name}. "
                f"This revolutionary device offers unmatched performance, stunning visuals, "
                f"and intuitive controls that make everyday tasks effortless."
            ],
            "Fashion": [
                f"Elevate your style with the {brand.name} {product_name}. "
                f"Crafted from premium materials, this piece combines comfort and fashion "
                f"to create a versatile addition to your wardrobe.",
                
                f"The {brand.name} {product_name} is a timeless piece that never goes out of style. "
                f"Perfect for any occasion, it offers both comfort and elegance in equal measure.",
                
                f"Make a statement with the {brand.name} {product_name}. "
                f"This carefully designed piece features premium quality materials and "
                f"expert craftsmanship for a look that's uniquely yours."
            ],
            "Home & Kitchen": [
                f"Transform your living space with the {brand.name} {product_name}. "
                f"This beautifully designed piece combines functionality with style "
                f"to create the perfect addition to your home.",
                
                f"The {brand.name} {product_name} brings comfort and elegance to your home. "
                f"Crafted with attention to detail, it offers both practicality and "
                f"aesthetic appeal for modern living.",
                
                f"Enhance your home with the {brand.name} {product_name}. "
                f"This thoughtfully designed piece offers the perfect blend of "
                f"style, comfort, and functionality."
            ],
            "Beauty & Personal Care": [
                f"Discover the secret to radiant beauty with {brand.name} {product_name}. "
                f"This premium product is formulated with high-quality ingredients "
                f"to deliver exceptional results for your skin.",
                
                f"The {brand.name} {product_name} is your daily essential for maintaining "
                f"healthy, beautiful skin. Its advanced formula works to nourish and "
                f"protect your skin's natural beauty.",
                
                f"Experience luxury skincare with {brand.name} {product_name}. "
                f"This carefully crafted product combines science and nature to "
                f"deliver visible results you'll love."
            ]
        }
        
        # Get the main category
        main_category = category
        while main_category.parent:
            main_category = main_category.parent
        
        # Get appropriate description based on main category
        category_descriptions = descriptions.get(main_category.name, descriptions["Fashion"])
        return random.choice(category_descriptions)
    
    def generate_product_specifications(self, category, product_name):
        """Generate realistic product specifications based on category"""
        specs = {
            "warranty": f"{random.choice([1, 2, 3])} years",
            "material": random.choice(["Premium", "Standard", "Eco-friendly"]),
            "origin": random.choice(["USA", "China", "Germany", "Japan", "Korea"]),
        }
        
        # Add category-specific specifications
        if "Electronics" in category.name:
            specs.update({
                "battery_life": f"{random.randint(8, 24)} hours",
                "screen_size": f"{random.choice(['5.5', '6.1', '6.7', '13.3', '15.6', '17.3'])} inches",
                "processor": random.choice(["Intel Core i7", "AMD Ryzen 9", "Apple M2", "Snapdragon 8 Gen 2"]),
                "memory": f"{random.choice(['8', '16', '32'])}GB",
                "storage": f"{random.choice(['128', '256', '512', '1TB'])}"
            })
        elif "Fashion" in category.name:
            specs.update({
                "care_instructions": random.choice(["Machine wash cold", "Hand wash only", "Dry clean only"]),
                "fit": random.choice(["Regular", "Slim", "Relaxed", "Oversized"]),
                "style": random.choice(["Casual", "Formal", "Sporty", "Classic"])
            })
        elif "Home & Kitchen" in category.name:
            specs.update({
                "dimensions": f"{random.randint(50, 200)}x{random.randint(50, 200)}x{random.randint(50, 200)} cm",
                "assembly_required": random.choice([True, False]),
                "color_options": random.randint(3, 8)
            })
        elif "Beauty & Personal Care" in category.name:
            specs.update({
                "skin_type": random.choice(["All skin types", "Dry skin", "Oily skin", "Combination skin"]),
                "volume": f"{random.choice(['30', '50', '100', '200'])}ml",
                "cruelty_free": random.choice([True, False])
            })
        
        return specs
    
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