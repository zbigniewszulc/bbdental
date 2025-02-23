from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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
