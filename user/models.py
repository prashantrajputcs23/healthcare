import random
import secrets
import string
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import TruncDate
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.timezone import localdate
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from healthcare.utils import current_site, get_request, current_org
from user.managers import UserManager


def get_random_number(n):
    minimum = pow(10, n - 1)
    maximum = pow(10, n) - 1
    return random.randint(minimum, maximum)


def get_random_password(length=4):
    special_char = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=']
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    result_str = result_str.capitalize() + secrets.choice(special_char) + str(get_random_number(4)) + secrets.choice(
        special_char)
    return result_str


class Gender(models.TextChoices):
    MALE = 'Male'
    FEMALE = 'Female'


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    gender = models.CharField(
        max_length=50,
        choices=Gender.choices,
        help_text='required*'
    )
    phone = PhoneNumberField(region="IN", null=True)
    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='user', null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['password', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        ordering = ['first_name']

    def __str__(self):
        return self.name

    @property
    def avatar(self):
        path = '/static/user/img/avatars'
        if self.gender == Gender.MALE:
            return f'{path}/male-avatar.png'
        if self.gender == Gender.FEMALE:
            return f'{path}/female-avatar.png'
        return f'{path}/jack.jpg'

    @property
    def name(self):
        return f'{self.first_name.title()} {self.last_name.title()}'

    @property
    def get_groups(self):
        groups = self.groups.all()
        if groups.exists():
            return ", ".join(group.name.title() for group in groups)
        return ''

    @classmethod
    def all(cls):
        return cls.objects.filter(site=current_site())

    def save(self, *args, **kwargs):
        site = current_site()
        if not self.site_id and site:
            self.site = site
        super(User, self).save(*args, **kwargs)

    @property
    def is_doctor(self):
        try:
            doctor = self.doctor
            return True
        except Exception as e:
            return False

    @property
    def get_monthly_attendance_status(self):
        today = timezone.now().date()
        start_date = today.replace(day=1)  # महीने की पहली तारीख
        end_date = today.replace(day=1).replace(month=today.month + 1) - timedelta(days=1)  # महीने की आखिरी तारीख

        # करंट मंथ की अटेंडेंस लाना और डेट-वाइज स्टेटस बनाना
        attendance_records = self.attendance.filter(created_at__date__range=(start_date, end_date)).values('created_at',
                                                                                                           'status')

        # डेट-वाइज अटेंडेंस स्टोर करने के लिए डिक्शनरी
        attendance_dict = {}

        for record in attendance_records:
            record_date = record['created_at'].date()
            attendance_dict[record_date] = record['status']

        return attendance_dict


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.PROTECT, related_name='owned_organisations')
    name = models.CharField(max_length=100, unique=True, null=False)
    slug = models.SlugField(unique=True, null=False, blank=True)
    logo = models.ImageField(upload_to='Logo', null=True, blank=True)
    prefix = models.CharField(max_length=12, default='RG')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_organisations')
    site = models.OneToOneField(Site, on_delete=models.PROTECT, related_name='organization')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Organization.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def get_default_branch(self):
        branches = self.branches.filter(is_default=True)
        if branches.exists():
            return branches.first()
        return None


class WhiteIP(models.Model):
    ip = models.GenericIPAddressField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_ips')
    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='site_white_ips', null=True)
    organization = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='org_white_ips', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.ip}'

    def save(self, *args, **kwargs):
        if not self.site_id:
            self.site = current_site()
        if not self.organization_id:
            self.organization = current_org()
        if not self.created_by_id:
            self.created_by = get_request().user
        super(WhiteIP, self).save(*args, **kwargs)



class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def departments(cls):
        return cls.objects.all()


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, related_name='states')
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, related_name='cites')
    state = models.ForeignKey(State, on_delete=models.RESTRICT, related_name='cites')
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    district = models.ForeignKey(District, null=True, on_delete=models.RESTRICT, related_name='addresses')
    city = models.CharField(max_length=100, null=True)
    state = models.ForeignKey(State, on_delete=models.RESTRICT, related_name='addresses')
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, related_name='addresses')
    postal_code = models.CharField(max_length=20)
    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='addresses')

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}"

    def save(self, *args, **kwargs):
        if not self.site_id:
            self.site = current_site()
        super(Address, self).save(*args, **kwargs)


class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = PhoneNumberField(null=True, help_text='example: +91-8433161615')
    email = models.EmailField(unique=True)
    opening_hours = models.CharField()
    opening_days = models.CharField()
    address = models.OneToOneField(Address, on_delete=models.RESTRICT, related_name='branches')
    is_default = models.BooleanField(default=False)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='branches')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='branches')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_branches')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.organisation.name} -- {self.address}'

    @classmethod
    def all_branches(cls):
        return cls.objects.filter(is_active=True, site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Branch, self).save(*args, **kwargs)


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=512, choices=(('P', 'Present'), ('A', 'Absent'),))
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='attendances', editable=False)
    site = models.ForeignKey(Site, on_delete=models.RESTRICT, related_name='attendances', editable=False)
    in_time = models.DateTimeField(auto_now_add=True)
    out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.name + ' '+ self.get_status_display()

    def total_time_spent(self):
        if self.out_time and self.in_time:
            return self.out_time - self.in_time
        return timedelta(0)

    def total_time_str(self):
        duration = self.total_time_spent()
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes = remainder // 60
        return f"{int(hours)}h {int(minutes)}m"

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-in_time']

    def clean(self):
        if Attendance.objects.filter(
                user=self.user,
                in_time__date=localdate(self.in_time)
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Attendance already marked for this user today.")