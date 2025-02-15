from django.shortcuts import render, get_object_or_404
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from .models import Product, Category, Subcategory


# Create your views here.


def get_sorted(request, queryset):
    """
    Utility function to sort products based on provided queryset
    """
    # Get sorting parameters with default values
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')

    sort_mapping = {
        'name': 'lower_product_name',
        'manufacturer': 'lower_manufacturer_name',
        'price': 'price'
    }
    # Default sorting - lower_product_name
    sortkey = sort_mapping.get(sort, 'lower_product_name')

    if direction == 'desc':
        sortkey = f'-{sortkey}'

    sorted_queryset = queryset.order_by(sortkey)

    return sorted_queryset


def get_paginated(request, queryset, per_page=20):
    """
    Utility function to paginate queryset of products
    """
    # Pagination: 20 products per page
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def get_categories():
    """
    Utility function to fetch all categories
    """
    categories = (
        Category.objects
        .prefetch_related('subcategories')
        .annotate(lower_category_name=Lower('category_name'))
        .order_by('lower_category_name')
    )

    return categories


def all_products(request):
    """
    A view to render all products page.
    Display all :model:`products.Product`.

    **Context**

    ``categories``
        A queryset of all :model:`products.Category`, used for menu display.
    ``page_obj``
        A paginated queryset of :model:`products.Product`.
    ``sort``
        Selected sorting criteria.
    ``direction``
        Selected sorting direction.

    **Template**
    :template:`products/products.html`.
    """
    # select_related and prefetch_related used to solve database query
    # performance issues
    products = (
        Product.objects
        .annotate(
            lower_product_name=Lower('product_name'),
            lower_manufacturer_name=Lower('manufacturer_id__manufacturer_name')
        )
        .select_related('subcategory_id', 'manufacturer_id')
    )
    products = get_sorted(request, products)
    page_obj = get_paginated(request, products)

    context = {
        'categories': get_categories(),
        'page_obj': page_obj,
        'sort': request.GET.get('sort', 'name'),
        'direction': request.GET.get('direction', 'asc')
    }

    return render(request, 'products/products.html', context)


def products_by_category(request, category_id):
    """
    A view to display products filtered by category.
    Display all :model:`products.Product` that are
    filtered by :model:`products.Category`.

    **Context**

    ```category``
        An instance of :model:`products.Category`.
    ``categories``
        A queryset of all :model:`products.Category`, used for menu display.
    ``page_obj``
        A paginated queryset of :model:`products.Product` filtered by category.
    ``sort``
        Selected sorting criteria.
    ``direction``
        Selected sorting direction.

    **Template**
    :template:`products/products.html`.
    """
    # select_related used to solve databse query performance issue
    category = get_object_or_404(Category, id=category_id)
    products = (
        Product.objects
        .filter(subcategory_id__category_id=category.id)
        .annotate(
            lower_product_name=Lower('product_name'), 
            lower_manufacturer_name=Lower('manufacturer_id__manufacturer_name')
        )
        .select_related('subcategory_id', 'manufacturer_id')
    )
    products = get_sorted(request, products)
    page_obj = get_paginated(request, products)

    context = {
        'category': category,
        'categories': get_categories(),
        'page_obj': page_obj,
        'sort': request.GET.get('sort', 'name'),
        'direction': request.GET.get('direction', 'asc')
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
    ``categories``
        A queryset of all :model:`products.Category`, used for menu display.
    ``page_obj``
        Paginated queryset of :model:`products.Product` filtered by subcategory
    ``sort``
        Selected sorting criteria.
    ``direction``
        Selected sorting direction.

    **Template**

    :template:`products/products.html`.
    """
    # select_related used to solve databse query performacne issue
    category = get_object_or_404(Category, id=category_id)
    subcategory = get_object_or_404(
        Subcategory, id=subcategory_id, category_id=category)
    products = (
        Product.objects
        .filter(subcategory_id=subcategory)
        .annotate(
            lower_product_name=Lower('product_name'),
            lower_manufacturer_name=Lower('manufacturer_id__manufacturer_name')
        )
        .select_related('subcategory_id', 'manufacturer_id')
    )
    products = get_sorted(request, products)
    page_obj = get_paginated(request, products)

    context = {
        'category': category,
        'subcategory': subcategory,
        'categories': get_categories(),
        'page_obj': page_obj,      
        'sort': request.GET.get('sort', 'name'),
        'direction': request.GET.get('direction', 'asc')
    }

    return render(request, 'products/products.html', context)


def products_menu(request):
    """ A view to render products menu """
    return render(request, 'products/products_menu.html')
