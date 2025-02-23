from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from bag.contexts import bag_contents
from django.conf import settings
import stripe

# Create your views here.


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    bag = request.session.get('bag', {})
    # Prevent users from staying on checkout page
    # if there are no items in the shopping bag
    if not bag:
        messages.warning(
            request,
            "Your shopping bag is empty. Taking you back to browsing products"
        )
        return redirect(reverse('all_products'))

    current_bag = bag_contents(request)
    grand_total = current_bag['grand_total']
    stripe_grand_total = round(grand_total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_grand_total,
        currency=settings.STRIPE_CURRENCY,
    )

    if not stripe_public_key:
        messages.warning(request, 'Public key missing. Contact administrator')

    order_form = OrderForm()
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret
    }

    return render(request, 'checkout/checkout.html', context)
