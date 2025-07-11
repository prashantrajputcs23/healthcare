import uuid

from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from healthcare.utils import current_site, current_org, get_request
from user.models import Organization, User, Department, Branch


class Slider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=1000, null=True)
    heading = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='sliders')
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sliders')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='sliders')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_sliders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading

    @classmethod
    def active_sliders(cls):
        return cls.objects.filter(is_active=True, site=current_site())

    @classmethod
    def inactive_sliders(cls):
        return cls.objects.filter(is_active=False, site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Slider, self).save(*args, **kwargs)


class AboutHeadingChoice(models.TextChoices):
    about_clinic = 'about clinic'
    our_mission = 'our mission'
    our_vision = 'our vision'
    director_message = 'director message'
    why_to_choose_us = 'why to choose us'


class About(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, choices=AboutHeadingChoice.choices)
    heading = models.CharField(max_length=1000)
    sub_heading = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField()
    bullet_points = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    image = models.ImageField(upload_to='abouts')
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='abouts')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='abouts')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_abouts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading

    @classmethod
    def active_abouts(cls):
        return cls.objects.filter(is_active=True, site=current_site())

    @classmethod
    def inactive_abouts(cls):
        return cls.objects.filter(is_active=False, site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(About, self).save(*args, **kwargs)


class Services(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    short_description = models.TextField(max_length=1000)
    text = models.TextField()
    image = models.ImageField(upload_to='services')
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='services')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='services')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_services')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @classmethod
    def active_services(cls):
        return cls.objects.filter(is_active=True, site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Services, self).save(*args, **kwargs)


class Gallery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery')
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='galleries')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='galleries')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_galleries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @classmethod
    def active_galleries(cls):
        return cls.objects.filter(is_active=True, site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Gallery, self).save(*args, **kwargs)


class Testimonial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='testimonials')
    comment = models.TextField()
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='testimonials')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='testimonials')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_testimonials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def active_testimonials(cls):
        return cls.objects.filter(is_active=True, site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Testimonial, self).save(*args, **kwargs)


class SocialMediaLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    link = models.URLField()
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='social_media_links')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='social_media_links')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='social_media_links')
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
        super(SocialMediaLink, self).save(*args, **kwargs)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=1000)
    email = models.EmailField(null=True, blank=True)
    phone = PhoneNumberField(default='+91', null=True, blank=True)
    text = models.TextField()
    is_replied = models.BooleanField(default=False)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='messages')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Message, self).save(*args, **kwargs)

    def __str__(self):
        return self.first_name

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        # Validate that either email or phone is provided
        if not self.email and not self.phone:
            raise ValidationError('At least one contact method (email or phone) must be provided.')


class SubscribedUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    device_token = models.TextField()
    status = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='subscribed_users')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='subscribed_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(SubscribedUser, self).save(*args, **kwargs)


class Statistics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    happy_customers = models.CharField(max_length=5, default='2487 Customer')
    year_of_experience = models.CharField(max_length=5, default='7 Years')
    satisfaction = models.CharField(max_length=5, default='98%')
    is_active = models.BooleanField(default=True)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='statistics')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='statistics')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='statistics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.happy_customers

    def save(self, *args, **kwargs):
        self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(Statistics, self).save(*args, **kwargs)


class Offer(models.Model):
    title = models.CharField(max_length=500)
    heading = models.CharField(max_length=500)
    short_description = models.CharField(max_length=1500)
    description = models.TextField()
    image = models.ImageField(upload_to='offer_image')
    is_active = models.BooleanField(default=True)
    valid_till = models.DateField(null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='offers')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_offers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.site_id:
            self.site = current_site()
        super(Offer, self).save(*args, **kwargs)

    @classmethod
    def all(cls, request):
        return cls.objects.filter(site=current_site(request=request))

    @classmethod
    def active_offers(cls, request):
        return cls.objects.filter(site=current_site(request=request)).filter(valid_till__gte=timezone.now())


class OurTreatment(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='our_treatments')
    image = models.ImageField(upload_to='our_treatment')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='our_treatments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_our_treatments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.site_id:
            self.site = current_site()
        super(OurTreatment, self).save(*args, **kwargs)

    @classmethod
    def all(cls, request):
        return cls.objects.filter(site=current_site(request=request))

    def __str__(self):
        return self.name
