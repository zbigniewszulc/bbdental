from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
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

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
    }

    return render(
        request,
        "dashboard/staff_dashboard.html",
        context,
    )
