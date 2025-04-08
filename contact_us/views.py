from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from .models import Contact_us_form


def contact_us_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to database
            Contact_us_form.objects.create(
                name=form.cleaned_data['your_name'],
                email=form.cleaned_data['your_email'],
                phone_number=form.cleaned_data.get('phone_number'),
                message=form.cleaned_data['message']
            )

            messages.success(request, "Thank you for your message! We will reply as soon as possible")
            return redirect('contact_form')
        else:
            messages.error(request, "There was an error with your submission. Please fix the errors and try again.")
    else:
        form = ContactForm()

    context = {
        'form': form
    }

    return render(request, 'contact_us/contact_form.html', context)
