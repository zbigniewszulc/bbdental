from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bag.contexts import bag_contents
from django.conf import settings
from products.models import Product
from profiles.models import UserProfile
from .models import OrderLineItem, Order
from .forms import OrderForm, OrderStatusForm
from bbdental.decorators import customer_required
from .emails import send_order_confirmation
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator

import stripe
import json


# Create your views here.
@login_required
@customer_required
@require_POST
def cache_checkout_data(request):
    """Save checkout data in the PaymentIntent metadata."""
    client_secret = request.POST.get('client_secret')

    if not client_secret:
        return HttpResponse(status=400)

    stripe_pid = client_secret.split('_secret_')[0]
    save_profile = request.POST.get('save_profile') == 'true'

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(
            stripe_pid,
            metadata={
                'bag': json.dumps(request.session.get('bag', {})),
                'user_id': str(request.user.id),
                'save_profile': str(save_profile).lower(),
            },
        )

        # Save the PaymentIntent ID in the session. If Stripe confirms the
        # payment but the customer closes the page before the checkout
        # form is submitted, Django can find the order created by the webhook
        # when the customer returns
        request.session['stripe_pid'] = stripe_pid

        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(content=str(e), status=400)


@login_required
@customer_required
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
    bag = request.session.get('bag', {})
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    intent = None
    order_form = OrderForm()

    # Check if the webhook completed an order for the PaymentIntent
    # saved in this user's session
    session_stripe_pid = request.session.get('stripe_pid')

    if session_stripe_pid:
        existing_order = Order.objects.filter(
            stripe_pid=session_stripe_pid,
            user_profile=request.user.userprofile,
        ).first()

        if existing_order:
            return redirect(
                reverse(
                    'checkout_success',
                    args=[existing_order.order_number],
                )
            )

    if request.method == 'GET':
        try:
            # Get the user's profile to pre-fill the order form
            profile = UserProfile.objects.get(user=request.user)
            order_form = OrderForm(initial={
                'name': profile.user.first_name,
                'surname': profile.user.last_name,
                'email': profile.user.email,
                'phone_number': profile.default_phone_number,
                'country': profile.default_country,
                'postcode': profile.default_postcode,
                'town': profile.default_town,
                'address_line_1': profile.default_address_line_1,
                'address_line_2': profile.default_address_line_2,
                'county': profile.default_country,
            })
            if bag:
                messages.info(
                    request, 'Profile details pre-filled for faster checkout.')
        except UserProfile.DoesNotExist:
            order_form = OrderForm()
            messages.warning(
                request,
                'Your profile details not found. '
                'Please enter your details manually.'
            )

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        stripe_pid = request.POST.get('stripe_pid')

        # If the webhook created the order before the checkout form
        # was submitted, use that order to avoid creating a duplicate
        # for the same payment
        if stripe_pid:
            existing_order = Order.objects.filter(
                stripe_pid=stripe_pid,
                user_profile=request.user.userprofile,
            ).first()  # Returns an object or None if nothing found

            if existing_order:
                return redirect(
                    reverse(
                        'checkout_success',
                        args=[existing_order.order_number],
                    )
                )

        form_data = {
            'name': request.POST.get('name', '').strip(),
            'surname': request.POST.get('surname', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'address_line_1': request.POST.get('address_line_1', '').strip(),
            'address_line_2': request.POST.get('address_line_2', '').strip(),
            'town': request.POST.get('town', '').strip(),
            'postcode': request.POST.get('postcode', '').strip(),
            'country': request.POST.get('country', '').strip(),
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.original_bag = json.dumps(bag)
            order.stripe_pid = request.POST.get('stripe_pid') or None
            order.save()

            # Save data to profile if checkbox selected
            if 'save_profile' in request.POST:
                profile = UserProfile.objects.get(user=request.user)
                profile.user.first_name = order_form.cleaned_data['name']
                profile.user.last_name = order_form.cleaned_data['surname']
                profile.user.save()  # Save User instance
                profile.default_phone_number = order_form.cleaned_data[
                    'phone_number']
                profile.default_address_line_1 = order_form.cleaned_data[
                    'address_line_1']
                profile.default_address_line_2 = order_form.cleaned_data[
                    'address_line_2']
                profile.default_town = order_form.cleaned_data['town']
                profile.default_postcode = order_form.cleaned_data['postcode']
                profile.default_country = order_form.cleaned_data['country']
                profile.save()  # Save profile instance
                messages.success(
                    request,
                    "Your profile has been updated with these details."
                )

            # Assign the order to the user profile if logged in
            if request.user.is_authenticated:
                profile = UserProfile.objects.get(user=request.user)
                order.user_profile = profile
                order.save()

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

            # Refresh order data to get the final totals before sending email
            order.refresh_from_db()
            send_order_confirmation(order)

            return redirect(
                reverse('checkout_success', args=[order.order_number])
            )
        else:
            messages.error(
                request,
                'Form validation error. Please check your data and try again'
            )

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


@login_required
@customer_required
def checkout_success(request, order_number):
    """
    Render checkout success view.

    **Context**

    ``order``
        An instance of :model:`checkout.Order`

    **Template**
    :template:`checkout/checkout_success.html`.
    """
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user_profile__user=request.user,
    )

    messages.success(
        request,
        f'Order {order_number} processed! '
        f'Confirmation email sent to {order.email}.'
    )

    if 'bag' in request.session:
        del request.session['bag']

    if 'stripe_pid' in request.session:
        del request.session['stripe_pid']

    context = {
        'order': order
    }

    return render(request, 'checkout/checkout_success.html', context)


@staff_member_required
def manage_orders(request):
    """Display all customer orders for staff users"""
    orders = Order.objects.all().order_by('-date_of_order')

    paginator = Paginator(orders, 70)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(
        request,
        'checkout/order_management.html',
        context,
    )


@staff_member_required
def order_management_details(request, order_number):
    """Display order details for staff users"""
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        status_form = OrderStatusForm(
            request.POST,
            # Update this order instead of creating a new one
            instance=order,
        )

        if status_form.is_valid():
            status_form.save()
            messages.success(
                request,
                'Order status updated successfully',
            )
            return redirect(
                'order_management_details',
                order_number=order.order_number,
            )
    else:
        status_form = OrderStatusForm(instance=order)

    context = {
        'order': order,
        'status_form': status_form,
    }

    return render(
        request,
        'checkout/order_management_details.html',
        context,
    )
