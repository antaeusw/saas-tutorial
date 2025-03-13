from django.contrib import admin
from django import forms
from .models import *
from equipment.models import LightingSpecs, LightingControlSpecs

class EnergyResultAdmin(admin.ModelAdmin):
    list_display = ('project', 'E_IT_input_kWh', 'E_DC_input_kWh', 'PUE_calc_input_rounded')
    list_editable = ('E_IT_input_kWh', 'E_DC_input_kWh')
    
    fieldsets = (
        ('Input Values', {
            'fields': ('E_IT_input_kWh', 'E_DC_input_kWh')
        }),
        ('PUE Results', {
            'fields': ('PUE_calc_input_rounded', 'PUE_calc_rounded', 'E_DC_calc_kWh', 'E_un_accounted_calc_kWh')
        }),
        ('Energy Calculations', {
            'classes': ('wide',),
            'description': 'Calculated energy consumption values for different components',
            'fields': (
                'E_lighting_calc_kWh',
                'E_UPS_calc_kWh',
                'E_TX_calc_kWh',
                'E_cable_losses_calc_kWh',
                'E_chiller_calc_kWh',
                'E_cooling_tower_calc_kWh',
                'E_pump_cw_calc_kWh',
                'E_pump_chw_primary_calc_kWh',
                'E_pump_chw_secondary_calc_kWh',
                'E_CRAH_calc_kWh',
                'E_CRAC_calc_kWh',
                'E_MAU_calc_kWh',
                'E_Humidifier_InRoom_kWh',
                'E_Dehum_InRoom_kWh',
                'E_generator_heating_calc_kWh',
            )
        }),
    )
    
    readonly_fields = (
        'PUE_calc_input_rounded',
        'E_DC_calc_kWh',
        'E_chiller_calc_kWh',
        'E_cooling_tower_calc_kWh',
        'E_pump_cw_calc_kWh', 
        'E_pump_chw_primary_calc_kWh',
        'E_pump_chw_secondary_calc_kWh',
        'E_CRAH_calc_kWh',
        'E_CRAC_calc_kWh',
        'E_MAU_calc_kWh',
        'E_Humidifier_InRoom_kWh',
        'E_Dehum_InRoom_kWh',
        'E_UPS_calc_kWh',
        'E_TX_calc_kWh',
        'E_generator_heating_calc_kWh',
        'E_lighting_calc_kWh',
        'E_cable_losses_calc_kWh',
        'E_un_accounted_calc_kWh',
        'PUE_calc_rounded',
    )

class LightingForm(forms.ModelForm):
    class Meta:
        model = Lighting
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the choices
        lighting_type_choices = [(instance.lighting_type, instance.lighting_type) 
                               for instance in LightingSpecs.objects.all()]
        lighting_control_choices = [(instance.control_type, instance.control_type) 
                                  for instance in LightingControlSpecs.objects.all()]
        
        # Set both fields to use Select widgets with their respective choices
        self.fields['lighting_type'].widget = forms.Select(choices=lighting_type_choices)
        self.fields['lighting_controls'].widget = forms.Select(choices=lighting_control_choices)
        
@admin.register(Lighting)
class LightingAdmin(admin.ModelAdmin):
    form = LightingForm
    list_display = ('project', 'lighting_type', 'lighting_controls', 'on_for_hoursyear')
    search_fields = ('project__project_name',)

admin.site.register(Datacenter)
admin.site.register(Project)
admin.site.register(EnergyResult, EnergyResultAdmin)
admin.site.register(UPS)
admin.site.register(Transformer) 
admin.site.register(Datahall)
admin.site.register(CRAH)
admin.site.register(CHWPump)
admin.site.register(ChilledWaterSetting)
admin.site.register(Chiller)

