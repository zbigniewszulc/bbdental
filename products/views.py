from django.shortcuts import render

# Create your views here.

def products(request):
    """ A view to render products page """
    return render(request, 'products/products.html')