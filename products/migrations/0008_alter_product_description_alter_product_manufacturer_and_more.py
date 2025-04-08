# Generated by Django 5.1.5 on 2025-04-08 01:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_rename_category_id_subcategory_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(default='No describtion', max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='manufacturer',
            field=models.ForeignKey(default=52, on_delete=django.db.models.deletion.PROTECT, related_name='manufacturer_products', to='products.manufacturer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(default=23, on_delete=django.db.models.deletion.PROTECT, related_name='subcategory_products', to='products.subcategory'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(default=8, on_delete=django.db.models.deletion.PROTECT, related_name='subcategories', to='products.category'),
            preserve_default=False,
        ),
    ]
