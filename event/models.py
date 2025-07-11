import uuid
from django.contrib.sites.models import Site
from django.db import models
from datetime import timedelta
from django.utils import timezone

from doctor.models import Doctor
from healthcare.utils import current_site, current_org, get_request
from user.models import Organization, Branch, User


class EventStatus(models.TextChoices):
    UPCOMING = 'Upcoming'
    CANCELED = 'Canceled'
    DONE = 'Done'


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    title = models.CharField(max_length=550)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField()
    fee = models.PositiveIntegerField(null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    address = models.TextField()
    status = models.CharField(max_length=15, choices=EventStatus.choices)
    is_published = models.BooleanField(default=False)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='events')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='events')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='events')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_events')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        if not self.end:
            self.end = self.start + timedelta(hours=6)
        super(Event, self).save(*args, **kwargs)

    def get_day_of_event(self):
        return self.start.strftime('%A')

    @classmethod
    def active_event(cls):
        return Event.objects.filter(is_active=True, site=current_site())

    @classmethod
    def upcoming_events(cls):
        return cls.active_event().filter(start__gte=timezone.now(), status=EventStatus.UPCOMING)


class EventMessageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='event_message_log')
    is_sent_48 = models.BooleanField(default=False)
    is_sent_24 = models.BooleanField(default=False)
    is_sent_1 = models.BooleanField(default=False)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='event_message_logs')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='event_message_logs')
    site = models.OneToOneField(Site, on_delete=models.PROTECT, related_name='event_message_log')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        if not self.branch_id:
            self.branch = self.event.branch

        super(EventMessageLog, self).save(*args, **kwargs)
