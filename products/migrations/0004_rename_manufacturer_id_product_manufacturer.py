# Generated by Django 5.1.5 on 2025-03-26 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_category_category_pic_loc_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='manufacturer_id',
            new_name='manufacturer',
        ),
    ]
