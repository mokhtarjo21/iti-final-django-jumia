# Generated by Django 5.1.7 on 2025-05-31 19:55

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Red', 'Red'), ('Blue', 'Blue'), ('Green', 'Green'), ('Black', 'Black'), ('White', 'White'), ('Yellow', 'Yellow'), ('Orange', 'Orange'), ('Purple', 'Purple'), ('Gray', 'Gray'), ('Brown', 'Brown')], max_length=20, unique=True)),
                ('slug', models.SlugField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='product_images/')),
                ('alt_text', models.CharField(blank=True, max_length=200)),
                ('is_primary', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='RecentlyViewedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-viewed_at'],
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], max_length=10, unique=True)),
                ('slug', models.SlugField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='brand_images/')),
            ],
            options={
                'ordering': ['name'],
                'indexes': [models.Index(fields=['slug'], name='products_br_slug_d4d839_idx')],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='category_images/')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(blank=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='products.category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='FlashSale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-start_time'],
                'indexes': [models.Index(fields=['start_time', 'end_time', 'is_active'], name='products_fl_start_t_2f3f8b_idx')],
            },
        ),
        migrations.CreateModel(
            name='FlashSaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('quantity_limit', models.IntegerField(default=0, help_text='0 for unlimited')),
                ('quantity_sold', models.IntegerField(default=0)),
                ('flash_sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='products.flashsale')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sku', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=500)),
                ('slug', models.SlugField(max_length=500, unique=True)),
                ('description', models.TextField()),
                ('specifications', models.JSONField(blank=True, default=dict)),
                ('price', models.DecimalField(decimal_places=2, help_text='Global/standard price', max_digits=10)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('sale_start_date', models.DateTimeField(blank=True, null=True)),
                ('sale_end_date', models.DateTimeField(blank=True, null=True)),
                ('stock_quantity', models.IntegerField(default=0)),
                ('quantity_sold', models.IntegerField(blank=True, default=0, null=True)),
                ('track_inventory', models.BooleanField(default=True)),
                ('allow_backorder', models.BooleanField(default=False)),
                ('weight', models.DecimalField(blank=True, decimal_places=3, help_text='Weight in KG', max_digits=10, null=True)),
                ('length', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_sponsored', models.BooleanField(default=False)),
                ('meta_title', models.CharField(blank=True, max_length=200)),
                ('meta_description', models.TextField(blank=True)),
                ('meta_keywords', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('launched_at', models.DateTimeField(blank=True, null=True)),
                ('rating_average', models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('rating_count', models.IntegerField(default=0)),
                ('material', models.CharField(blank=True, max_length=100)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.brand')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.category')),
                ('colors', models.ManyToManyField(blank=True, related_name='products', to='products.color')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
