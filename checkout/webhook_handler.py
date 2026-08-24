# Initial StripeWH_Handler class and generic event handler adapted from:
# https://www.youtube.com/watch?v=AU0F2wnrbEs&t=2s
#
# PaymentIntent specific handler methods adapted from:
# https://www.youtube.com/watch?v=lg8p1vD9-Bs&t=230s

import json

from django.http import HttpResponse

from products.models import Product
from profiles.models import UserProfile

from .emails import send_order_confirmation
from .models import Order, OrderLineItem


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        Will be send each time user coompletes the payemnt process
        """
        payment_intent = event['data']['object']
        stripe_pid = payment_intent['id']

        # Do not create another order for the same payment.
        # Stripe may send the same webhook more than once, so check if an order
        # for this payment already exists to avoid creating a duplicate order
        if Order.objects.filter(stripe_pid=stripe_pid).exists():
            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]}. '
                    'Order already exists.'
                ),
                status=200,
            )

        metadata = payment_intent['metadata']
        shipping = payment_intent['shipping']
        address = shipping['address']

        profile = UserProfile.objects.get(
            user_id=metadata['user_id']
        )

        # Stripe provides the customer's full name as one value
        full_name = shipping['name'].strip()
        name_parts = full_name.rsplit(' ', 1)
        name = name_parts[0]
        surname = name_parts[1] if len(name_parts) > 1 else ''

        order = Order.objects.create(
            user_profile=profile,
            business_name=profile.business_name,
            name=name,
            surname=surname,
            email=profile.user.email,
            phone_number=shipping['phone'],
            address_line_1=address['line1'],
            address_line_2=address.get('line2', ''),
            town=address['city'],
            postcode=address.get('postal_code', ''),
            country=address['country'],
            original_bag=metadata['bag'],
            stripe_pid=stripe_pid,
        )

        # Add the products saved in the Stripe metadata to the order
        bag = json.loads(metadata['bag'])

        try:
            for product_id, quantity in bag.items():
                product = Product.objects.get(id=product_id)

                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )
        except Product.DoesNotExist:
            # A product may have been removed from the database after the
            # payment started but before the webhook was processed
            order.delete()

            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]}. '
                    'Product not found.'
                ),
                status=500,
            )

        # Save the delivery details to the profile if the customer selected
        # this option during checkout
        if metadata.get('save_profile') == 'true':
            profile.user.first_name = name
            profile.user.last_name = surname
            profile.user.save()

            profile.default_phone_number = shipping['phone']
            profile.default_address_line_1 = address['line1']
            profile.default_address_line_2 = address.get('line2', '')
            profile.default_town = address['city']
            profile.default_postcode = address.get('postal_code', '')
            profile.default_country = address['country']
            profile.save()

        # Refresh the order to get the final totals and send one confirmation
        # email after all products have been added
        order.refresh_from_db()
        send_order_confirmation(order)

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )
