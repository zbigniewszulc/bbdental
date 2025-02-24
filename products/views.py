from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Subcategory, Manufacturer
from .forms import ProductForm

# Create your views here.


def get_sorted_filtered(request, queryset):
    """
    Utility function to sort products based on provided queryset
    """
    # Get sorting parameters with default values
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')
    manufacturer_filter = request.GET.get('manufacturer', '')
    query = request.GET.get('q', '')

    sort_mapping = {
        'name': 'lower_product_name',
        'manufacturer': 'lower_manufacturer_name',
        'price': 'price'
    }
    # Default sorting - lower_product_name
    sortkey = sort_mapping.get(sort, 'lower_product_name')

    if direction == 'desc':
        sortkey = f'-{sortkey}'

    # If query exists apply this filter
    if query:
        queryset = queryset.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query)
        )

    # Apply manufacturer filter (if selected)
    # iexact -> case-insensitive match
    if manufacturer_filter:
        queryset = queryset.filter(
            manufacturer_id__manufacturer_name__iexact=manufacturer_filter)

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


def get_manufacturers(products):
    """
    Utility function to fetch all manufacturers based on product
    """
    manufacturers = (
        Manufacturer.objects
        .filter(manufacturer_products__in=products)
        # distinct() removes duplicate records
        .distinct()
        .annotate(lower_manufacturer_name=Lower('manufacturer_name'))
        .order_by('lower_manufacturer_name')
    )
    return manufacturers


def all_products(request):
    """
    A view to render all products page.
    Display all :model:`products.Product` with filtering and sorting

    **Context**

    ``categories``
        A queryset of all :model:`products.Category`, used for menu display.
    ``manufacturers`` A queryset of all :model:`products.Manufacturer`
        used for filtering
    ``page_obj``
        A paginated queryset of :model:`products.Product`.
    ``sort``
        Selected sorting criteria.
    ``direction``
        Selected sorting direction.
    ``selected_manufacturer``
        Selected manufacturer for filtering.
    ``query``
        Search query entered by user.

    **Template**
    :template:`products/products.html`.
    """
    # select_related and prefetch_related used to solve database query
    # performance issues
    query = None
    products = (
        Product.objects
        .annotate(
            lower_product_name=Lower('product_name'),
            lower_manufacturer_name=Lower('manufacturer_id__manufacturer_name')
        )
        .select_related('subcategory_id', 'manufacturer_id')
    )
    # Get search query entered by user from URL
    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.warning(
                    request,
                    'Search field empty. Showing all products.'
                )
                return redirect(reverse('all_products'))
            queries = Q(product_name__icontains=query) | Q(
                description__icontains=query)
            products = products.filter(queries)

    products = get_sorted_filtered(request, products)
    page_obj = get_paginated(request, products)

    context = {
        'categories': get_categories(),
        'manufacturers': get_manufacturers(products),
        'page_obj': page_obj,
        'sort': request.GET.get('sort', 'name'),
        'direction': request.GET.get('direction', 'asc'),
        'selected_manufacturer': request.GET.get('manufacturer', ''),
        'query': query
    }

    return render(request, 'products/products.html', context)


def product_details(request, product_id):
    """
    A view to show idyvidual product details.
    Display information about :model:`products.Product`

    **Context**

    ``product``
        An instance of :model:`products.Product`

    **Template**
    :template:`products/product_details.html`
    """
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_details.html', context)


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
    ``manufacturers`` A queryset of :model:`products.Manufacturer`
        used for filtering
    ``page_obj``
        A paginated queryset of :model:`products.Product` filtered by category.
    ``sort``
        Selected sorting criteria.
    ``direction``
        Selected sorting direction.
    ``selected_manufacturer``
        Selected manufacturer for filtering.

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
    products = get_sorted_filtered(request, products)
    page_obj = get_paginated(request, products)

    context = {
        'category': category,
        'categories': get_categories(),
        'manufacturers': get_manufacturers(products),
        'page_obj': page_obj,
        'sort': request.GET.get('sort', 'name'),
        'direction': request.GET.get('direction', 'asc'),
        'selected_manufacturer': request.GET.get('manufacturer', '')
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
    `manufacturers`` A queryset of :model:`products.Manufacturer`
        used for filtering
    ``page_obj``
        Paginated queryset of :model:`products.Product` filtered by subcategory
    ``sort``
        Selected sorting criteria.
    ``direction``
        Selected sorting direction.
    ``selected_manufacturer``
        Selected manufacturer for filtering.

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
    products = get_sorted_filtered(request, products)
    page_obj = get_paginated(request, products)

    context = {
        'category': category,
        'subcategory': subcategory,
        'categories': get_categories(),
        'manufacturers': get_manufacturers(products),
        'page_obj': page_obj,
        'sort': request.GET.get('sort', 'name'),
        'direction': request.GET.get('direction', 'asc'),
        'selected_manufacturer': request.GET.get('manufacturer', '')
    }

    return render(request, 'products/products.html', context)


def products_menu(request):
    """ A view to render products menu """
    return render(request, 'products/products_menu.html')


def manage_products(request):
    """
    Display all :model:`products.Product` with sorting and filtering

    **Context**

    ``manufacturers``
        A list of all available manufacturers to filter the products by.
    ``selected_manufacturer``
        The manufacturer currently selected for filtering.
    ``sort``
        Selected sorting method (e.g., name, price, or manufacturer).
    ``direction``
        The direction of sorting, either ascending or descending.
    ``page_obj``
        A paginated list of products

    **Template**

    :template:`products/product_management.html`.
    """
    products = Product.objects.annotate(
        lower_product_name=Lower('product_name'),
        lower_manufacturer_name=Lower('manufacturer_id__manufacturer_name')
    ).select_related('subcategory_id', 'manufacturer_id')

    products = get_sorted_filtered(request, products)

    page_obj = get_paginated(request, products)

    context = {
        'manufacturers': get_manufacturers(products),
        'selected_manufacturer': request.GET.get('manufacturer', ''),
        'sort': request.GET.get('sort', 'name'),
        'direction': request.GET.get('direction', 'asc'),
        'page_obj': page_obj
    }
    return render(request, 'products/product_management.html', context)


def add_product(request):
    """
    Add new product to the database.

    **Context**

    ``form``
        A form used to add a new product

    **Template**

    :template:`products/product_add.html`.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('manage_products')
        else:
            messages.success(
                request, 
                'Unknown error occurred while adding the product'
            )
    else:
        form = ProductForm()

    context = {
        'form': form
    }
    return render(request, 'products/product_add.html', context)


def edit_product(request, product_id):
    """
    A view to edit an existing product details

    **Context**
    ``form``
        The form used to edit product.

    **Template**
    :template:`products/product_edit.html`.
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('edit_product', product_id=product.id)
        else:
            messages.error(
                request,
                'Error updating product. Please check the entered details'
            )
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'products/product_edit.html', context)
