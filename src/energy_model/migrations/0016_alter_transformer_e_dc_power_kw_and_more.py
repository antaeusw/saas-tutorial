# Generated by Django 5.0.12 on 2025-03-14 12:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy_model', '0015_transformer_core_loss_factor_percent_input_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformer',
            name='E_DC_power_kW',
            field=models.FloatField(blank=True, editable=False, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='transformer',
            name='total_installed_capacity_kW',
            field=models.FloatField(blank=True, editable=False, help_text='Including redundancy', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
