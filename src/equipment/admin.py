from django.contrib import admin
from .models import *

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


@admin.register(TransformerSpecs)
class TransformerSpecsAdmin(admin.ModelAdmin):
    list_display = ('id', 'transformer_type', 'application', 'core_losses_percent', 'load_losses_percent')
    list_editable = ('transformer_type', 'application', 'core_losses_percent', 'load_losses_percent',)
    search_fields = ('transformer_type',)


