from django.urls import path
from web.views import *

app_name = 'web'

urlpatterns = [
    path('', HomePage.as_view(), name='home_page'),
    path('about', AboutPage.as_view(), name='about_page'),
    path('services', ServicePage.as_view(), name='service_page'),
    path('service<slug:slug>', ServiceDetailView.as_view(), name='service_detail'),
    path('contact', ContactPage.as_view(), name='contact_page'),
    path('appointment/new', create_appointment, name='create_appointment'),
    path('doctor/dates', load_available_date, name='load_available_date'),
    path('doctor/branches', load_doctor_branches, name='load_doctor_branches'),
    path('doctor/dates/slots', load_time_slot, name='load_time_slot'),
]
