import uuid

from django.contrib.sites.models import Site
from django.utils import timezone
from doctor.models import Doctor
from healthcare.utils import get_request, current_org, current_site
from patient.models import Patient
from django.db import models

from user.models import Organization, User


class Vital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='vitals')
    blood_pressure = models.CharField(max_length=50)
    pulse = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='vitals')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='vitals')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='vitals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Vital, self).save(*args, **kwargs)

    def __str__(self):
        return f"Vitals for {self.patient.name}"


class Diagnosis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='diagnoses')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnoses')
    title = models.CharField(max_length=255)
    refer_to = models.CharField(max_length=100)
    diagnosis_result = models.TextField(blank=True, null=True)
    diagnosis_recommendation = models.TextField(blank=True, null=True)
    date_diagnosed = models.DateField(default=timezone.now)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='diagnosis')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='diagnosis')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='diagnosis')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Diagnosis, self).save(*args, **kwargs)

    def __str__(self):
        return f"Diagnosis for {self.patient.name} by Dr. {self.doctor.name}"
