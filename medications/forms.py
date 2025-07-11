# forms.py
from django import forms

from diagnostics.models import Diagnosis, Vital
from .models import Prescription, PrescriptionDetail


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['diagnosis', 'date_issued', 'notes']


class PrescriptionDetailForm(forms.ModelForm):
    class Meta:
        model = PrescriptionDetail
        fields = ['medication', 'dosage', 'frequency', 'duration', 'instructions']


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['patient', 'doctor', 'diagnosis_result']


class VitalForm(forms.ModelForm):
    class Meta:
        model = Vital
        fields = ['patient', 'doctor', 'blood_pressure', 'pulse']