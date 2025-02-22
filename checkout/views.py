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
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51QvO9sFGwD2JX9ErtZZyKjUshUhU4EWDRDklBdtawNUuFtt63YQtpB5s4acGVOs5hiu5sVj2KJZgfGQP7keHTcCG008q08mc47',
        'client_secret': 'test client secret'
    }

    return render(request, 'checkout/checkout.html', context)
