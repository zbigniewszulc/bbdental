from django.db.models.signals import post_save, post_delete
from django.utils.timezone import localtime
from django.core.mail import send_mail
from django.dispatch import receiver
from django.conf import settings
from .models import OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on line item udpate or create
    Also reduces product quantity if a new order is created
    """
    instance.order.update_total()

    if created and instance.product:
        product = instance.product
        product.in_stock -= instance.quantity
        product.save()


@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on line item delete
    """
    instance.order.update_total()


@receiver(post_save, sender=OrderLineItem)
def send_order_confirmation(sender, instance, created, **kwargs):
    """
    Send an order confirmation email
    """
    order = instance.order
    order_items = OrderLineItem.objects.filter(order=order)

    if created and order_items.exists():
        order.update_total()

        # Convert date_of_order to human readable format
        formatted_order_date = localtime(
            order.date_of_order).strftime("%d %B %Y, %I:%M %p")

        # Build the email content
        subject = f"Order Confirmation - {order.order_number}"
        recipient_email = order.email

        email_body = f"""
        Dear {order.name} {order.surname},

        Thank you for your order! Here are your order details:

        Order Number: {order.order_number}
        Order Date: {formatted_order_date}

        Items Ordered:
        ---------------------------------
        """
        for item in order_items:
            email_body += f"{item.product.product_name} - Quantity: {
                item.quantity} - Price: €{item.line_item_total}\n"

        email_body += f"""
        ---------------------------------
        Subtotal: €{order.subtotal}
        Delivery Cost: €{order.delivery_cost}
        Grand Total: €{order.grand_total}

        Delivery Address:
        {order.address_line_1}
        {order.address_line_2 or ""}

        Thank you for shopping with us!
        BBdental
        """

        # Send the email
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
