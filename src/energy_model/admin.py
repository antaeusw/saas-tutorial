from django.contrib import admin
from django import forms
from .models import *

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

@admin.register(Lighting)
class LightingAdmin(admin.ModelAdmin):
    list_display = ('project', 'lighting_type', 'lighting_controls', 'on_for_hoursyear')
    search_fields = ('project__project_name',)
    fields = ('project', 'lighting_type', 'lighting_load_input_Wm2', 'lighting_load_Wm2','lighting_controls', 'on_for_hoursyear_input', 'on_for_hoursyear',)
    readonly_fields = ('lighting_load_Wm2', 'on_for_hoursyear',)

@admin.register(Transformer)
class TransformerAdmin(admin.ModelAdmin):
    list_display = ('project', 'transformer_type', 'transformer_unit_capacity_kW', 'E_DC_power_kW', 'TX_total_loss_kW')
    search_fields = ('project__project_name',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'transformer_type', 'transformer_unit_capacity_kW', 'quantity_installed_number', 'total_installed_capacity_kW')
        }),
        ('Load Information', {
            'fields': ('E_DC_power_kW', 'average_utilization')
        }),
        ('Loss Factors', {
            'fields': ('core_loss_factor_percent_input', 'load_loss_factor_percent_input', 'core_loss_factor_percent', 'load_loss_factor_percent')
        }),
        ('Calculated Results', {
            'fields': ('TX_total_loss_factor_percent', 'TX_total_loss_kW')
        }),
    )
    readonly_fields = ('core_loss_factor_percent', 'load_loss_factor_percent', 'TX_total_loss_factor_percent', 'TX_total_loss_kW', 'E_DC_power_kW', 'total_installed_capacity_kW', 'average_utilization')

admin.site.register(Datacenter)
admin.site.register(Project)
admin.site.register(EnergyResult, EnergyResultAdmin)
admin.site.register(UPS)
admin.site.register(Datahall)
admin.site.register(CRAH)
admin.site.register(CHWPump)
admin.site.register(ChilledWaterSetting)
admin.site.register(Chiller)

