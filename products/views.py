from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Subcategory
from django.core.paginator import Paginator

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
    # select_related and prefetch_related used to solve databse query
    # performance issue
    products = Product.objects.select_related(
        'subcategory_id', 'manufacturer_id').order_by('product_name')
    categories = Category.objects.prefetch_related(
        'subcategories').order_by('category_name')

    # Pagination: 20 products per page
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'page_obj': page_obj
    }
    return render(request, 'products/products.html', context)


def products_by_category(request, category_id):
    """
    A view to display products filtered by category.
    Display all :model:`products.Product` that are
    filtered by :model:`products.Category`.

    **Context**

    ``category``
        An instance of :model:`products.Category`.
    ``products``
        A queryset of :model:`products.Product` filtered by category.
    ``categories``
        A queryset of all :model:`products.Category`, used for menu display.

    **Template**

    :template:`products/products.html`.
    """
    # select_related used to solve databse query performance issue
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(
        subcategory_id__category_id=category.id).select_related(
            'subcategory_id', 'manufacturer_id').order_by('product_name')
    categories = Category.objects.all().order_by('category_name')

    # Pagination: 20 products per page
    paginator = Paginator(products, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'categories': categories,
        'page_obj': page_obj
    }

    return render(request, 'products/products.html', context)


def products_by_subcategory(request, category_id, subcategory_id):
    """
    A view to display products filtered by subcategory.
    Display all :model:`products.Product` that are
    filtered by :model:`products.Subcategory` and :model:`products.Category`.

    **Context**

    ``category``
        An instance of :model:`products.Category`.
    ``subcategory``
        An instance of :model:`products.Subcategory`.
    ``products``
        A queryset of :model:`products.Product` filtered by subcategory.
    ``categories``
        A queryset of all :model:`products.Category`, used for menu display.

    **Template**

    :template:`products/products.html`.
    """
    # select_related used to solve databse query performacne issue
    category = get_object_or_404(Category, id=category_id)
    subcategory = get_object_or_404(
        Subcategory, id=subcategory_id, category_id=category)
    products = Product.objects.filter(
        subcategory_id=subcategory).select_related(
        'subcategory_id', 'manufacturer_id').order_by('product_name')
    categories = Category.objects.all().order_by('category_name')

    # Pagination: 20 products per page
    paginator = Paginator(products, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'subcategory': subcategory,
        'categories': categories,
        'page_obj': page_obj
    }

    return render(request, 'products/products.html', context)


def products_menu(request):
    """ A view to render products menu """
    return render(request, 'products/products_menu.html')
