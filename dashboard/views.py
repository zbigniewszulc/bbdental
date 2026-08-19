from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from checkout.models import Order, OrderLineItem
from products.models import Product

LOW_STOCK_THRESHOLD = 10


# Create your views here
@staff_member_required
def staff_dashboard(request):
    """Display the sales dashboard for staff users"""
    total_orders = Order.objects.count()

    # aggregate() returns a dictionary with the calculated sum under
    # the "total" key. If there are no orders, Sum() returns None
    # so Decimal("0.00") is used instead
    total_revenue = Order.objects.exclude(
        status="cancelled",
    ).aggregate(
        total=Sum("grand_total"),
    )["total"] or Decimal("0.00")

    # Get the number of non-cancelled orders for each month
    # The results are ordered by month so the labels and totals
    # can be used in the same order on the dashboard chart
    monthly_orders = (
        Order.objects.exclude(status="cancelled")
        .annotate(month=TruncMonth("date_of_order"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    # Convert each month into a readable label for the chart
    monthly_order_labels = [
        order["month"].strftime("%B %Y")
        for order in monthly_orders
    ]

    # Store the number of orders for each month in the same order
    # as the labels above
    monthly_order_totals = [
        order["total"]
        for order in monthly_orders
    ]

    # Add together the quantities sold for each product
    # Cancelled orders are not included and only the top five are returned
    top_selling_products = (
        OrderLineItem.objects.exclude(order__status="cancelled")
        .values("product__product_name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:5]
    )

    # Store the product names in the same order as the query above
    top_selling_product_labels = [
        product["product__product_name"]
        for product in top_selling_products
    ]

    # Store the total quantity sold for each product
    top_selling_product_totals = [
        product["total_quantity"]
        for product in top_selling_products
    ]

    # Find products with fewer than 10 items left in stock
    low_stock_products = Product.objects.filter(
        in_stock__lt=LOW_STOCK_THRESHOLD,
    ).order_by("in_stock")

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "monthly_order_labels": monthly_order_labels,
        "monthly_order_totals": monthly_order_totals,
        "top_selling_products": top_selling_products,
        "top_selling_product_labels": top_selling_product_labels,
        "top_selling_product_totals": top_selling_product_totals,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "low_stock_products": low_stock_products,
    }

    return render(
        request,
        "dashboard/staff_dashboard.html",
        context,
    )
