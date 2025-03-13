# Generated by Django 5.0.12 on 2025-03-12 22:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy_model', '0007_alter_lighting_lighting_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lighting',
            name='lighting_load_Wm2',
            field=models.FloatField(blank=True, help_text='Look up table based on type of lighting', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='lighting',
            name='on_for_hoursyear',
            field=models.FloatField(blank=True, help_text='Calculated depending on lighting controls and occupancy assumptions', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
