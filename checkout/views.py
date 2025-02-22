from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm

# Create your views here.


def checkout(request):
    bag = request.session.get('bag', {})
    # Prevent users from staying on checkout page
    # if there are no items in the shopping bag
    if not bag:
        messages.warning(
            request,
            "Your shopping bag is empty. Taking you back to browsing products"
        )
        return redirect(reverse('all_products'))

    order_form = OrderForm()
    context = {
        'order_form': order_form
    }

    return render(request, 'checkout/checkout.html', context)
