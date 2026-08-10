# Ref: https://www.youtube.com/watch?v=lg8p1vD9-Bs&t=230s
from django.http import HttpResponse
from .models import Order


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
