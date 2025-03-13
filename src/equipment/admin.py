from django.contrib import admin
from .models import LightingSpecs, LightingControlSpecs

@admin.register(LightingSpecs)
class LightingSpecsAdmin(admin.ModelAdmin):
    list_display = ('id', 'lighting_type', 'lighting_load_Wm2')
    list_editable = ('lighting_type', 'lighting_load_Wm2',)
    search_fields = ('lighting_type',)

@admin.register(LightingControlSpecs)
class LightingControlSpecsAdmin(admin.ModelAdmin):
    list_display = ('id', 'control_type', 'hours_per_year')
    list_editable = ('control_type', 'hours_per_year',)
    search_fields = ('control_type',)
