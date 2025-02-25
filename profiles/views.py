from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm
from checkout.models import Order
# Create your views here.


def profile(request):
    """
    Render user's profile page
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
    orders = Order.objects.filter(user_profile=profile)

    context = {
        'form': form,
        'orders': orders,
    }

    return render(request, 'profiles/profile.html', context)
