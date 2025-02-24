from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.contrib import messages
from bag.contexts import bag_contents
from django.conf import settings
from products.models import Product
from .models import OrderLineItem, Order
from .forms import OrderForm
import stripe

# Create your views here.


def checkout(request):
    """
    Handle the checkout process.

    **Context**

    ``order_form``
        An instance of :model:`checkout.OrderForm` for user input.
    ``stripe_public_key``
        Stripe public key from settings.
    ``client_secret``
        The client secret for Stripe PaymentIntent.

    **Template**
    :template:`checkout/checkout.html`.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    intent = None
    order_form = OrderForm()

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        form_data = {
            'name': request.POST.get('name', '').strip(),
            'surname': request.POST.get('surname', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'address_line_1': request.POST.get('address_line_1', '').strip(),
            'address_line_2': request.POST.get('address_line_2', '').strip(),
            'address_line_3': request.POST.get('address_line_3', '').strip(),
            'town': request.POST.get('town', '').strip(),
            'postcode': request.POST.get('postcode', '').strip(),
            'country': request.POST.get('country', '').strip(),
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()
            for product_id, quantity in bag.items():
                try:
                    product = Product.objects.get(id=product_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        quantity=quantity,
                    )
                    order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        'Database error: please contact administrator'
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            return redirect(
                reverse('checkout_success', args=[order.order_number])
            )
        else:
            messages.error(
                request,
                'Form validation error. Please check your data and try again'
            )

    # Even after a failed form submission at first time
    # always generate PaymentIntent
    bag = request.session.get('bag', {})
    # Prevent users from staying on checkout page
    # if there are no items in the shopping bag
    if not bag:
        messages.warning(
            request,
            'Your shopping bag is empty. Taking you back '
            'to browsing products'
            )
        return redirect(reverse('all_products'))

    # Get grand total and generate Stripe PaymentIntent
    current_bag = bag_contents(request)
    grand_total = current_bag['grand_total']
    stripe_grand_total = round(grand_total * 100)
    try:
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_grand_total,
            currency=settings.STRIPE_CURRENCY,
        )
        print(f"Stripe Client Secret: {intent.client_secret}")  # Debugging
    except Exception as e:
        messages.error(request, f"Stripe Payment Error: {e}")
        intent = None  # Prevent further errors

    if not stripe_public_key:
        messages.warning(request, 'Public key missing. Contact administrator')

    # Ensure client_secret is always a valid value
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret if intent else '',
    }

    return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    """
    Render checkout success view.

    **Context**

    ``order``
        An instance of :model:`checkout.Order`

    **Template**
    :template:`checkout/checkout_success.html`.
    """
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(
        request,
        f'Order {order_number} processed! '
        f'Confirmation email sent to {order.email}.'
    )

    if 'bag' in request.session:
        del request.session['bag']

    context = {
        'order': order
    }

    return render(request, 'checkout/checkout_success.html', context)
