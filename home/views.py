from django.shortcuts import render

# Create your views here.


def index(request):
    """
    A view to render index page.

    **Template**

    :template:`home/index.html`.
    """

    return render(request, 'home/index.html')
