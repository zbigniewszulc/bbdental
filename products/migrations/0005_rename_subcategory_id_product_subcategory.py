# Generated by Django 5.1.5 on 2025-03-31 22:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_rename_manufacturer_id_product_manufacturer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='subcategory_id',
            new_name='subcategory',
        ),
    ]
