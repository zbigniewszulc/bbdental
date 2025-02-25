from django.shortcuts import render

# Create your views here.


def profile(request):
    """
    Render user's profile page
    """
    context = {}

    return render(request, 'profiles/profile.html', context)
