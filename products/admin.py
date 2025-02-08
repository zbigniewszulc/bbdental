from django.contrib import admin
from .models import Category, Subcategory, Manufacturer, Product

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'category_name',
        'category_vat',
        'category_pic_loc',
    )
    ordering = ('category_name',)


class SubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        'subcategory_name',
        'category_id',
    )
    ordering = ('subcategory_name',)


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = (
        'manufacturer_name',
    )
    ordering = ('manufacturer_name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'description',
        'subcategory_id',
        'manufacturer_id',
        'price',
        'in_stock',
    )
    ordering = ('product_name',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
