# Generated by Django 4.2.15 on 2025-02-21 16:11

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='testimonials')),
                ('comment', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_testimonials', to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testimonials', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='testimonials', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='SubscribedUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('device_token', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribed_users', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscribed_users', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('happy_customers', models.CharField(default='2487 Customer', max_length=5)),
                ('year_of_experience', models.CharField(default='7 Years', max_length=5)),
                ('satisfaction', models.CharField(default='98%', max_length=5)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='statistics', to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='statistics', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='SocialMediaLink',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('icon', models.CharField(max_length=100)),
                ('link', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='social_media_links', to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_media_links', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='social_media_links', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=1000, null=True)),
                ('heading', models.CharField(max_length=1000)),
                ('image', models.ImageField(upload_to='sliders')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_sliders', to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sliders', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sliders', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('short_description', models.TextField(max_length=1000)),
                ('text', models.TextField()),
                ('image', models.ImageField(upload_to='services')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_services', to=settings.AUTH_USER_MODEL)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='user.department')),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='services', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=1000)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='+91', max_length=128, null=True, region=None)),
                ('text', models.TextField()),
                ('is_replied', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages', to='sites.site')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tag', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='gallery')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_galleries', to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='galleries', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='galleries', to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='About',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(choices=[('about clinic', 'About Clinic'), ('our mission', 'Our Mission'), ('our vision', 'Our Vision'), ('director message', 'Director Message'), ('why to choose us', 'Why To Choose Us')], max_length=100)),
                ('heading', models.CharField(max_length=1000)),
                ('sub_heading', models.CharField(blank=True, max_length=100, null=True)),
                ('text', models.TextField()),
                ('bullet_points', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None)),
                ('image', models.ImageField(upload_to='abouts')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_abouts', to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='abouts', to='user.organization')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='abouts', to='sites.site')),
            ],
        ),
    ]
