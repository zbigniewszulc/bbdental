from django.shortcuts import render
from .models import Product

# Create your views here.


def all_products(request):
    """
    A view to render all roducts page.
    Display all :model:`products.Product`.

    **Context**

    ``products``
        An instance of :model:`products.Product`.

    **Template**

    :template:`products/all_products.html`.
    """

    products = Product.objects.all().order_by('product_name')
    context = {
        'products': products
    }
    return render(request, 'products/all_products.html', context)


def products_menu(request):
    """ A view to render products menu """
    return render(request, 'products/products_menu.html')
