import datetime

import django_filters
from django import forms
from django.utils import timezone
from django_filters import ChoiceFilter, DateFilter, CharFilter, FilterSet, ModelChoiceFilter, BooleanFilter, \
    DateFromToRangeFilter
from django_filters.widgets import RangeWidget

from patient.models import Patient
from user.models import User
from .models import PharmacyProduct, ProductCategory, SalesOrder, PurchaseOrder


class PharmacyProductFilter(django_filters.FilterSet):
    product_name = django_filters.CharFilter(field_name="product__name", lookup_expr='icontains', label="Product Name")
    category = django_filters.ModelChoiceFilter(queryset=ProductCategory.objects.all(), field_name="product__category",
                                                label="Category")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte", label="Min Price")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte", label="Max Price")
    in_stock = django_filters.BooleanFilter(field_name="quantity_in_stock", lookup_expr="gt", method="filter_in_stock",
                                            label="In Stock")

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(quantity_in_stock__gt=0) if value else queryset

    class Meta:
        model = PharmacyProduct
        fields = ['product_name', 'category', 'min_price', 'max_price', 'in_stock']


class SalesOrderFilter(django_filters.FilterSet):
    order_date = django_filters.DateRangeFilter(
        field_name="created_at",
        label="Order Date (Between)",
    )

    class Meta:
        model = SalesOrder
        fields = ['is_paid', 'order_date', 'created_by', 'patient']


class PurchaseOrderFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(field_name='supplier__name', lookup_expr='icontains', label='Supplier')
    order_date = django_filters.DateRangeFilter(
        field_name="created_at",
        label="Order Date (Between)"
    )
    is_paid = django_filters.BooleanFilter(field_name='is_paid', label='Is Paid')
    created_by = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains', label='Created By')

    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'is_paid', 'created_by']