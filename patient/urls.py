from django.urls import path
from . views import *

app_name = 'patient'


urlpatterns = [
    path('search-patients', search_patients, name='search_patients'),
]