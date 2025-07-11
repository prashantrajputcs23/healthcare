from django.http import JsonResponse
from django.shortcuts import render

from patient.models import Patient


def search_patients(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all()
    if query:
        patients = patients.filter(name__icontains=query) | Patient.objects.filter(phone__icontains=query)
        results = [
            {"id": patient.id, "text": f"{patient.name} ({patient.phone})"}
            for patient in patients
        ]
    else:
        patients = patients[:6]
        results = [
            {"id": patient.id, "text": f"{patient.name} ({patient.phone})"}
            for patient in patients
        ]
    return JsonResponse({"results": results})