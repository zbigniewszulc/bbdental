from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from checkout.models import Order

from .forms import UserProfileForm
from .models import UserProfile

# Create your views here.


@login_required
def profile(request):
    """
    Render the user's profile page, where they can update their details
    and view past orders.

    **Context**

    ``form``
        An instance of :model:`profiles.UserProfileForm`
    ``orders``
        A queryset of :model:`checkout.Order`

    **Template**
    :template:`profiles/profile.html`.
    """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your profile has been updated successfully'
            )
    form = UserProfileForm(instance=profile)
    orders = Order.objects.filter(
        user_profile=profile).order_by('-date_of_order')

    context = {
        'form': form,
        'orders': orders,
    }

    return render(request, 'profiles/profile.html', context)


@login_required
def order_history(request, order_number):
    """
    Render detailed view of a specific order's information.

    **Context**
    ``order``
        An instance of :model:`checkout.Order`

    **Template**
    :template:`checkout/checkout_success.html`
    """
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user_profile__user=request.user,
    )

    context = {
        'order': order,
        'coming_from_profile': True
    }

    return render(request, 'checkout/checkout_success.html', context)
