from django.contrib import admin
from .models import Contact_us_form
# Register your models here.


class Contact_us_formAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone_number',
        'date_submitted',
    )
    ordering = ('-date_submitted', )


admin.site.register(Contact_us_form, Contact_us_formAdmin)
