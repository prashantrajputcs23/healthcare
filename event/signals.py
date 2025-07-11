from django.db.models.signals import post_save
from django.dispatch import receiver

from patient.models import Patient
from healthcare.utils import WhatsappThread
from .models import Event


@receiver(post_save, sender=Event)
def on_event_create(sender, instance, created, **kwargs):
    if created:
        pass
    if instance.is_published:
        patients = Patient.objects.all().order_by('phone').distinct('phone')
        for patient in patients:
            print(patient.name)
            WhatsappThread(instance, patient).start()

