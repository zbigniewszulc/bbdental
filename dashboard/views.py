from datetime import timedelta
from decimal import Decimal
from math import ceil

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from checkout.models import Order, OrderLineItem
from products.models import Product

LOW_STOCK_THRESHOLD = 10
SALES_PERIOD_DAYS = 30


def get_stock_estimate_sort_value(product):
    """
    Sort available estimates by days left and place unavailable estimates last
    estimate_group: 0 = estimation available, 1 = estimation unavailable
    """
    if product.days_until_out_of_stock is None:
        estimate_group = 1
        estimated_days = 0
    else:
        estimate_group = 0
        estimated_days = product.days_until_out_of_stock

    return (estimate_group, estimated_days)


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

    # Define the beginning of the sales period
    sales_start_date = timezone.now() - timedelta(
        days=SALES_PERIOD_DAYS,
    )

    # Get all products for the stock estimation
    stock_estimates = Product.objects.all()

    # Calculate how many days the current stock may last
    for product in stock_estimates:
        total_sold = (
            OrderLineItem.objects
            .filter(
                product=product,
                order__date_of_order__gte=sales_start_date,
            )
            .exclude(order__status="cancelled")
            .aggregate(total=Sum("quantity"))["total"] or 0
        )

        if product.in_stock == 0:
            product.days_until_out_of_stock = 0
        elif total_sold:
            average_daily_sales = total_sold / SALES_PERIOD_DAYS
            product.days_until_out_of_stock = ceil(
                product.in_stock / average_daily_sales
            )
        else:
            product.days_until_out_of_stock = None

    # Display products expected to run out first at the top
    stock_estimates = sorted(
        stock_estimates,
        key=get_stock_estimate_sort_value,
    )

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
        "sales_period_days": SALES_PERIOD_DAYS,
        "stock_estimates": stock_estimates,
    }

    return render(
        request,
        "dashboard/staff_dashboard.html",
        context,
    )
