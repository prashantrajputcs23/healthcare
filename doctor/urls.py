from django.urls import path

from .views import *

app_name = 'doctor'

urlpatterns = [
    path('create-update-availability', create_update_availability, name='create_update_availability'),
    path('availability-for-month', get_doctor_availability_for_month, name='doctor_availability_for_month'),
    path('appointments', AppointmentListView.as_view(), name='appointment_list'),
    path('prescription/core', core_template, name='prescription_template'),
    path('prescription/write', create_prescription, name='create_prescription'),
    path('vital/create', create_vital, name='create_vital'),
    path('diagnosis/create', create_diagnosis, name='create_diagnosis'),
]
