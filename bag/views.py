from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product

# Create your views here.


@login_required
def view_bag(request):
    """
    A view to render bag content page.

    **Template**

    :template:`bag/bag.html`.
    """

    return render(request, 'bag/bag.html')


@login_required
def add_to_bag(request, product_id):
    """
    Add particular product to the shopping bag
    """
    try:
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get('quantity'))
        redirect_url = request.POST.get('redirect_url')
        bag = request.session.get('bag', {})
        in_stock = product.in_stock

        # If the product already exists in the shopping bag
        if product_id in list(bag.keys()):
            new_quantity = bag[product_id] + quantity
            if new_quantity > in_stock:
                bag[product_id] = in_stock
                messages.warning(
                    request,
                    f'Only {in_stock} available. Added maximum '
                    'possible quantity.'
                )
            else:
                bag[product_id] = new_quantity
                messages.success(
                    request,
                    f'{product.product_name} has been added to '
                    'the shopping bag.'
                )
        # If it is a product which is not in the shopping bag yet
        else:
            if quantity > in_stock:
                bag[product_id] = in_stock
                messages.warning(
                    request,
                    f'Only {in_stock} available. Added maximum '
                    'possible quantity.'
                )
            else:
                bag[product_id] = quantity
                messages.success(
                    request,
                    f'{product.product_name} has been added '
                    'to the shopping bag.'
                )

        request.session['bag'] = bag

    except Exception as e:
        messages.error(request, f'Error occurred: {e}')

    return redirect(redirect_url)


@login_required
def update_bag(request):
    """
    Update quantity of product in the shopping bag or remove it.
    """
    if request.method == "POST":
        try:
            product_id = request.POST.get("product_id")
            quantity = int(request.POST.get("quantity", 1))
            product = get_object_or_404(Product, pk=product_id)

            bag = request.session.get("bag", {})

            if quantity > 0:
                bag[product_id] = quantity  # Update quantity
                messages.success(
                    request,
                    f'Quantity of the {product.product_name} has been updated'
                )
            else:
                bag.pop(product_id, None)  # Remove item if quantity is 0
                messages.warning(
                    request,
                    f'{product.product_name} has been removed '
                    'from the shopping bag'
                )
            request.session["bag"] = bag  # Save updated bag to session

        except Exception as e:
            messages.error(request, f'Error occurred: {e}')

    return redirect("view_bag")
