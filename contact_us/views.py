from django.shortcuts import render
from .forms import ContactForm


def contact_us_view(request):
    form = ContactForm()
    context = {
        'form': form,
    }

    return render(request, 'contact_us/contact_form.html', context)
