from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import localtime


def send_order_confirmation(order):
    """Send one order confirmation email."""
    order_items = order.line_items.all()

    # Convert date_of_order to human readable format
    formatted_order_date = localtime(
        order.date_of_order
    ).strftime("%d %B %Y, %I:%M %p")

    # Build email content
    items = "\n".join(
        f"- {item.product.product_name} | Quantity: {item.quantity} | "
        f"Line Total: €{item.line_item_total:.2f}"
        for item in order_items
    )

    delivery_address = "\n".join(
        line for line in [
            order.address_line_1,
            order.address_line_2,
            order.town,
            order.postcode,
            order.country.name,
        ] if line
    )

    subject = f"Order Confirmation - {order.order_number}"

    # .2f - format order totals with two decimal places
    email_body = (
        f"Dear {order.name} {order.surname},\n\n"
        "Thank you for your order. Here are your order details:\n\n"
        f"Order Number: {order.order_number}\n"
        f"Order Date: {formatted_order_date}\n\n"
        "Items Ordered:\n"
        "---------------------------------\n"
        f"{items}\n"
        "---------------------------------\n"
        f"Subtotal: €{order.subtotal:.2f}\n"
        f"Delivery Cost: €{order.delivery_cost:.2f}\n"
        f"Grand Total: €{order.grand_total:.2f}\n\n"
        "Delivery Address:\n"
        f"{delivery_address}\n\n"
        "Thank you for shopping with us!\n"
        "BBdental"
    )

    send_mail(
        subject=subject,
        message=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=False,
    )
