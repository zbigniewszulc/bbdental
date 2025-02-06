from django.contrib import admin
from .models import CatGroup, Category, Manufacturer, Product

# Register your models here.


class CatGroupAdmin(admin.ModelAdmin):
    list_display = (
        'group_name',
        'group_vat',
        'group_pic_loc',
    )
    ordering = ('group_name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'category_name',
        'group_id',
    )
    ordering = ('category_name',)


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = (
        'manufacturer_name',
    )
    ordering = ('manufacturer_name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'description',
        'category_id',
        'manufacturer_id',
        'price',
        'in_stock',
    )
    ordering = ('product_name',)


admin.site.register(CatGroup, CatGroupAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Product, ProductAdmin)
