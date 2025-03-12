from django.contrib import admin

# Register your models here.
from .models import *

class EnergyResultAdmin(admin.ModelAdmin):
    list_display = ('project', 'E_IT_input_kWh', 'E_DC_input_kWh', 'PUE_calc_input_rounded')
    list_editable = ('E_IT_input_kWh', 'E_DC_input_kWh')
    fields = ('E_IT_input_kWh', 'E_DC_input_kWh', 'PUE_calc_input_rounded')
    readonly_fields = ('PUE_calc_input_rounded',)

admin.site.register(Datacenter)
admin.site.register(Project)
admin.site.register(EnergyResult, EnergyResultAdmin)
admin.site.register(UPS)
admin.site.register(Transformer) 
admin.site.register(Lighting)
admin.site.register(Datahall)
admin.site.register(CRAH)
admin.site.register(CHWPump)
admin.site.register(ChilledWaterSetting)
admin.site.register(Chiller)

