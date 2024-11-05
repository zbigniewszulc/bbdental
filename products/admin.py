from django.contrib import admin
from .models import CatGroup, Category, Manufacturer, Product

# Register your models here.
admin.site.register(CatGroup)
admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Product)