from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product

# Create your views here.


def view_bag(request):
    """
    A view to render bag content page.

    **Template**

    :template:`bag/bag.html`.
    """

    return render(request, 'bag/bag.html')


def add_to_bag(request, product_id):
    """
    Add particular product to the shopping bag
    """
    try:
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get('quantity'))
        redirect_url = request.POST.get('redirect_url')
        bag = request.session.get('bag', {})

        if product_id in list(bag.keys()):
            bag[product_id] += quantity
            messages.success(
                request,
                f'{product.product_name} has been added to the shopping bag'
            )
        else:
            bag[product_id] = quantity
            messages.success(
                request,
                f'{product.product_name} has been added to the shopping bag'
            )

        request.session['bag'] = bag

    except Exception as e:
        messages.error(request, f'Error occurred: {e}')

    return redirect(redirect_url)


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
