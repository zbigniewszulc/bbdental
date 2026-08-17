from django.conf import settings
from django.shortcuts import render

# Create your views here.


def index(request):
    """
    A view to render index page.

    **Context**
    ``free_delivery_threshold``
        Minimum order amount reqired to qualify for free delivery

    **Template**

    :template:`home/index.html`.
    """
    free_delivery_threshold = settings.FREE_DELIVERY_THRESHOLD
    context = {
        'free_delivery_threshold': free_delivery_threshold
    }
    return render(request, 'home/index.html', context)


def contact_page(request):
    """
    A view to render Contact Us page.

    **Template**
    :template:`home/contact.html`
    """
    return render(request, 'home/contact.html')


def privacy_policy(request):
    """
    A view to render the Privacy and Cookies Policy page with a PDF

    **Context**

    ``documents``
        A list of dictionaries containing:
        - ``name``: Title of the privacy-related document.
        - ``file``: Filename of the document stored in the static directory

    **Template**
    :template:`legal/privacy_policy.html`.
    """
    privacy_pdfs = [
        {
            "name": "Privacy and Cookies Policy",
            "file": "bbdental-privacy-and-cookies-policy.pdf"
        }
    ]

    context = {
        'documents': privacy_pdfs,
    }

    return render(request, 'legal/privacy_policy.html', context)


def terms_of_service(request):
    """
    A view to render the Terms and Conditions page with a PDF

    **Context**

    ``documents``
        A list of dictionaries containing:
        - ``name``: Title of the Terms of Service document.
        - ``file``: Filename of the document stored in the static directory.

    **Template**
    :template:`legal/terms_of_service.html`.
    """
    terms_pdfs = [
        {
            "name": "Terms and Conditions",
            "file": "bbdental-terms-and-conditions.pdf"
        }
    ]

    context = {
         'documents': terms_pdfs,
    }

    return render(request, 'legal/terms_of_service.html', context)
