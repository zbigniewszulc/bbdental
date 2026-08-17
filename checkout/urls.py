from django.urls import path

from . import views
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path(
        'checkout_success/<order_number>',
        views.checkout_success,
        name='checkout_success',
    ),
    path('wh/', webhook, name='wh'),
    path(
        'cache_checkout_data/',
        views.cache_checkout_data,
        name='cache_checkout_data',
    ),
    path('manage_orders/', views.manage_orders, name='manage_orders'),
    path(
        'manage_orders/<order_number>/',
        views.order_management_details,
        name='order_management_details',
    ),
]
