from django.shortcuts import render

# Create your views here.


def view_bag(request):
    """
    A view to render bag content page.

    **Template**

    :template:`bag/bag.html`.
    """

    return render(request, 'bag/bag.html')
