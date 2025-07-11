import uuid

from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone

from diagnostics.models import Diagnosis
from doctor.models import Doctor
from healthcare.utils import current_site, get_request, current_org
from inventory.models import PharmacyProduct
from patient.models import Patient
from user.models import Organization, User


class FrequencyChoice(models.TextChoices):
    ONCE_A_DAY = 'once_a_day', 'Once a Day'
    TWICE_A_DAY = 'twice_a_day', 'Twice a Day'
    THRICE_A_DAY = 'thrice_a_day', 'Thrice a Day'
    EVERY_FOUR_HOURS = 'every_four_hours', 'Every 4 Hours'
    BEFORE_SLEEP = 'before_sleep', 'Before Sleep'


class WithLiquidChoice(models.TextChoices):
    NORMAL_WATER = 'normal_water', 'Normal Water'
    LUKEWARM_WATER = 'lukewarm_water', 'Lukewarm Water'
    MILK = 'milk', 'Milk'
    SWEET_MILK = 'sweet_milk', 'Sweet Milk'
    JUICE = 'juice', 'Juice'
    NO_LIQUID = 'no_liquid', 'No Liquid'


class WhenToEatChoice(models.TextChoices):
    BEFORE_MEAL = 'before_meal', 'Before Meal'
    AFTER_MEAL = 'after_meal', 'After Meal'
    WITH_MEAL = 'with_meal', 'With Meal'
    EMPTY_STOMACH = 'empty_stomach', 'Empty Stomach'
    ANYTIME = 'anytime', 'Anytime'


class StatusChoice(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    ISSUED = 'issued', 'Issued'
    COMPLETED = 'completed', 'Completed'


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription_no = models.CharField(max_length=100, unique=True, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    diagnosis = models.ForeignKey(Diagnosis, null=True, blank=True, on_delete=models.CASCADE,
                                  related_name='prescriptions')
    date_issued = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default='draft')
    notes = models.TextField(blank=True, null=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='prescriptions')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='prescriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription #{self.id} for {self.patient.name}"

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Prescription, self).save(*args, **kwargs)


class PrescriptionDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='details')
    medication = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100, help_text='e.g., 1 tablet, 5 ml')
    frequency = models.CharField(max_length=100, help_text='e.g., twice a day, once a day')
    duration = models.CharField(max_length=100, help_text='e.g., 7 days, 2 weeks')
    when_to_eat = models.CharField(max_length=50, choices=WhenToEatChoice.choices,
                                   help_text="When to take the medication")
    with_liquid = models.CharField(max_length=50, choices=WithLiquidChoice.choices,
                                   help_text="What to take the medication with")
    instructions = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='prescription_details')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='prescription_details')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(PrescriptionDetail, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.medication.product.name} for {self.prescription.patient.name}"
