from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.all_products, name='all_products'),
    path('<int:product_id>', views.product_details, name='product_details'),
    path('<int:category_id>/', views.products_by_category,
         name='products_by_category'),
    path('<int:category_id>/<int:subcategory_id>/',
         views.products_by_subcategory, name='products_by_subcategory'),
    path("manage/", views.manage_products, name='manage_products'),
    path("add/", views.add_product, name="add_product"),
    path("edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path("delete/<int:product_id>/", views.delete_product,
         name="delete_product")
]
