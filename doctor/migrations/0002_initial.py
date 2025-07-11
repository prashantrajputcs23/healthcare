# Generated by Django 4.2.15 on 2025-02-21 16:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('doctor', '0001_initial'),
        ('patient', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='branches',
            field=models.ManyToManyField(related_name='doctors', to='user.branch'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctors', to='user.department'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctors', to='user.organization'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='doctors', to='sites.site'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='availability',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='user.branch'),
        ),
        migrations.AddField(
            model_name='availability',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='doctor.doctor'),
        ),
        migrations.AddField(
            model_name='availability',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='user.organization'),
        ),
        migrations.AddField(
            model_name='availability',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='availabilities', to='sites.site'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='user.branch'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='doctor.doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='user.organization'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='patient.patient'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='sites.site'),
        ),
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together={('doctor', 'date', 'start_time')},
        ),
        migrations.AlterUniqueTogether(
            name='appointment',
            unique_together={('doctor', 'patient', 'date', 'branch')},
        ),
    ]
