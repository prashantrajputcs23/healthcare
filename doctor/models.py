import uuid
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from healthcare.utils import current_site, get_request, current_org
from patient.models import Patient
from user.models import User, Branch
from django.contrib.sites.models import Site
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from user.models import Department, Organization


class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    image = models.ImageField(upload_to='profile_photo', blank=True, null=True)
    phone = PhoneNumberField(null=True, blank=True, help_text='example: +91-8433161615')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    slot_duration = models.DurationField(default=timedelta(minutes=10))
    available_days = models.PositiveIntegerField(default=30)
    branches = models.ManyToManyField(Branch, related_name='doctors')
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='doctors')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='doctors')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Doctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.name

    @classmethod
    def active_doctors(cls):
        return cls.objects.filter(user__is_active=True, site=current_site())

    @property
    def name(self):
        return self.user.name

    def get_monthly_time_slots(self, year, month):
        first_day = datetime(year, month, 1)
        last_day = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        availability_records = Availability.objects.filter(
            doctor=self,
            date__range=[first_day.date(), last_day.date()],
            is_available=True
        )

        slots_by_date = {}
        for availability in availability_records:
            slots_by_date[availability.date] = self._generate_slots_for_availability(availability)

        return slots_by_date

    def generate_time_slots(self, availability):
        """
        Generate time slots based on the doctor's slot_duration and availability start/end times.
        Excludes lunch breaks and past time slots for the current day.
        """
        start_time = availability.start_time
        end_time = availability.end_time
        lunch_start_time = availability.lunch_start_time
        lunch_end_time = availability.lunch_end_time

        slots = []
        # Get the current time and today's date
        now = datetime.now().time()
        today = date.today()

        # Convert start_time and end_time to datetime objects for calculations
        current_time = datetime.combine(date.min, start_time)
        end_datetime = datetime.combine(date.min, end_time)
        slot_duration_seconds = int(self.slot_duration.total_seconds())

        while current_time + timedelta(seconds=slot_duration_seconds) <= end_datetime:
            slot_end_time = current_time + timedelta(seconds=slot_duration_seconds)

            # Convert lunch times to datetime objects
            lunch_start_datetime = datetime.combine(date.min, lunch_start_time)
            lunch_end_datetime = datetime.combine(date.min, lunch_end_time)

            # Check if the slot overlaps with the lunch break
            if not (lunch_start_datetime <= current_time < lunch_end_datetime or
                    lunch_start_datetime < slot_end_time <= lunch_end_datetime):

                # If the availability date is today, exclude passed slots
                if availability.date > today or (availability.date == today and current_time.time() >= now):
                    slots.append(current_time.time())

            # Move to the next slot
            current_time += timedelta(seconds=slot_duration_seconds)

        return slots

    def book_appointment(self, patient, date, start_time):
        if not self.is_slot_available(date, start_time):
            raise ValueError("Slot is not available.")

        slot_end_time = (datetime.combine(date, start_time) + self.slot_duration).time()
        slot = {
            'start_time': start_time,
            'end_time': slot_end_time
        }

        appointment = Appointment.objects.create(
            doctor=self,
            patient=patient,
            date=date,
            start_time=start_time,
            end_time=slot_end_time,
            status='pending'
        )
        return appointment

    def is_slot_available(self, date, start_time):
        slot_end_time = (datetime.combine(date, start_time) + self.slot_duration).time()
        is_available = Availability.objects.filter(
            doctor=self,
            date=date,
            start_time__lte=start_time,
            end_time__gte=slot_end_time,
            is_available=True
        ).exists()

        if not is_available:
            return False

        overlap = Appointment.objects.filter(
            doctor=self,
            date=date,
            start_time__lt=slot_end_time,
            end_time__gt=start_time
        ).exists()

        return not overlap


class Availability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    lunch_start_time = models.TimeField(blank=True, null=True, default='14:00')
    lunch_end_time = models.TimeField(blank=True, null=True, default='15:00')
    is_available = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='availabilities')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='availabilities')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='availabilities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Availability, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date} from {self.start_time} to {self.end_time}"

    def update_appointments(self):
        if not self.is_available:
            Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
                start_time__gte=self.start_time,
                end_time__lte=self.end_time
            ).update(status='cancelled')
            return


class AppointmentStatus(models.Choices):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    DONE = 'Done'


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token_no = models.PositiveIntegerField(null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=AppointmentStatus.choices)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='appointments')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='appointments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_appointments', null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def calc_end_time(self):
        doctor = self.doctor
        if doctor and doctor.slot_duration:
            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = start_datetime + doctor.slot_duration
            return end_datetime
        return self.end_time

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        if not self.end_time:  # Calculate end time only if it's not already set
            self.end_time = self.calc_end_time
        super().save(*args, **kwargs)

    def clean(self):
        if self.start_time is None:
            raise ValidationError(_('Start time must be provided.'))

        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            branch=self.branch,
            date=self.date,
            start_time__lt=self.calc_end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)  # Exclude current instance for updates

        if overlapping_appointments.exists():
            raise ValidationError(
                _('An appointment with this doctor at this branch on this date already exists during the selected time slot.'))

    class Meta:
        unique_together = ('doctor', 'patient', 'date', 'branch')

    def __str__(self):
        return f"Appointment with {self.doctor.user.name} on {self.date} from {self.start_time} to {self.end_time}"

    @classmethod
    def all(cls):
        request = get_request()
        if request:
            if request.user.is_authenticated:
                return request.user.doctor.appointments.all()
        return

    @classmethod
    def get_current_appointments(cls, queryset=None):
        if not queryset:
            queryset = cls.all()
        now = datetime.now()
        return queryset.filter(date__lte=now.date(), start_time__lte=now.time(), end_time__gte=now.time())

    @classmethod
    def get_upcoming_appointments(cls, queryset=None):
        if not queryset:
            queryset = cls.all()
        now = datetime.now()
        return cls.all().filter(date__gt=now.date()).order_by('date', 'start_time')

    @classmethod
    def get_done_appointments(cls, queryset=None):
        if not queryset:
            queryset = cls.all()
        today = date.today()
        return cls.all().filter(date__lt=today, status=AppointmentStatus.DONE).order_by('-date', '-start_time')

    @classmethod
    def get_cancelled_appointments(cls, queryset=None):
        if not queryset:
            queryset = cls.all()
        today = date.today()
        return cls.all().filter(date__lt=today, status=AppointmentStatus.CANCELLED).order_by('-date', '-start_time')

    @classmethod
    def get_today_appointments(cls, queryset=None):
        if not queryset:
            queryset = cls.all()
        today = date.today()
        return cls.all().filter(date=today).order_by('start_time')

    @classmethod
    def get_today_upcoming_appointments(cls, queryset=None):
        if not queryset:
            queryset = cls.all()
        now = datetime.now()
        today = date.today()
        return cls.all().filter(date=today, start_time__gte=now.time()).order_by('start_time')

    @classmethod
    def get_today_past_appointments(cls, queryset=None):
        if not queryset:
            queryset = cls.all()
        now = datetime.now()
        today = date.today()
        return cls.all().filter(date=today, end_time__lte=now.time()).order_by('-end_time')
