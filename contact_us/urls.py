from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_us_view, name='contact_form'),
]
