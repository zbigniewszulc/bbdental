from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def customer_required(view_function):
    """Allow only customer accounts to make purchases"""

    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            messages.error(
                request, "Staff accounts cannot make purchases."
            )
            return redirect("all_products")

        return view_function(request, *args, **kwargs)

    return wrapper
