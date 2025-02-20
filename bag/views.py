from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """
    A view to render bag content page.

    **Template**

    :template:`bag/bag.html`.
    """

    return render(request, 'bag/bag.html')


def add_to_bag(request, product_id):
    """
    Add particular product to the bag
    """
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})

    if product_id in list(bag.keys()):
        bag[product_id] += quantity
    else:
        bag[product_id] = quantity

    request.session['bag'] = bag
    return redirect(redirect_url)


def update_bag(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        bag = request.session.get("bag", {})

        if quantity > 0:
            bag[product_id] = quantity  # Update quantity
        else:
            bag.pop(product_id, None)  # Remove item if quantity is 0

        request.session["bag"] = bag  # Save updated bag to session

    return redirect("view_bag")
