from datetime import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit, Reset
from django import forms

from healthcare.utils import get_request, current_site
from patient.models import Patient
from user.models import Branch
from .models import Availability, Doctor, Appointment


class MonthAvailabilityForm(forms.Form):
    year = forms.IntegerField(initial=datetime.now().year, label='Year')
    month = forms.IntegerField(initial=datetime.now().month, label='Month')
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    lunch_start_time = forms.TimeField(required=False)
    lunch_end_time = forms.TimeField(required=False)
    same_for_all_days = forms.BooleanField(required=False, label='Apply to all days of the month')


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['doctor', 'date', 'start_time', 'end_time', 'lunch_start_time', 'lunch_end_time', 'is_available']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_start_time': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.none(),
        widget=forms.Select(
            attrs={
                'class': 'form-select bg-light border-0',
                'style': 'height: 55px;'
            }),
        label='')

    branch = forms.ModelChoiceField(
        queryset=Branch.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select bg-light border-0',
            'style': 'height: 55px;'
        }), label='')

    date = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Date of appointment',
            'class': 'form-control bg-light border-0',
            'style': 'height: 55px;'
        }), label='')

    start_time = forms.CharField(
        widget=forms.Select(attrs={
            'placeholder': 'time of appointment',
            'class': 'form-select bg-light border-0',
            'style': 'height: 55px;'
        }), label='')

    class Meta:
        model = Appointment
        fields = ['doctor', 'branch', 'date', 'start_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.active_doctors()
        self.fields['branch'].queryset = Branch.all_branches()

        # Add empty option as a placeholder
        self.fields['doctor'].choices = [('', 'Select Doctor')] + list(self.fields['doctor'].choices)
        self.fields['branch'].choices = [('', 'Select Branch')] + list(self.fields['branch'].choices)


