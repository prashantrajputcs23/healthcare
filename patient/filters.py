import django_filters
from .models import Patient


class PatientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')
    age = django_filters.NumberFilter(label='Age')
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date', label='Created At')

    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'created_at']
