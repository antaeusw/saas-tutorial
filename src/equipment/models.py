from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class LightingSpecs(models.Model):
    lighting_type = models.CharField(max_length=100)
    lighting_load_Wm2 = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.lighting_type

class LightingControlSpecs(models.Model):
    """
    Model to store lighting control types and their associated hours per year
    """
    control_type = models.CharField(max_length=100)
    hours_per_year = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(8760)], 
                                      help_text="Number of hours per year the lighting is on")
    
    def __str__(self):
        return self.control_type
    
    class Meta:
        verbose_name = "Lighting Control Specification"
        verbose_name_plural = "Lighting Control Specifications"
