from django.contrib import admin
from .models import Order, OrderLineItem

# Register your models here.


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('line_item_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = (
        'order_number', 'date_of_order',
        'delivery_cost', 'subtotal', 'grand_total',
    )

    fields = (
        'order_number', 'date_of_order', 'name', 'surname', 'email',
        'phone_number', 'address_line_1', 'address_line_2', 'address_line_3',
        'town', 'postcode', 'country', 'delivery_cost', 'subtotal',
        'grand_total',
    )

    list_display = (
        'order_number', 'date_of_order', 'name', 'surname', 
        'delivery_cost', 'subtotal', 'grand_total',
    )

    ordering = ('-date_of_order',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLineItem)
