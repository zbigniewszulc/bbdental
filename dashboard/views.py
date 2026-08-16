from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


# Create your views here.
@staff_member_required
def staff_dashboard(request):
    """Display the sales dashboard for staff users"""
    return render(request, "dashboard/staff_dashboard.html")
