from django.shortcuts import render, get_object_or_404
from .models import Product, Category

# Create your views here.


def all_products(request):
    """
    A view to render all roducts page.
    Display all :model:`products.Product`.

    **Context**

    ``products``
        An instance of :model:`products.Product`.

    **Template**

    :template:`products/products.html`.
    """

    products = Product.objects.all().order_by('product_name')
    categories = Category.objects.all().order_by('category_name')

    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'products/products.html', context)


def products_by_category(request, category_id):
    """ A view to display products filtered by category """
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(
        subcategory_id__category_id=category.id).order_by('product_name')
    categories = Category.objects.all().order_by('category_name')

    context = {
        'category': category,
        'products': products,
        'categories': categories
    }

    return render(request, 'products/products.html', context)


def products_menu(request):
    """ A view to render products menu """
    return render(request, 'products/products_menu.html')
