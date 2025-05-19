import tempfile
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Category, Brand, Product, Size, Color
from products.serializers import (
    CategoryListSerializer,
    BrandListSerializer,
    ProductListSerializer,
    ProductCreateUpdateSerializer
)

class SerializerTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Clothing", slug="clothing")
        self.brand = Brand.objects.create(name="Nike", slug="nike")
        self.size = Size.objects.create(name="M")
        self.color = Color.objects.create(name="Red")

        self.product = Product.objects.create(
            name="T-Shirt",
            slug="t-shirt",
            category=self.category,
            brand=self.brand,
            price=100,
            sale_price=80,
            stock_quantity=10,
            sku="TSH-001",
            description="A comfortable t-shirt"
        )
        self.product.sizes.add(self.size)
        self.product.colors.add(self.color)

    def test_category_list_serializer(self):
        serializer = CategoryListSerializer(instance=self.category)
        data = serializer.data
        self.assertEqual(data['name'], "Clothing")
        self.assertIn('product_count', data)

    def test_brand_list_serializer(self):
        serializer = BrandListSerializer(instance=self.brand)
        data = serializer.data
        self.assertEqual(data['name'], "Nike")
        self.assertEqual(data['product_count'], 1)

    def test_product_list_serializer(self):
        serializer = ProductListSerializer(instance=self.product)
        data = serializer.data
        self.assertEqual(data['name'], "T-Shirt")
        self.assertEqual(data['discount_percentage'], 20)

    def test_product_create_serializer(self):
        image_file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {
            "name": "Sneakers",
            "category": self.category.id,
            "brand_name": "Adidas",
            "price": 200,
            "sale_price": 150,
            "stock_quantity": 5,
            "description": "A comfortable pair of sneakers",
            "sku": "SNK-001",
            "images_data": [image_file],
            "sizes": [self.size.id],
            "colors": [self.color.id]
        }
        serializer = ProductCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.name, "Sneakers")
        self.assertEqual(product.brand.name, "Adidas")
        self.assertEqual(product.sizes.first().name, "M")
        self.assertEqual(product.colors.first().name, "Red")
