from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from checkout.models import Order


# Create your views here.
@staff_member_required
def staff_dashboard(request):
    """Display the sales dashboard for staff users"""
    total_orders = Order.objects.count()

    # aggregate() returns a dictionary with the calculated sum under
    # the "total" key. If there are no orders, Sum() returns None,
    # so Decimal("0.00") is used instead
    total_revenue = Order.objects.exclude(
        status="cancelled",
    ).aggregate(
        total=Sum("grand_total"),
    )["total"] or Decimal("0.00")

    # Get the number of non-cancelled orders for each month.
    # The results are ordered by month so the labels and totals
    # can be used in the same order on the dashboard chart.
    monthly_orders = (
        Order.objects.exclude(status="cancelled")
        .annotate(month=TruncMonth("date_of_order"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    # Convert each month into a readable label for the chart.
    monthly_order_labels = [
        order["month"].strftime("%B %Y")
        for order in monthly_orders
    ]

    # Store the number of orders for each month in the same order
    # as the labels above.
    monthly_order_totals = [
        order["total"]
        for order in monthly_orders
    ]

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "monthly_order_labels": monthly_order_labels,
        "monthly_order_totals": monthly_order_totals,
    }

    return render(
        request,
        "dashboard/staff_dashboard.html",
        context,
    )
