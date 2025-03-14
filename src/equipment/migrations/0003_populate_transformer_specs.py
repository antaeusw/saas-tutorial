from django.db import migrations

def populate_transformer_specs(apps, schema_editor):
    TransformerSpecs = apps.get_model('equipment', 'TransformerSpecs')
    
    transformer_data = [
        {
            'transformer_type': 'Dry-Type',
            'application': 'Indoor applications, data centers',
            'core_losses_percent': 0.0030,  # 0.30%
            'load_losses_percent': 0.0110,  # 1.10%
        },
        {
            'transformer_type': 'Oil-Filled',
            'application': 'Utility distribution, large power',
            'core_losses_percent': 0.0020,  # 0.20%
            'load_losses_percent': 0.0095,  # 0.95%
        },
        {
            'transformer_type': 'Cast Resin',
            'application': 'Indoor, medium voltage applications',
            'core_losses_percent': 0.0025,  # 0.25%
            'load_losses_percent': 0.0110,  # 1.10%
        },
        {
            'transformer_type': 'Pad-Mounted',
            'application': 'Outdoor distribution systems',
            'core_losses_percent': 0.0023,  # 0.23%
            'load_losses_percent': 0.0103,  # 1.03%
        },
        {
            'transformer_type': 'K-Rated',
            'application': 'Harmonic-rich environments',
            'core_losses_percent': 0.0033,  # 0.33%
            'load_losses_percent': 0.0138,  # 1.38%
        },
        {
            'transformer_type': 'DOE Compliant',
            'application': 'Energy-efficient applications',
            'core_losses_percent': 0.0018,  # 0.18%
            'load_losses_percent': 0.0078,  # 0.78%
        },
    ]
    
    for data in transformer_data:
        TransformerSpecs.objects.create(**data)


def reverse_populate_transformer_specs(apps, schema_editor):
    TransformerSpecs = apps.get_model('equipment', 'TransformerSpecs')
    
    transformer_types = [
        'Dry-Type',
        'Oil-Filled',
        'Cast Resin',
        'Pad-Mounted',
        'K-Rated',
        'DOE Compliant',
    ]
    
    TransformerSpecs.objects.filter(transformer_type__in=transformer_types).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0001_initial'),  # Make sure to update this to your actual previous migration
    ]

    operations = [
        migrations.RunPython(
            populate_transformer_specs,
            reverse_populate_transformer_specs
        ),
    ] 