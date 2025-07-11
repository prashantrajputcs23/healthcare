from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Layout, Column, Submit, Reset
from django import forms

from .models import Patient


class PatientForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control bg-light border-0 datetimepicker-input',
                'placeholder': 'Patient Name',

            }), label='')
    age = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control bg-light border-0 datetimepicker-input',
                'placeholder': 'Patient Age',

            }), label='')

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control bg-light border-0 datetimepicker-input',
                'placeholder': 'Patient Phone Number',

            }), label='')

    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Patient Address',
                'style': 'height:40px; width:100%;'
            }), label='')

    class Meta:
        model = Patient
        fields = ['name', 'age', 'phone', 'address']
