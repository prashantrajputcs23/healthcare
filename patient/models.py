import uuid

from user.models import User
from django.contrib.sites.models import Site
from django.core.validators import MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from user.models import Organization, Gender


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    age = models.PositiveIntegerField(validators=[MaxValueValidator(100)], default=40)
    address = models.TextField()
    gender = models.CharField(max_length=6, choices=Gender.choices)
    phone = PhoneNumberField(default='+91', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(Patient, self).save(*args, **kwargs)

    @classmethod
    def delete_duplicates(cls):
        # Step 1: Fetch duplicates
        duplicates = cls.objects.values('name', 'phone').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)

        for duplicate in duplicates:
            name = duplicate['name']
            phone = duplicate['phone']
            # Fetch the duplicates for the specific name and phone
            patients = cls.objects.filter(name=name, phone=phone)

            # Keep the first entry and delete the rest
            first_patient = patients.first().delete()
            for patient in patients[1:]:
                print(f'Deleting duplicate patient: {patient}')
                patient.delete()

            print(f'Deleted duplicates for name: {name}, phone: {phone}')

        print('Successfully deleted all duplicate records.')

    class Meta:
        unique_together = ['name', 'phone']
        ordering = ['-created_at']
