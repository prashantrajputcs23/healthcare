import django_filters
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.contrib.auth.models import User, Group
from django.db.models import Q


class UserFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(
        method='filter_by_full_name',
        label="Search Name"
    )
    group = django_filters.ChoiceFilter(
        choices=lambda: [(group.name, group.name) for group in Group.objects.all()],  # Show group names in dropdown
        method='filter_by_group',
        label="Group",
        empty_label="All Groups"
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Active Status"
    )

    class Meta:
        model = User
        fields = ['full_name', 'group', 'is_active']

    def filter_by_full_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(username__icontains=value)
        )

    def filter_by_group(self, queryset, name, value):
        if value:
            return queryset.filter(Q(groups__name__icontains=value))  # Filter by name or ID
        return queryset  # Return all if no filter is applied