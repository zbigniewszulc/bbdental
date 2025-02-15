from django.shortcuts import render, get_object_or_404
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from .models import Product, Category, Subcategory


# Create your views here.


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
    # Fetch categories
    categories = Category.objects.prefetch_related('subcategories').annotate(
        lower_category_name=Lower('category_name')).order_by(
            'lower_category_name')

    # Get sorting parameters with default values
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')

    # Sorting
    if sort == 'name':
        sortkey = 'lower_product_name'
    elif sort == 'manufacturer':
        sortkey = 'lower_manufacturer_name'
    elif sort == 'price':
        sortkey = 'price'
    else:
        sortkey = 'lower_product_name'  # Default sorting

    if direction == 'desc':
        sortkey = f'-{sortkey}'

    products = products.order_by(sortkey)

    # Pagination: 20 products per page
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'page_obj': page_obj,
        'sort': sort,
        'direction': direction
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
    categories = (
        Category.objects
        .prefetch_related('subcategories')
        .annotate(lower_category_name=Lower('category_name'))
        .order_by('lower_category_name')
    )

    # Get sorting parameters with default values
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')

    # Sorting
    if sort == 'name':
        sortkey = 'lower_product_name'
    elif sort == 'manufacturer':
        sortkey = 'manufacturer_id'
    elif sort == 'price':
        sortkey = 'price'
    else:
        sortkey = 'lower_product_name'  # Default sorting

    if direction == 'desc':
        sortkey = f'-{sortkey}'

    products = products.order_by(sortkey)

    # Pagination: 20 products per page
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'sort': sort,
        'direction': direction
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
    categories = Category.objects.prefetch_related('subcategories').annotate(
        lower_category_name=Lower('category_name')).order_by(
            'lower_category_name')

    # Get sorting parameters with default values
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')

    # Sorting
    if sort == 'name':
        sortkey = 'lower_product_name'
    elif sort == 'manufacturer':
        sortkey = 'manufacturer_id'
    elif sort == 'price':
        sortkey = 'price'
    else:
        sortkey = 'lower_product_name'  # Default sorting

    if direction == 'desc':
        sortkey = f'-{sortkey}'

    products = products.order_by(sortkey)

    # Pagination: 20 products per page
    paginator = Paginator(products, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'subcategory': subcategory,
        'categories': categories,
        'page_obj': page_obj,      
        'sort': sort,
        'direction': direction
    }

    return render(request, 'products/products.html', context)


def products_menu(request):
    """ A view to render products menu """
    return render(request, 'products/products_menu.html')
