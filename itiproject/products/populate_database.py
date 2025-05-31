# products/populate_database.py
import os
import django
import random
import json
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.cache import cache

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itiproject.settings')

django.setup()

# Import models after Django setup
from products.models import Category, Brand, Product, ProductImage, Size, Color, FlashSale, FlashSaleItem

class Command(BaseCommand):
    help = 'Populates the database with initial data'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting database population...')
    
        # Clear all cache before populating
        cache.clear()
        self.stdout.write('Cache cleared.')
        
        # Create sizes
        self.create_sizes()
        
        # Create colors
        self.create_colors()
        
        # Create categories
        self.create_categories()
        
        # Create brands
        self.create_brands()
        
        # Create products
        self.create_products()
        
        # Create flash sales
        self.create_flash_sales()
        
        # Clear cache again after populating
        cache.clear()
        self.stdout.write('Cache cleared after population.')
        
        self.stdout.write(self.style.SUCCESS('Database population completed successfully!'))
    
    def create_sizes(self):
        """Create size records using model choices"""
        for size_choice, _ in Size.SIZE_CHOICES:
            size, created = Size.objects.get_or_create(name=size_choice)
            self.stdout.write(f"{'Created' if created else 'Found'} size: {size.name}")
    
    def create_colors(self):
        """Create color records using model choices"""
        for color_choice, _ in Color.COLOR_CHOICES:
            color, created = Color.objects.get_or_create(name=color_choice)
            self.stdout.write(f"{'Created' if created else 'Found'} color: {color.name}")
    
    def create_categories(self):
        """Create categories with proper hierarchy and all required attributes"""
        # Define main categories with their subcategories and descriptions
        categories_data = {
            "Health & Beauty": {
                "description": "Discover a wide range of health and beauty products for your personal care needs",
                "children": {
                    "Personal Care": {
                        "description": "Essential personal care products for daily hygiene and wellness",
                        "children": {
                            "Oral Care": "Complete oral hygiene solutions including toothbrushes, toothpaste, and dental floss",
                            "Feminine Care": "Comprehensive feminine hygiene products for women's health",
                            "Shave & Hair Removal": "Professional shaving and hair removal products for smooth skin",
                            "Deodorants": "Long-lasting deodorants and antiperspirants for all-day freshness",
                            "Shower Gels": "Refreshing shower gels and body washes for daily cleansing",
                            "Face Wash": "Gentle and effective face washes for all skin types"
                        }
                    },
                    "Skin Care": {
                        "description": "Premium skincare products for healthy, radiant skin",
                        "children": {
                            "Body": "Nourishing body care products for soft, smooth skin",
                            "Eyes": "Specialized eye care products for bright, youthful eyes",
                            "Face": "Complete facial care solutions for all skin types",
                            "Feet & Hands": "Intensive care products for soft hands and feet",
                            "Sunscreens & Tanning oils": "Protection and tanning solutions for healthy skin"
                        }
                    },
                    "Hair Care": {
                        "description": "Professional hair care products for beautiful, healthy hair",
                        "children": {
                            "Styling Tools & Appliances": "Professional hair styling tools and appliances",
                            "Hair Styling Products": "Premium hair styling products for perfect looks",
                            "Shampoo, Conditioner & Serums": "Complete hair care solutions for all hair types",
                            "Hair Coloring": "Professional hair coloring products and kits",
                            "Extensions & Wigs": "High-quality hair extensions and wigs",
                            "Hair Accessories": "Stylish hair accessories for every occasion"
                        }
                    },
                    "Health Care": {
                        "description": "Essential healthcare products for your wellbeing",
                        "children": {
                            "Wellness & Relaxation": "Products for stress relief and relaxation",
                            "Sexual Wellness": "Discrete and essential sexual wellness products",
                            "Medical Supplies & Equipment": "Professional medical supplies and equipment",
                            "Contact Lenses & Solutions": "Quality contact lenses and care solutions"
                        }
                    },
                    "Fragrance": {
                        "description": "Luxury fragrances for every occasion",
                        "children": {
                            "Women's Perfumes & Body Splashes": "Elegant fragrances for women",
                            "Men's Perfumes": "Sophisticated fragrances for men",
                            "Children's Perfumes": "Gentle fragrances for children"
                        }
                    },
                    "Makeup": {
                        "description": "Professional makeup products for stunning looks",
                        "children": {
                            "Face Makeup": "Complete face makeup solutions",
                            "Lip Makeup": "Beautiful lip colors and care products",
                            "Eye Makeup": "Professional eye makeup products",
                            "Makeup Remover": "Effective makeup removal solutions",
                            "Makeup Brushes & Tools": "Professional makeup tools and brushes",
                            "Nails": "Complete nail care and color products"
                        }
                    }
                }
            },
            "Sporting Goods": {
                "description": "High-quality sporting equipment and accessories for all your fitness needs",
                "children": {
                    "Cardio Training": {
                        "description": "Professional cardio equipment for effective workouts",
                        "children": {
                            "Treadmills": "Premium treadmills for home and commercial use",
                            "Exercise Bike": "Quality exercise bikes for cardio workouts",
                            "Elliptical Trainers": "Advanced elliptical trainers for full-body workouts"
                        }
                    },
                    "Strength Training Equipment": {
                        "description": "Professional strength training equipment",
                        "children": {
                            "Dumbbells": "High-quality dumbbells for strength training",
                            "Bars": "Professional weight bars and accessories",
                            "Core & Abdominal Trainers": "Effective core and abdominal training equipment"
                        }
                    },
                    "Outdoor & Adventure": {
                        "description": "Equipment for outdoor sports and adventures",
                        "children": {
                            "Cycling": "Complete cycling equipment and accessories",
                            "Running": "Professional running gear and accessories"
                        }
                    },
                    "Sports Wear": {
                        "description": "High-performance sports wear for athletes",
                        "children": {
                            "Men Sports Wear": "Professional sports wear for men",
                            "Women Sports Wear": "High-quality sports wear for women"
                        }
                    },
                    "Sports & Fitness": {
                        "description": "Essential sports and fitness equipment",
                        "children": {
                            "Accessories": "Professional sports accessories",
                            "Swimming": "Complete swimming equipment and gear",
                            "Team Sports": "Equipment for various team sports",
                            "Hunting & Fishing": "Professional hunting and fishing gear",
                            "Leisure Sports & Game Room": "Equipment for leisure sports and games"
                        }
                    },
                    "Accessories": {
                        "description": "Essential sports and fitness accessories",
                        "children": {
                            "Exercise Bands": "Professional exercise bands and resistance tools",
                            "Jump Ropes": "Quality jump ropes for cardio workouts",
                            "Exercise Mats": "Comfortable and durable exercise mats",
                            "Gym Bags": "Spacious and durable gym bags"
                        }
                    }
                }
            },
            "Supermarket": {
                "description": "Essential household and grocery items for your daily needs",
                "children": {
                    "Household Supplies": {
                        "description": "Essential household supplies for daily living",
                        "children": {
                            "Food Storage, Foil & Cling Film": "Quality food storage solutions",
                            "Disposable Plates & Cutlery": "Eco-friendly disposable dining items",
                            "Disposable Cups": "Convenient disposable cups for any occasion",
                            "Trash, Compost & Lawn Bags": "Durable bags for waste management",
                            "Kitchen and Toilet Rolls": "Premium paper products for home",
                            "Facial Tissues": "Soft and gentle facial tissues",
                            "Household Batteries": "Reliable batteries for household devices",
                            "Lighters & Matches": "Quality lighters and matches"
                        }
                    },
                    "Household Cleaning": {
                        "description": "Effective cleaning products for your home",
                        "children": {
                            "Dishwashing": "Quality dishwashing products",
                            "Air Fresheners": "Fresh and pleasant air care products",
                            "Kitchen Cleaners": "Effective kitchen cleaning solutions",
                            "Bathroom Cleaners": "Professional bathroom cleaning products",
                            "All Purpose & Floor Cleaners": "Versatile cleaning solutions",
                            "Glass Cleaners": "Streak-free glass cleaning products",
                            "Disinfectants": "Powerful disinfecting solutions",
                            "Cleaning Tools": "Professional cleaning tools and equipment",
                            "Wood Polish & Care": "Premium wood care products"
                        }
                    },
                    "Beverages": {
                        "description": "Refreshing beverages for every occasion",
                        "children": {
                            "Soft Drinks, Juices & Water": "Quality beverages and water",
                            "Coffee, Tea & Cocoa": "Premium coffee, tea, and cocoa products"
                        }
                    },
                    "Pet Supplies": {
                        "description": "Essential supplies for your pets",
                        "children": {
                            "Dogs Supplies": "Complete care products for dogs",
                            "Cats Supplies": "Essential supplies for cats"
                        }
                    },
                    "Laundry": {
                        "description": "Effective laundry care products",
                        "children": {
                            "Detergent": "Powerful laundry detergents",
                            "Fabric Softener": "Gentle fabric softeners",
                            "Stain Removal": "Effective stain removal products",
                            "Lint Removal": "Quality lint removal tools"
                        }
                    }
                }
            },
            "Televisions & Audio": {
                "description": "Premium entertainment systems and audio equipment",
                "children": {
                    "Televisions & Receivers": {
                        "description": "High-quality televisions and audio receivers",
                        "children": {
                            "Televisions": "Premium television sets",
                            "LED & LCD TVs": "Advanced LED and LCD television technology",
                            "Smart TVs": "Intelligent smart television systems",
                            "Large Screens": "Immersive large screen displays",
                            "32-inch TVs": "Compact 32-inch television options",
                            "43-inch TVs": "Versatile 43-inch television displays",
                            "50-inch TVs": "Premium 50-inch television experience",
                            "55-inch TVs": "Immersive 55-inch television displays",
                            "65-inch TVs": "Large 65-inch television options",
                            "Receivers": "High-quality audio receivers",
                            "Remote Controls": "Universal and specialized remote controls"
                        }
                    },
                    "Audio": {
                        "description": "Professional audio equipment and accessories",
                        "children": {
                            "Radios": "Quality radio systems",
                            "Audio Speakers": "Premium audio speaker systems",
                            "Home Theater Systems": "Complete home theater solutions",
                            "Headphones": "Professional headphones and earphones"
                        }
                    },
                    "Cameras & Accessories": {
                        "description": "Professional photography equipment",
                        "children": {
                            "Digital Cameras": "Advanced digital camera systems",
                            "Lenses": "Professional camera lenses",
                            "Projectors": "High-quality video projectors"
                        }
                    }
                }
            },
            "Home & Furniture": {
                "description": "Premium home furnishings and furniture",
                "children": {
                    "Home Essentials": {
                        "description": "Essential home items and decor",
                        "children": {
                            "Home Decor": "Beautiful home decoration items",
                            "Lighting": "Premium lighting solutions",
                            "Bedding": "Comfortable bedding and linens",
                            "Bath": "Complete bathroom essentials",
                            "Storage & Organization": "Smart storage solutions",
                            "Cleaning Supplies": "Effective cleaning products",
                            "Event & Party Supplies": "Party and event essentials",
                            "Seasonal Decor": "Seasonal decoration items",
                            "Light Blubs": "Energy-efficient light bulbs",
                            "Power & Hand Tools": "Professional tools for home",
                            "Air Purifiers": "Advanced air purification systems",
                            "Tools & Improvements": "Home improvement tools"
                        }
                    },
                    "Furniture": {
                        "description": "Quality furniture for every room",
                        "children": {
                            "Living room": "Comfortable living room furniture",
                            "Bedroom Furniture": "Premium bedroom furnishings",
                            "Dining room": "Elegant dining room furniture",
                            "Bean Bags": "Comfortable bean bag chairs",
                            "TV Units": "Stylish TV stands and units",
                            "Storage Units": "Practical storage furniture"
                        }
                    },
                    "Kitchen & Dining": {
                        "description": "Complete kitchen and dining solutions",
                        "children": {
                            "Cookware": "Professional cookware sets",
                            "Bakeware": "Quality baking equipment",
                            "Serveware": "Elegant serving dishes",
                            "Glassware": "Premium glassware sets",
                            "Kitchen Utensils": "Essential kitchen tools",
                            "Kitchen Storage": "Smart kitchen storage solutions"
                        }
                    },
                    "Garden & Outdoors": {
                        "description": "Outdoor living and garden essentials",
                        "children": {
                            "Outdoor Decor": "Beautiful outdoor decoration",
                            "Outdoor Furniture & Accessories": "Comfortable outdoor furniture",
                            "Grills & Outdoor Cooking": "Professional outdoor cooking equipment",
                            "Gardening & Lawn Care": "Complete gardening tools",
                            "Pest Control Repellents": "Effective pest control solutions",
                            "Artificial Plants": "Realistic artificial plants"
                        }
                    },
                    "School & Office Supplies": {
                        "description": "Essential supplies for work and study",
                        "children": {
                            "School & Office Furniture": "Comfortable office furniture",
                            "Stationary & Supplies": "Quality office supplies"
                        }
                    }
                }
            },
            "Fashion": {
                "description": "Trendy fashion for everyone",
                "children": {
                    "Women's Fashion": {
                        "description": "Stylish women's clothing and accessories",
                        "children": {
                            "Tops & T-Shirts": "Trendy tops and t-shirts",
                            "Dresses": "Elegant dresses for every occasion",
                            "Blouses": "Stylish blouses and shirts",
                            "Bottoms": "Comfortable bottom wear",
                            "Sneakers": "Fashionable sneakers",
                            "Swimwear": "Stylish swimwear",
                            "Homewear & Lingerie": "Comfortable homewear",
                            "Sandals & Slippers": "Comfortable footwear",
                            "Accessories": "Fashion accessories",
                            "Kimonos": "Stylish kimonos",
                            "Sports Shoes": "Athletic footwear"
                        }
                    },
                    "Men's Fashion": {
                        "description": "Trendy men's clothing and accessories",
                        "children": {
                            "T-Shirts & Polos": "Casual t-shirts and polos",
                            "Shirts": "Formal and casual shirts",
                            "Pants": "Comfortable pants",
                            "Sportswear": "Athletic clothing",
                            "Shorts": "Casual shorts",
                            "Footwear": "Stylish shoes",
                            "Sports Shoes": "Athletic footwear",
                            "Pajamas": "Comfortable sleepwear",
                            "Watches": "Premium timepieces",
                            "Underwear": "Comfortable underwear",
                            "Accessories": "Fashion accessories"
                        }
                    },
                    "Kid's Fashion": {
                        "description": "Cute and comfortable kids' clothing",
                        "children": {
                            "Boy's Fashion": "Stylish boys' clothing",
                            "Girl's Fashion": "Trendy girls' clothing",
                            "Baby Boy's Fashion": "Cute baby boy clothes",
                            "Baby Girl's Fashion": "Adorable baby girl clothes"
                        }
                    }
                }
            },
            "Computing": {
                "description": "Professional computing equipment and accessories",
                "children": {
                    "Desktop & Laptops": {
                        "description": "High-performance computers",
                        "children": {
                            "2 in 1 Laptops": "Versatile 2-in-1 laptops",
                            "Gaming Laptops": "Powerful gaming laptops",
                            "Desktops": "High-performance desktops",
                            "Monitors": "Quality computer monitors"
                        }
                    },
                    "Data Storage": {
                        "description": "Reliable data storage solutions",
                        "children": {
                            "USB Flash Drives": "Portable USB drives",
                            "External Hard Drives": "External storage solutions",
                            "Memory Cards": "Digital memory cards"
                        }
                    },
                    "Computer Components": {
                        "description": "Essential computer parts",
                        "children": {
                            "Internal Hard Drives": "Internal storage solutions",
                            "Graphics Cards": "High-performance GPUs",
                            "Fans & Cooling": "Computer cooling systems",
                            "Audio & Video Accessories": "Multimedia accessories",
                            "Computer Memory": "RAM and memory modules"
                        }
                    },
                    "Computers & Accessories": {
                        "description": "Essential computer accessories",
                        "children": {
                            "Laptop Accessories": "Laptop add-ons",
                            "Laptop Bags & Sleeves": "Protective laptop cases",
                            "Keyboard": "Quality keyboards",
                            "Mouse": "Precision mice",
                            "Cleaning & Repair": "Computer maintenance tools",
                            "Cables & Interconnects": "Essential cables",
                            "Scanners": "Document scanners",
                            "Printer Ink & Toner": "Printing supplies"
                        }
                    },
                    "Networking Products": {
                        "description": "Professional networking equipment",
                        "children": {
                            "Network Adapters": "Network connectivity solutions",
                            "Routers": "High-speed routers",
                            "Wireless Access Points": "Wi-Fi access points",
                            "Network Switches": "Network management switches",
                            "Network Hubs": "Network connection hubs"
                        }
                    }
                }
            },
            "Baby Products": {
                "description": "Essential products for your baby",
                "children": {
                    "Diapering": {
                        "description": "Complete diapering solutions",
                        "children": {
                            "Disposable Diapers": "Quality disposable diapers",
                            "Wipes & Holders": "Baby wipes and dispensers",
                            "Diaper Bags": "Spacious diaper bags"
                        }
                    },
                    "Baby Feeding": {
                        "description": "Essential feeding supplies",
                        "children": {
                            "Bottle-Feeding & Tablewear": "Baby bottles and dishes",
                            "Breast feeding": "Breastfeeding essentials",
                            "Baby Food": "Nutritious baby food",
                            "Bibs & Burp Cloths": "Feeding accessories"
                        }
                    },
                    "Bathing & Skin Care": {
                        "description": "Gentle baby care products",
                        "children": {
                            "Lotions": "Moisturizing baby lotions",
                            "Shampoo & Conditioner": "Gentle hair care",
                            "Bath Essentials": "Complete bath sets",
                            "Grooming & Healthcare Kits": "Baby care kits",
                            "Potty Training": "Potty training supplies",
                            "Health & Baby Care": "Essential health products"
                        }
                    },
                    "Nursery": {
                        "description": "Complete nursery solutions",
                        "children": {
                            "Beds, Cribs & Bedding": "Comfortable sleeping solutions",
                            "Nursery Decor": "Beautiful nursery decorations"
                        }
                    },
                    "Baby Safety": {
                        "description": "Essential safety products",
                        "children": {
                            "Kitchen Safety": "Kitchen safety items",
                            "Outdoor Safety": "Outdoor safety products",
                            "Gear Safety": "Safety equipment"
                        }
                    },
                    "Gear": {
                        "description": "Essential baby gear",
                        "children": {
                            "Swings, Jumpers & Bouncers": "Baby entertainment items",
                            "Backpacks & Carriers": "Baby carrying solutions",
                            "Walkers": "Baby walking aids"
                        }
                    },
                    "Strollers & Accessories": {
                        "description": "Complete stroller solutions",
                        "children": {
                            "Accessories": "Stroller add-ons",
                            "Strollers": "Quality strollers",
                            "Car Seats": "Safe car seats"
                        }
                    },
                    "Toys & Games": {
                        "description": "Educational and fun toys",
                        "children": {
                            "Baby & Toddler Toys": "Age-appropriate toys",
                            "Dolls & Accessories": "Dolls and accessories",
                            "Learning & Education": "Educational toys",
                            "Action Figures & Statues": "Action figures",
                            "Arts & Crafts": "Creative toys",
                            "Dress Up & Pretend Play": "Role-play toys",
                            "Puzzles": "Educational puzzles",
                            "Toy Remote Control & Play Vehicles": "Remote control toys"
                        }
                    }
                }
            },
            "Phones & Tablets": {
                "description": "Latest mobile devices and accessories",
                "children": {
                    "Mobile Phones": {
                        "description": "Premium smartphones",
                        "children": {
                            "Android Phones": "Latest Android smartphones",
                            "IOS Phones": "Apple iPhone series",
                            "Cell Phones": "Basic cell phones"
                        }
                    },
                    "Tablets": {
                        "description": "High-performance tablets",
                        "children": {
                            "Tablets": "General tablets",
                            "Ipads": "Apple iPad series",
                            "Educational Tablets": "Learning tablets",
                            "Tablet Accessories": "Tablet add-ons"
                        }
                    },
                    "Telephones": {
                        "description": "Traditional telephones",
                        "children": {
                            "Landline Phones": "Home and office phones"
                        }
                    },
                    "Mobile Phones Accessories": {
                        "description": "Essential phone accessories",
                        "children": {
                            "Smart Watches": "Smart wearable devices",
                            "Bluetooth Headsets": "Wireless audio",
                            "Portable Power Banks": "Mobile charging solutions",
                            "Phone Cases": "Protective cases",
                            "Screen Protectors": "Screen protection",
                            "Cables": "Charging cables",
                            "Chargers": "Power adapters",
                            "Car Accessories": "Car phone accessories",
                            "Memory Cards": "Storage solutions",
                            "Mounts & Stands": "Phone holders",
                            "Selfie Sticks & Tripods": "Photo accessories",
                            "Batteries": "Replacement batteries",
                            "Adapters": "Connection adapters",
                            "Speakers": "Portable speakers"
                        }
                    }
                }
            },
            "Appliances": {
                "description": "Essential home appliances",
                "children": {
                    "Small Appliances": {
                        "description": "Compact home appliances",
                        "children": {
                            "Kettles": "Electric kettles",
                            "Blenders": "Food blenders",
                            "Irons & Steamers": "Clothing care",
                            "Air Fryers": "Healthy cooking",
                            "Microwaves": "Quick cooking",
                            "Coffee Machine": "Coffee makers",
                            "Mixers": "Food mixers",
                            "Food Processors": "Food preparation",
                            "Hand Blenders": "Portable blending",
                            "Waffle & Sandwich Makers": "Breakfast appliances",
                            "Ovens & Toasters": "Baking equipment",
                            "Vacuums & Floor Care": "Cleaning appliances",
                            "Juicers": "Juice extractors",
                            "Grills": "Indoor grilling",
                            "Rice Cookers": "Rice preparation"
                        }
                    },
                    "Large Appliances": {
                        "description": "Major home appliances",
                        "children": {
                            "Refrigerators": "Food storage",
                            "Freezers": "Frozen storage",
                            "Dishwashers": "Dish cleaning",
                            "Washers & Driers": "Laundry care",
                            "Cookers": "Cooking appliances",
                            "Cooktop": "Stovetop cooking",
                            "Range Hoods": "Kitchen ventilation"
                        }
                    },
                    "Cooling & Heating Appliances": {
                        "description": "Climate control appliances",
                        "children": {
                            "Air conditioners": "Room cooling",
                            "Household Fans": "Air circulation",
                            "Water Dispensers": "Water cooling",
                            "Water Heaters": "Water heating",
                            "Water Coolers & Filters": "Water purification"
                        }
                    }
                }
            },
            "Gaming": {
                "description": "Premium gaming equipment and accessories",
                "children": {
                    "Playstation 5": {
                        "description": "Latest PlayStation gaming",
                        "children": {
                            "Consoles": "PS5 gaming consoles",
                            "Games": "PS5 game titles",
                            "Controllers": "Gaming controllers",
                            "Cards": "Gift cards",
                            "Accessories": "PS5 add-ons"
                        }
                    },
                    "Playstation 4": {
                        "description": "PS4 gaming experience",
                        "children": {
                            "Games": "PS4 game titles",
                            "Controllers": "PS4 controllers",
                            "Cards": "Gift cards",
                            "Accessories": "PS4 add-ons"
                        }
                    },
                    "Xbox": {
                        "description": "Xbox gaming solutions",
                        "children": {
                            "Controllers": "Xbox controllers",
                            "Accessories": "Xbox add-ons"
                        }
                    },
                    "PC Gaming": {
                        "description": "Professional PC gaming",
                        "children": {
                            "Gaming Laptops": "High-performance laptops",
                            "Headsets": "Gaming audio",
                            "Keyboard": "Gaming keyboards",
                            "Mouse": "Gaming mice",
                            "Gaming Chairs": "Comfortable seating",
                            "Monitors": "Gaming displays"
                        }
                    },
                    "Card & Board Games": {
                        "description": "Classic gaming entertainment",
                        "children": {
                            "Card Games": "Traditional card games",
                            "Board Games": "Family board games"
                        }
                    }
                }
            }
        }

        # Create categories with proper hierarchy
        for main_cat_name, main_cat_data in categories_data.items():
            # Create main category
            main_slug = slugify(main_cat_name)
            main_cat, created = Category.objects.get_or_create(
                name=main_cat_name,
                defaults={
                    "slug": main_slug,
                    "is_active": True,
                    "description": main_cat_data["description"],
                    "image": "default.jpg"
                }
            )
            self.stdout.write(f"{'Created' if created else 'Found'} main category: {main_cat.name}")
            
            # Create subcategories
            for sub_cat_name, sub_cat_data in main_cat_data["children"].items():
                sub_slug = f"{main_slug}-{slugify(sub_cat_name)}"
                sub_cat, created = Category.objects.get_or_create(
                    name=sub_cat_name,
                    parent=main_cat,
                    defaults={
                        "slug": sub_slug,
                        "is_active": True,
                        "description": sub_cat_data["description"],
                        "image": "default.jpg"
                    }
                )
                self.stdout.write(f"  {'Created' if created else 'Found'} subcategory: {sub_cat.name}")

                # Create child categories
                for child_cat_name, child_cat_desc in sub_cat_data["children"].items():
                    child_slug = f"{sub_slug}-{slugify(child_cat_name)}"
                    child_cat, created = Category.objects.get_or_create(
                        name=child_cat_name,
                        parent=sub_cat,
                        defaults={
                            "slug": child_slug,
                            "is_active": True,
                            "description": child_cat_desc,
                            "image": "default.jpg"
                        }
                    )
                    self.stdout.write(f"    {'Created' if created else 'Found'} child category: {child_cat.name}")
    
    def create_brands(self):
        """Create brands with proper attributes"""
        brands_data = {
            "Electronics": [
                {"name": "Samsung Electronics", "image": "brand_images/samsung.jpg"},
                {"name": "Apple", "image": "brand_images/apple.jpg"},
                {"name": "Sony", "image": "brand_images/sony.jpg"},
                {"name": "LG Electronics", "image": "brand_images/lg.jpg"},
                {"name": "Xiaomi", "image": "brand_images/xiaomi.jpg"},
                {"name": "Huawei", "image": "brand_images/huawei.jpg"},
                {"name": "OnePlus", "image": "brand_images/oneplus.jpg"},
                {"name": "Google", "image": "brand_images/google.jpg"},
                {"name": "Microsoft", "image": "brand_images/microsoft.jpg"},
                {"name": "Asus", "image": "brand_images/asus.jpg"}
            ],
            "Fashion": [
                {"name": "Nike", "image": "brand_images/nike.jpg"},
                {"name": "Adidas", "image": "brand_images/adidas.jpg"},
                {"name": "Zara", "image": "brand_images/zara.jpg"},
                {"name": "H&M", "image": "brand_images/hm.jpg"},
                {"name": "Gucci", "image": "brand_images/gucci.jpg"},
                {"name": "Puma", "image": "brand_images/puma.jpg"},
                {"name": "Under Armour", "image": "brand_images/underarmour.jpg"},
                {"name": "Levi's", "image": "brand_images/levis.jpg"},
                {"name": "Calvin Klein", "image": "brand_images/calvinklein.jpg"},
                {"name": "Ralph Lauren", "image": "brand_images/ralphlauren.jpg"}
            ],
            "Home & Kitchen": [
                {"name": "IKEA", "image": "brand_images/ikea.jpg"},
                {"name": "Bosch", "image": "brand_images/bosch.jpg"},
                {"name": "Philips", "image": "brand_images/philips.jpg"},
                {"name": "Dyson", "image": "brand_images/dyson.jpg"},
                {"name": "KitchenAid", "image": "brand_images/kitchenaid.jpg"},
                {"name": "Whirlpool", "image": "brand_images/whirlpool.jpg"},
                {"name": "Samsung Home", "image": "brand_images/samsung.jpg"},
                {"name": "LG Home", "image": "brand_images/lg.jpg"},
                {"name": "Panasonic", "image": "brand_images/panasonic.jpg"},
                {"name": "Sharp", "image": "brand_images/sharp.jpg"}
            ],
            "Beauty & Personal Care": [
                {"name": "L'Oreal", "image": "brand_images/loreal.jpg"},
                {"name": "Maybelline", "image": "brand_images/maybelline.jpg"},
                {"name": "MAC", "image": "brand_images/mac.jpg"},
                {"name": "Nivea", "image": "brand_images/nivea.jpg"},
                {"name": "Dove", "image": "brand_images/dove.jpg"},
                {"name": "Garnier", "image": "brand_images/garnier.jpg"},
                {"name": "Neutrogena", "image": "brand_images/neutrogena.jpg"},
                {"name": "Revlon", "image": "brand_images/revlon.jpg"},
                {"name": "Clinique", "image": "brand_images/clinique.jpg"},
                {"name": "Estee Lauder", "image": "brand_images/esteelauder.jpg"}
            ],
            "Sports & Outdoors": [
                {"name": "Nike Sports", "image": "brand_images/nike.jpg"},
                {"name": "Adidas Sports", "image": "brand_images/adidas.jpg"},
                {"name": "Under Armour Sports", "image": "brand_images/underarmour.jpg"},
                {"name": "Puma Sports", "image": "brand_images/puma.jpg"},
                {"name": "Reebok", "image": "brand_images/reebok.jpg"},
                {"name": "New Balance", "image": "brand_images/newbalance.jpg"},
                {"name": "The North Face", "image": "brand_images/thenorthface.jpg"},
                {"name": "Columbia", "image": "brand_images/columbia.jpg"},
                {"name": "Asics", "image": "brand_images/asics.jpg"},
                {"name": "Mizuno", "image": "brand_images/mizuno.jpg"}
            ],
            "Gaming": [
                {"name": "Sony Gaming", "image": "brand_images/sony.jpg"},
                {"name": "Microsoft Gaming", "image": "brand_images/microsoft.jpg"},
                {"name": "Nintendo", "image": "brand_images/nintendo.jpg"},
                {"name": "Razer", "image": "brand_images/razer.jpg"},
                {"name": "Logitech", "image": "brand_images/logitech.jpg"},
                {"name": "SteelSeries", "image": "brand_images/steelseries.jpg"},
                {"name": "Corsair", "image": "brand_images/corsair.jpg"},
                {"name": "ASUS ROG", "image": "brand_images/asusrog.jpg"},
                {"name": "Alienware", "image": "brand_images/alienware.jpg"},
                {"name": "HyperX", "image": "brand_images/hyperx.jpg"}
            ],
            "Baby Products": [
                {"name": "Pampers", "image": "brand_images/pampers.jpg"},
                {"name": "Huggies", "image": "brand_images/huggies.jpg"},
                {"name": "Johnson & Johnson", "image": "brand_images/johnson.jpg"},
                {"name": "Gerber", "image": "brand_images/gerber.jpg"},
                {"name": "Fisher-Price", "image": "brand_images/fisherprice.jpg"},
                {"name": "Philips Avent", "image": "brand_images/philipsavent.jpg"},
                {"name": "MAM", "image": "brand_images/mam.jpg"},
                {"name": "NUK", "image": "brand_images/nuk.jpg"},
                {"name": "Chicco", "image": "brand_images/chicco.jpg"},
                {"name": "Graco", "image": "brand_images/graco.jpg"}
            ],
            "Computing": [
                {"name": "Dell", "image": "brand_images/dell.jpg"},
                {"name": "HP", "image": "brand_images/hp.jpg"},
                {"name": "Lenovo", "image": "brand_images/lenovo.jpg"},
                {"name": "ASUS Computing", "image": "brand_images/asus.jpg"},
                {"name": "Acer", "image": "brand_images/acer.jpg"},
                {"name": "MSI", "image": "brand_images/msi.jpg"},
                {"name": "Intel", "image": "brand_images/intel.jpg"},
                {"name": "AMD", "image": "brand_images/amd.jpg"},
                {"name": "Western Digital", "image": "brand_images/wd.jpg"},
                {"name": "Seagate", "image": "brand_images/seagate.jpg"}
            ],
            "Phones & Tablets": [
                {"name": "Apple Mobile", "image": "brand_images/apple.jpg"},
                {"name": "Samsung Mobile", "image": "brand_images/samsung.jpg"},
                {"name": "Xiaomi Mobile", "image": "brand_images/xiaomi.jpg"},
                {"name": "Huawei Mobile", "image": "brand_images/huawei.jpg"},
                {"name": "OnePlus Mobile", "image": "brand_images/oneplus.jpg"},
                {"name": "Google Mobile", "image": "brand_images/google.jpg"},
                {"name": "OPPO", "image": "brand_images/oppo.jpg"},
                {"name": "Vivo", "image": "brand_images/vivo.jpg"},
                {"name": "Realme", "image": "brand_images/realme.jpg"},
                {"name": "Nothing", "image": "brand_images/nothing.jpg"}
            ],
            "Appliances": [
                {"name": "Samsung Appliances", "image": "brand_images/samsung.jpg"},
                {"name": "LG Appliances", "image": "brand_images/lg.jpg"},
                {"name": "Bosch Appliances", "image": "brand_images/bosch.jpg"},
                {"name": "Whirlpool", "image": "brand_images/whirlpool.jpg"},
                {"name": "Electrolux", "image": "brand_images/electrolux.jpg"},
                {"name": "Miele", "image": "brand_images/miele.jpg"},
                {"name": "Panasonic Appliances", "image": "brand_images/panasonic.jpg"},
                {"name": "Sharp Appliances", "image": "brand_images/sharp.jpg"},
                {"name": "Philips Appliances", "image": "brand_images/philips.jpg"},
                {"name": "Dyson Appliances", "image": "brand_images/dyson.jpg"}
            ]
        }

        # Create brands
        for category, brands in brands_data.items():
            for brand_data in brands:
                try:
                    # Try to get existing brand
                    brand = Brand.objects.get(name=brand_data["name"])
                    self.stdout.write(f"Found existing brand: {brand.name}")
                except Brand.DoesNotExist:
                    # Create new brand if it doesn't exist
                    brand = Brand(
                        name=brand_data["name"],
                        image="default.jpg"
                    )
                    brand.save()  # This will trigger the save() method and generate the slug
                    self.stdout.write(f"Created new brand: {brand.name}")
    
    def create_products(self):
        """Create products with realistic data for each leaf category (10 products per category)"""
        # Get all leaf categories (categories with no children)
        leaf_categories = []
        for category in Category.objects.all():
            if not category.children.exists():
                leaf_categories.append(category)
        
        self.stdout.write(f"Found {len(leaf_categories)} leaf categories")
        
        # Get all brands
        brands = Brand.objects.all()
        sizes = Size.objects.all()
        colors = Color.objects.all()
        
        # Product name adjectives and features for generating realistic names
        adjectives = ["Premium", "Professional", "Advanced", "Deluxe", "Ultimate", "Essential", "Classic", "Modern", 
                     "Elegant", "Smart", "Elite", "Superior", "Compact", "Lightweight", "Portable", "Digital"]
        
        features = ["Plus", "Pro", "Ultra", "Max", "Elite", "Series", "Edition", "Collection", "Line", 
                   "Signature", "Limited", "Special", "Enhanced", "Improved", "NextGen"]
        
        # Define category-brand mapping for more logical brand selection
        category_brand_mapping = {
            "Electronics": ["Samsung Electronics", "Apple", "Sony", "LG Electronics", "Xiaomi", "Huawei", "OnePlus", "Google", "Microsoft", "Asus"],
            "Fashion": ["Nike", "Adidas", "Zara", "H&M", "Gucci", "Puma", "Under Armour", "Levi's", "Calvin Klein", "Ralph Lauren"],
            "Home & Furniture": ["IKEA", "Bosch", "Philips", "Dyson", "KitchenAid", "Whirlpool", "Samsung Home", "LG Home", "Panasonic", "Sharp"],
            "Beauty & Personal Care": ["L'Oreal", "Maybelline", "MAC", "Nivea", "Dove", "Garnier", "Neutrogena", "Revlon", "Clinique", "Estee Lauder"],
            "Sports & Outdoors": ["Nike Sports", "Adidas Sports", "Under Armour Sports", "Puma Sports", "Reebok", "New Balance", "The North Face", "Columbia", "Asics", "Mizuno"],
            "Gaming": ["Sony Gaming", "Microsoft Gaming", "Nintendo", "Razer", "Logitech", "SteelSeries", "Corsair", "ASUS ROG", "Alienware", "HyperX"],
            "Baby Products": ["Pampers", "Huggies", "Johnson & Johnson", "Gerber", "Fisher-Price", "Philips Avent", "MAM", "NUK", "Chicco", "Graco"],
            "Computing": ["Dell", "HP", "Lenovo", "ASUS Computing", "Acer", "MSI", "Intel", "AMD", "Western Digital", "Seagate"],
            "Phones & Tablets": ["Apple Mobile", "Samsung Mobile", "Xiaomi Mobile", "Huawei Mobile", "OnePlus Mobile", "Google Mobile", "OPPO", "Vivo", "Realme", "Nothing"],
            "Appliances": ["Samsung Appliances", "LG Appliances", "Bosch Appliances", "Whirlpool", "Electrolux", "Miele", "Panasonic Appliances", "Sharp Appliances", "Philips Appliances", "Dyson Appliances"],
            "Health & Beauty": ["L'Oreal", "Maybelline", "MAC", "Nivea", "Dove", "Garnier", "Neutrogena", "Revlon", "Clinique", "Estee Lauder"],
            "Sporting Goods": ["Nike Sports", "Adidas Sports", "Under Armour Sports", "Puma Sports", "Reebok", "New Balance", "The North Face", "Columbia", "Asics", "Mizuno"],
            "Supermarket": ["Nestle", "Procter & Gamble", "Unilever", "Coca-Cola", "PepsiCo", "Kraft Heinz", "Kellogg's", "General Mills", "Mars", "Colgate-Palmolive"],
            "Televisions & Audio": ["Samsung Electronics", "LG Electronics", "Sony", "Panasonic", "Sharp", "Philips", "TCL", "Hisense", "Bose", "JBL"],
        }

        # Loop through each leaf category and create 10 products
        for category in leaf_categories:
            # Get the parent hierarchy to determine relevant brands
            current = category
            hierarchy = [current.name]
            while current.parent:
                current = current.parent
                hierarchy.append(current.name)
            
            # Get relevant brands for this category based on mapping
            relevant_brands = []
            
            # Find the most relevant parent category for mapping
            mapped_category = None
            for cat_name in hierarchy:
                for mapping_key in category_brand_mapping.keys():
                    if mapping_key.lower() in cat_name.lower() or cat_name.lower() in mapping_key.lower():
                        mapped_category = mapping_key
                        break
                if mapped_category:
                    break
            
            if mapped_category:
                # Get brands from mapping
                brand_names = category_brand_mapping[mapped_category]
                for brand_name in brand_names:
                    for brand in brands:
                        if brand_name.lower() in brand.name.lower():
                            relevant_brands.append(brand)
            
            if not relevant_brands:  # If no relevant brands found, use random brands
                relevant_brands = random.sample(list(brands), min(5, brands.count()))
            
            # Create 10 products for this category
            for i in range(1, 11):
                # Select a brand for this product
                brand = random.choice(relevant_brands)
                
                # Generate product name
                base_name = category.name
                if random.random() < 0.3:  # 30% chance to include brand in name
                    product_name = f"{brand.name} {random.choice(adjectives)} {base_name}"
                else:
                    product_name = f"{random.choice(adjectives)} {base_name} {random.choice(features)}"
                
                # Make the name unique with a model number/identifier
                if random.random() < 0.7:  # 70% chance to add a model number
                    model_series = random.choice(["A", "B", "C", "E", "G", "H", "J", "M", "P", "S", "X", "Z"])
                    model_number = random.randint(1, 9999)
                    product_name = f"{product_name} {model_series}{model_number}"
                
                # Generate SKU (unique identifier)
                sku_prefix = ''.join([word[0] for word in brand.name.split()[:2]]).upper()
                sku_middle = ''.join([word[0] for word in category.name.split()[:2]]).upper()
                sku_suffix = f"{random.randint(1000, 9999)}"
                sku = f"{sku_prefix}-{sku_middle}-{sku_suffix}"
                
                # Generate price based on category depth (deeper categories are more specialized products)
                depth = 0
                temp_cat = category
                while temp_cat.parent:
                    depth += 1
                    temp_cat = temp_cat.parent
                
                base_price = random.uniform(50, 100) * (depth + 1)
                price = round(base_price * (1 + random.uniform(-0.1, 0.2)), 2)  # Vary by ±10-20%
                
                # Add sale price to some products (40% chance)
                sale_price = None
                sale_start_date = None
                sale_end_date = None
                
                if random.random() < 0.4:  # 40% chance for sale
                    discount = random.uniform(0.05, 0.7)  # 5-70% discount
                    sale_price = round(price * (1 - discount), 2)
                    
                    # Set sale period (between now and 30 days in future)
                    now = timezone.now()
                    sale_start_date = now - timedelta(days=random.randint(0, 15))
                    sale_end_date = now + timedelta(days=random.randint(5, 30))
                
                # Generate stock quantity
                if "Limited" in product_name:
                    stock_quantity = random.randint(1, 10)
                else:
                    stock_quantity = random.randint(10, 100)
                
                # Generate description
                description = self.generate_product_description(category, product_name, brand)
                
                # Generate specifications based on category
                specifications = self.generate_product_specifications(category, product_name)
                
                # Determine if product is featured (10% chance)
                is_featured = random.random() < 0.1
                
                # Determine if product is sponsored (5% chance)
                is_sponsored = random.random() < 0.05
                
                # Generate physical dimensions (50% chance)
                weight = None
                length = None
                width = None
                height = None
                
                if random.random() < 0.5:
                    weight = round(random.uniform(0.1, 10.0), 2)
                    length = round(random.uniform(10, 100), 2)
                    width = round(random.uniform(10, 100), 2)
                    height = round(random.uniform(5, 50), 2)
                
                # Generate ratings data
                rating_average = round(random.uniform(3.5, 5.0), 1)
                rating_count = random.randint(0, 1000)
                
                # Generate quantity sold based on rating count
                quantity_sold = int(rating_count * random.uniform(1.0, 3.0))
                
                # Set material for applicable categories
                material = ""
                if any(word in category.name.lower() for word in ["shirt", "dress", "clothing", "fabric", "wear", "apparel", "fashion"]):
                    materials = ["Cotton", "Polyester", "Wool", "Silk", "Linen", "Leather", "Denim", "Nylon", "Spandex", "Cashmere"]
                    material = random.choice(materials)
                elif any(word in category.name.lower() for word in ["furniture", "sofa", "chair", "table", "bed"]):
                    materials = ["Wood", "Metal", "Glass", "Plastic", "Fabric", "Leather", "Bamboo", "Rattan", "MDF", "Particleboard"]
                    material = random.choice(materials)
                
                # Generate meta data for SEO
                meta_title = product_name[:199]  # Ensure within 200 char limit
                meta_description = f"Buy {product_name} online. {description[:200]}..."
                meta_keywords = f"{brand.name}, {category.name}, {', '.join(product_name.split()[:5])}"
                
                # Set a realistic launch date (between 3 years ago and now)
                now = timezone.now()
                launched_at = now - timedelta(days=random.randint(0, 1095))  # Up to 3 years ago
                
                try:
                    # Create the product
                    product = Product.objects.create(
                        name=product_name,
                        slug=slugify(f"{product_name}-{sku}"),
                        sku=sku,
                        description=description,
                        category=category,
                        brand=brand,
                        price=price,
                        sale_price=sale_price,
                        sale_start_date=sale_start_date,
                        sale_end_date=sale_end_date,
                        stock_quantity=stock_quantity,
                        quantity_sold=quantity_sold,
                        track_inventory=True,
                        allow_backorder=random.random() < 0.2,  # 20% chance to allow backorders
                        weight=weight,
                        length=length,
                        width=width,
                        height=height,
                        is_featured=is_featured,
                        is_sponsored=is_sponsored,
                        meta_title=meta_title,
                        meta_description=meta_description,
                        meta_keywords=meta_keywords,
                        specifications=specifications,
                        rating_average=rating_average,
                        rating_count=rating_count,
                        material=material,
                        launched_at=launched_at
                    )
                    
                    # Add sizes if applicable to this category
                    if any(word in category.name.lower() for word in ["clothing", "apparel", "wear", "shirt", "dress", "pants", "shoes"]):
                        # For clothing, add appropriate sizes
                        selected_sizes = random.sample(list(sizes), min(random.randint(4, 7), len(sizes)))
                        product.sizes.add(*selected_sizes)
                    
                    # Add colors to all products
                    selected_colors = random.sample(list(colors), min(random.randint(1, 5), len(colors)))
                    product.colors.add(*selected_colors)
                    
                    # Create primary product image using default image
                    ProductImage.objects.create(
                        product=product,
                        image="default.jpg",
                        alt_text=f"{product_name} - Main Image",
                        is_primary=True,
                        order=0
                    )
                    
                    # Add 1-3 additional product images (30% chance)
                    if random.random() < 0.3:
                        for j in range(1, random.randint(2, 4)):
                            ProductImage.objects.create(
                                product=product,
                                image="default.jpg",
                                alt_text=f"{product_name} - Additional Image {j}",
                                is_primary=False,
                                order=j
                            )
                    
                    self.stdout.write(f"Created product {i}/10 for category '{category.name}': {product.name}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating product for '{category.name}': {str(e)}"))
                    continue
            
            self.stdout.write(self.style.SUCCESS(f"Created products for '{category.name}'"))
        
        self.stdout.write(self.style.SUCCESS(f"Created products for all {len(leaf_categories)} leaf categories"))
    
    def generate_product_description(self, category, product_name, brand):
        """Generate a realistic product description based on category and product"""
        # Get category hierarchy to determine the product type
        main_category = category
        while main_category.parent:
            main_category = main_category.parent
        
        # Define opening statements
        openings = [
            f"Introducing the {product_name}, a premium offering from {brand.name}.",
            f"Experience unparalleled quality with the {product_name} by {brand.name}.",
            f"The {product_name} represents {brand.name}'s commitment to excellence.",
            f"Discover the exceptional features of the {brand.name} {product_name}.",
            f"Meet the {product_name}, the latest innovation from {brand.name}."
        ]
        
        # Define category-specific feature highlights
        features = {
            "Electronics": [
                "advanced technology", "intuitive interface", "stunning display", 
                "lightning-fast performance", "intelligent design", "wireless connectivity",
                "long battery life", "immersive experience", "superior sound quality"
            ],
            "Fashion": [
                "premium materials", "elegant design", "comfortable fit", "timeless style", 
                "durable construction", "versatile options", "attention to detail", 
                "contemporary aesthetics", "perfect for any occasion"
            ],
            "Home & Furniture": [
                "exceptional comfort", "sturdy construction", "elegant design", 
                "space-saving features", "premium materials", "easy assembly", 
                "versatile functionality", "timeless appeal", "perfect dimensions"
            ],
            "Beauty & Personal Care": [
                "gentle formula", "natural ingredients", "long-lasting effects", 
                "dermatologically tested", "suitable for all skin types", "refreshing scent", 
                "eco-friendly packaging", "visible results", "luxurious experience"
            ],
            "Sports & Outdoors": [
                "durable construction", "weather-resistant materials", "ergonomic design", 
                "lightweight build", "high performance", "versatile functionality", 
                "professional-grade quality", "enhanced stability", "improved comfort"
            ],
            "Gaming": [
                "immersive experience", "responsive controls", "stunning graphics", 
                "seamless gameplay", "customizable features", "competitive edge", 
                "high-resolution display", "enhanced audio", "tactile feedback"
            ],
            "Baby Products": [
                "gentle materials", "safety-first design", "easy cleaning", 
                "comfortable for baby", "adjustable features", "practical for parents", 
                "BPA-free construction", "adorable design", "developmental benefits"
            ],
            "Phones & Tablets": [
                "crystal-clear display", "powerful processor", "all-day battery life", 
                "stunning camera system", "sleek design", "fast charging", 
                "expanded storage", "enhanced security", "seamless connectivity"
            ],
            "Appliances": [
                "energy-efficient operation", "quiet performance", "intuitive controls", 
                "spacious capacity", "sleek design", "durable construction", 
                "advanced technology", "time-saving features", "easy maintenance"
            ]
        }
        
        # Define benefits statements
        benefits = [
            "Designed to enhance your daily experience with its exceptional quality and performance.",
            "Combines style and functionality to deliver an outstanding user experience every time.",
            "Perfect for those who appreciate attention to detail and superior craftsmanship.",
            "An excellent choice for discerning customers who demand the very best.",
            "Created with your needs in mind, offering the perfect balance of form and function."
        ]
        
        # Define concluding statements
        conclusions = [
            f"Order your {product_name} today and discover why {brand.name} is a leader in {main_category.name.lower()}.",
            f"Elevate your experience with the {product_name} – the smart choice for quality and value.",
            f"Don't miss out on the exceptional quality of the {product_name}, available now for a limited time.",
            f"Make the {product_name} part of your collection and experience the {brand.name} difference.",
            f"Invest in quality with the {product_name} and enjoy years of reliable performance."
        ]
        
        # Get relevant features for this category
        category_features = features.get(main_category.name, features["Electronics"])
        
        # Select random elements to build the description
        opening = random.choice(openings)
        feature_list = random.sample(category_features, min(4, len(category_features)))
        feature_text = f"This exceptional product offers {', '.join(feature_list[:-1])}, and {feature_list[-1]}."
        benefit = random.choice(benefits)
        conclusion = random.choice(conclusions)
        
        # Combine elements into a coherent description
        description = f"{opening} {feature_text} {benefit} {conclusion}"
        
        return description
    
    def generate_product_specifications(self, category, product_name):
        """Generate realistic product specifications based on category"""
        specs = {
            "Model": f"{product_name.split()[-1] if len(product_name.split()) > 1 else 'Standard'}",
            "Warranty": f"{random.choice([1, 2, 3, 5])} years",
            "Country of Origin": random.choice(["China", "USA", "Japan", "Germany", "South Korea", "Vietnam", "Malaysia", "India", "Taiwan", "Thailand"]),
        }
        
        # Get category hierarchy
        main_category = category
        while main_category.parent:
            main_category = main_category.parent
            
        # Add category-specific specifications
        if "Electronics" in main_category.name or "Phone" in category.name or "Tablet" in category.name or "Computer" in category.name:
            specs.update({
                "Display": f"{random.choice(['5.5', '6.1', '6.7', '7.0', '10.2', '11', '12.9', '13.3', '14', '15.6', '17', '24', '27', '32', '43', '50', '55', '65'])} inch {random.choice(['LCD', 'LED', 'OLED', 'AMOLED', 'IPS', 'Retina', 'Super Retina XDR', 'Dynamic AMOLED', 'QLED'])}",
                "Processor": random.choice(["Snapdragon 8 Gen 2", "Apple A17 Pro", "MediaTek Dimensity 9000", "Exynos 2200", "Intel Core i7", "AMD Ryzen 9", "Apple M2", "Intel Core i9", "Qualcomm Snapdragon 888"]),
                "RAM": f"{random.choice(['4', '6', '8', '12', '16', '32', '64'])} GB",
                "Storage": f"{random.choice(['64', '128', '256', '512', '1', '2'])} {random.choice(['GB', 'GB', 'GB', 'GB', 'TB', 'TB'])}",
                "Battery": f"{random.randint(2000, 6000)} mAh" if "Phone" in category.name else f"{random.randint(5000, 12000)} mAh",
                "Operating System": random.choice(["Android 14", "iOS 17", "Windows 11", "macOS Sonoma", "iPadOS 17", "Chrome OS", "Linux"])
            })
            
        elif "Fashion" in main_category.name or "Clothing" in category.name or "Wear" in category.name:
            specs.update({
                "Material": random.choice(["Cotton", "Polyester", "Wool", "Silk", "Linen", "Leather", "Denim", "Nylon", "Spandex", "Cashmere"]),
                "Care Instructions": random.choice(["Machine wash cold", "Hand wash only", "Dry clean only", "Tumble dry low", "Wash with similar colors", "Do not bleach"]),
                "Fit": random.choice(["Regular", "Slim", "Relaxed", "Oversized", "Athletic", "Tailored", "Loose", "Skinny", "Straight"]),
                "Occasion": random.choice(["Casual", "Formal", "Business", "Sports", "Evening", "Beach", "Outdoor", "Everyday", "Special events"]),
                "Season": random.choice(["All seasons", "Summer", "Winter", "Spring/Fall", "Rainy season"])
            })
            
        elif "Furniture" in main_category.name or "Home" in category.name:
            specs.update({
                "Material": random.choice(["Wood", "Metal", "Glass", "Plastic", "Fabric", "Leather", "Bamboo", "Rattan", "MDF", "Particleboard"]),
                "Dimensions": f"{random.randint(50, 250)}L x {random.randint(50, 150)}W x {random.randint(40, 120)}H cm",
                "Weight Capacity": f"{random.randint(100, 300)} kg",
                "Assembly Required": random.choice(["Yes", "No", "Partial"]),
                "Style": random.choice(["Modern", "Contemporary", "Traditional", "Scandinavian", "Industrial", "Bohemian", "Mid-Century", "Rustic", "Minimalist"]),
                "Color/Finish": random.choice(["Natural wood", "White", "Black", "Gray", "Brown", "Walnut", "Oak", "Cherry", "Espresso", "Beige"])
            })
            
        elif "Beauty" in main_category.name or "Care" in category.name:
            specs.update({
                "Ingredients": "Water, Glycerin, Fragrance, " + ", ".join(random.sample(["Aloe Vera Extract", "Vitamin E", "Retinol", "Hyaluronic Acid", "Ceramides", "Shea Butter", "Niacinamide", "Salicylic Acid", "Peptides", "Collagen"], 3)),
                "Skin Type": random.choice(["All skin types", "Dry", "Oily", "Combination", "Sensitive", "Normal", "Mature"]),
                "Benefits": ", ".join(random.sample(["Moisturizing", "Anti-aging", "Brightening", "Exfoliating", "Soothing", "Calming", "Hydrating", "Firming", "Mattifying"], 2)),
                "Application": random.choice(["Apply daily", "Use morning and night", "Use as needed", "Apply to damp skin", "Massage gently", "Apply liberally"]),
                "Volume/Weight": f"{random.choice(['30', '50', '100', '150', '200', '250', '500'])} {random.choice(['ml', 'g'])}"
            })
            
        elif "Sports" in main_category.name or "Fitness" in category.name:
            specs.update({
                "Material": random.choice(["Nylon", "Polyester", "Spandex", "Cotton blend", "Neoprene", "Rubber", "Aluminum", "Steel", "Carbon fiber"]),
                "Weight": f"{random.randint(1, 30)} kg" if "Equipment" in category.name else f"{random.randint(100, 500)} g",
                "Features": ", ".join(random.sample(["Adjustable resistance", "Easy grip", "Non-slip surface", "Compact design", "Portable", "Water resistant", "Shock absorption", "Breathable", "Lightweight"], 3)),
                "Recommended For": random.choice(["Beginners", "Intermediate", "Advanced", "Professional", "All levels"]),
                "Usage": random.choice(["Indoor", "Outdoor", "Both indoor and outdoor", "Gym", "Home workouts", "Professional training"])
            })
            
        elif "Gaming" in main_category.name:
            specs.update({
                "Platform": random.choice(["PlayStation 5", "PlayStation 4", "Xbox Series X", "Xbox One", "Nintendo Switch", "PC", "Multiple platforms"]),
                "Genre": random.choice(["Action", "Adventure", "RPG", "FPS", "Strategy", "Simulation", "Sports", "Racing", "Puzzle", "Horror"]),
                "Players": random.choice(["Single player", "Multiplayer", "1-2 players local", "2-4 players local", "Online multiplayer", "1-8 players online"]),
                "Age Rating": random.choice(["E (Everyone)", "E10+ (Everyone 10+)", "T (Teen)", "M (Mature)", "A (Adult)"]),
                "Release Date": f"{random.choice(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])} {random.randint(2018, 2023)}"
            })
            
        elif "Baby" in main_category.name:
            specs.update({
                "Age Range": random.choice(["0-3 months", "3-6 months", "6-12 months", "1-2 years", "2-3 years", "3-5 years", "All ages"]),
                "Material": random.choice(["BPA-free plastic", "Cotton", "Silicone", "Wood", "Polyester", "Bamboo fiber", "Organic cotton"]),
                "Safety Features": ", ".join(random.sample(["Non-toxic", "Phthalate-free", "Choking hazard tested", "Anti-slip", "Hypoallergenic", "Lead-free", "Flame resistant"], 2)),
                "Care Instructions": random.choice(["Machine washable", "Hand wash only", "Wipe clean", "Dishwasher safe", "Sterilizer safe"]),
                "Certification": random.choice(["ASTM Certified", "CPSC Compliant", "EN71 Certified", "CE Certified", "FDA Approved"])
            })
            
        elif "Appliances" in main_category.name:
            specs.update({
                "Power": f"{random.randint(500, 3000)} W",
                "Capacity": f"{random.randint(1, 30)} L" if "Kitchen" in category.name else f"{random.randint(5, 500)} L",
                "Energy Efficiency": random.choice(["A+++", "A++", "A+", "A", "B", "Energy Star Certified"]),
                "Control Type": random.choice(["Digital", "Manual", "Touch", "Remote", "Smart (app-controlled)", "Voice-controlled"]),
                "Dimensions": f"{random.randint(30, 100)}L x {random.randint(30, 80)}W x {random.randint(30, 180)}H cm",
                "Features": ", ".join(random.sample(["Timer", "Auto shut-off", "Multiple settings", "LCD display", "Quiet operation", "Quick start", "Child lock", "Memory function"], 3))
            })
            
        # Add random additional specification based on product name keywords
        product_words = product_name.lower().split()
        
        if any(tech in product_words for tech in ["smart", "digital", "electronic", "tech", "wireless"]):
            specs["Connectivity"] = ", ".join(random.sample(["Bluetooth", "Wi-Fi", "NFC", "USB-C", "Lightning", "HDMI"], min(3, random.randint(1, 3))))
            
        if any(premium in product_words for premium in ["premium", "deluxe", "elite", "professional", "pro"]):
            specs["Special Features"] = ", ".join(random.sample(["Premium finish", "Exclusive design", "Professional grade", "Enhanced durability", "Lifetime support"], min(2, random.randint(1, 2))))
            
        if any(eco in product_words for eco in ["eco", "green", "sustainable", "natural", "organic"]):
            specs["Eco-Friendly"] = ", ".join(random.sample(["Recycled materials", "Sustainable production", "Energy efficient", "Reduced packaging", "Carbon neutral"], min(2, random.randint(1, 2))))
            
        return specs
    
    def create_flash_sales(self):
        """Create flash sales with some products"""
        products = Product.objects.all()
        if not products.exists():
            self.stdout.write(self.style.WARNING("No products available for flash sales"))
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
        
        for i, sale_data in enumerate(flash_sales_data):
            start_time = timezone.now() + timedelta(hours=random.randint(0, 24))
            end_time = start_time + timedelta(hours=sale_data["duration_hours"])
            
            # Create unique slug by adding timestamp
            timestamp = int(timezone.now().timestamp())
            unique_slug = f"{slugify(sale_data['name'])}-{timestamp}-{i}"
            
            flash_sale = FlashSale.objects.create(
                name=sale_data["name"],
                slug=unique_slug,
                description=sale_data["description"],
                start_time=start_time,
                end_time=end_time,
                is_active=True
            )
            
            # Add 5-10 random products to the flash sale
            num_products = random.randint(5, min(10, products.count()))
            selected_products = random.sample(list(products), num_products)
            
            for product in selected_products:
                discount = random.randint(*sale_data["discount_range"])
                FlashSaleItem.objects.create(
                    flash_sale=flash_sale,
                    product=product,
                    discount_percentage=discount,
                    quantity_limit=random.randint(10, 50),
                    quantity_sold=random.randint(0, 10)
                )
            
            self.stdout.write(f"Created flash sale: {flash_sale.name} with {num_products} products")

# Execute the script when run directly
if __name__ == "__main__":
    populator = Command()
    populator.handle()

# for runnign the script 
# cd /media/king/16D8CD34D8CD1343/projects\ ITI/final-project/back-end/iti-final-django-jumia/
# DJANGO_SETTINGS_MODULE=itiproject.settings python itiproject/products/populate_database.py