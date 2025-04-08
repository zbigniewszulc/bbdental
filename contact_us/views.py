from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import ContactForm
from .models import Contact_us_form


def contact_us_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save to database
            contact = Contact_us_form.objects.create(
                name=form.cleaned_data['your_name'],
                email=form.cleaned_data['your_email'],
                phone_number=form.cleaned_data.get('phone_number'),
                message=form.cleaned_data['message']
            )

            # Email data
            user_subject = 'Thank you for contacting BBDental'
            user_message = (
                f"Dear {contact.name},\n\n"
                f"Thank you for reaching out to us. We received your message and will get back to you shortly.\n\n"
                f"Your message:\n{contact.message}\n\n"
                f"Best regards,\nBB Dental Team"
            )

            admin_subject = f'New contact form submission from {contact.name}'
            admin_message = (
                f"New contact us form submission:\n\n"
                f"Name: {contact.name}\n"
                f"Email: {contact.email}\n"
                f"Phone: {contact.phone_number or 'N/A'}\n"
                f"Message:\n{contact.message}"
            )

            # Send confirmation to user
            send_mail(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,
                [contact.email],
                fail_silently=False,
            )

            # Send copy to default email (which is admin)
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            messages.success(request, "Thank you for your message! A confirmation email has been sent.")
            return redirect('contact_form')
        else:
            messages.error(request, "There was an error with your submission. Please fix the errors and try again.")
    else:
        form = ContactForm()

    context = {
        'form': form
    }

    return render(request, 'contact_us/contact_form.html', context)
