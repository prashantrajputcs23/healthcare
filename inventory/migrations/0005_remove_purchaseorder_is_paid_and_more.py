# Generated by Django 4.2.15 on 2025-05-06 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_purchaseorder_status_salesorder_payment_mode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='is_paid',
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='status',
            field=models.CharField(default='pending', max_length=50),
        ),
    ]
