from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.all_products, name='all_products'),
    path('menu/', views.products_menu, name='products_menu')
]
