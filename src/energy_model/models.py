from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from .calculations import EnergyCalculations
from equipment.models import LightingSpecs, LightingControlSpecs

# Create your models here.

class Datacenter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
      
    def __str__(self):
        return self.name

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    datacenter = models.ForeignKey(Datacenter, on_delete=models.CASCADE, related_name='projects')
    project_name = models.CharField(max_length=255)

    def __str__(self):
        return self.project_name

    def recalculate_energy(self):
        """Trigger all energy calculations for this project"""
        calculator = EnergyCalculations(self)
        calculator.calculate_all()

# Energy calculation results model
class EnergyResult(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='energy_results')
    E_IT_input_kWh = models.FloatField(default=0, help_text="The annual energy usage of the IT equipment in kWh")
    E_DC_input_kWh = models.FloatField(default=0, help_text="The annual energy usage of the datacenter in kWh")
    
    PUE_calc_input = models.FloatField(editable=False, null=True, blank=True, help_text="calculated based on E_DC_input_kWh and E_IT_input_kWh")
    
    E_DC_calc_kWh = models.FloatField(editable=False, null=True, blank=True) #calculated as the sum of E_IT_input_kWh and all the other energy usage values below.
        
    E_chiller_calc_kWh = models.FloatField(editable=False, default=0, help_text="Only calculated if the system includes chillers")
    E_cooling_tower_calc_kWh = models.FloatField(editable=False, default=0, help_text="Only calculated when CTs are present")
    E_pump_cw_calc_kWh = models.FloatField(editable=False, default=0, help_text="Condenser water pumps calculation")
    E_pump_chw_primary_calc_kWh = models.FloatField(editable=False, default=0, help_text="Only calculated if chilled water is present")
    E_pump_chw_secondary_calc_kWh = models.FloatField(editable=False, default=0, help_text="Only calculated if chilled water is present")
    E_CRAH_calc_kWh = models.FloatField(editable=False, default=0)
    E_CRAC_calc_kWh = models.FloatField(editable=False, default=0)
    E_MAU_calc_kWh = models.FloatField(editable=False, default=0, help_text="MAU may or may not include hum and dehum")
    E_Humidifier_InRoom_kWh = models.FloatField(editable=False, default=0)
    E_Dehum_InRoom_kWh = models.FloatField(editable=False, default=0)
    E_UPS_calc_kWh = models.FloatField(editable=False, default=0)
    E_TX_calc_kWh = models.FloatField(editable=False, default=0)
    E_generator_heating_calc_kWh = models.FloatField(editable=False, default=0)
    E_lighting_calc_kWh = models.FloatField(editable=False, default=0)
    E_cable_losses_calc_kWh = models.FloatField(editable=False, default=0)
    E_un_accounted_calc_kWh = models.FloatField(editable=False, default=0)
    
    PUE_calc = models.FloatField(editable=False, null=True, blank=True, help_text="Calculated based on E_IT_input_kWh and the calculated E_DC value. This is partial PUE if any subcomponent isn´t yet calculated")
    
    def __str__(self):
        return f"{self.project.project_name}"

    def save(self, *args, **kwargs):
        """Override save to trigger all energy calculations when relevant fields change"""
        
        # Trigger all energy calculations when relevant fields change
        if hasattr(self, 'project' ): #and
            calculator = EnergyCalculations(self.project)
            calculator.calculate_all()
            print(f"PUE_input calculated", self.PUE_calc_input)
        super().save(*args, **kwargs)
    
    @property
    def PUE_calc_input_rounded(self):
        """Return PUE value rounded to 3 decimal places"""
        if self.PUE_calc_input is not None:
            return round(self.PUE_calc_input, 3)
        return None
    
    @property
    def PUE_calc_rounded(self):
        """Return PUE value rounded to 3 decimal places"""
        if self.PUE_calc is not None:
            return round(self.PUE_calc, 3)
        return None
        

@receiver(post_save, sender=Project)
def create_energy_result(sender, instance, created, **kwargs):
    """Create EnergyResult instance when a new Project is created"""
    if created:
        EnergyResult.objects.create(
            project=instance,
        )

# Component-specific models

class UPS(models.Model):
    # UPS Configuration choices
    OPERATING_MODE_CHOICES = [
        ('Double Conversion', 'Double Conversion'),
        ('Eco Mode', 'Eco Mode'),
        # Add other modes as needed
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='UPS_System')
    model_name = models.CharField(max_length=255)
    installed_capacity_kW = models.FloatField(validators=[MinValueValidator(0)])
    utilization_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], 
                                           help_text="Calculated based on installed capacity and actual IT load")
    operating_mode = models.CharField(max_length=100, choices=OPERATING_MODE_CHOICES)
    efficiency_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         help_text="Interpolate efficiency from table and apply operating mode modifiers")

    def calculate_utilization_percent(self):
        """Calculate UPS utilization percentage based on IT load and installed capacity"""
        project_energy = self.project.energy_results
        if self.installed_capacity_kW and project_energy.E_IT_input_kWh:
            return (project_energy.E_IT_input_kWh / self.installed_capacity_kW) * 100
        return 0
    
    def calculate_ups_losses(self):
        """Calculate UPS energy losses based on efficiency and load"""
        project_energy = self.project.energy_results
        if project_energy.E_IT_input_kWh and self.efficiency_percent:
            efficiency_decimal = self.efficiency_percent / 100
            # UPS output = IT load
            # UPS input = IT load / efficiency
            # UPS losses = UPS input - IT load
            ups_input = project_energy.E_IT_input_kWh / efficiency_decimal
            return ups_input - project_energy.E_IT_input_kWh
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to update calculated fields"""
        self.utilization_percent = self.calculate_utilization_percent()
        super().save(*args, **kwargs)
        
        # Update related energy results if they exist
        try:
            energy_results = self.project.energy_results
            energy_results.E_UPS_calc_kWh = self.calculate_ups_losses()
            energy_results.save()
        except EnergyResult.DoesNotExist:
            pass

class Transformer(models.Model):
    TRANSFORMER_TYPE_CHOICES = [
        ('Dry-Type', 'Dry-Type'),
        ('Oil Filled', 'Oil Filled'),
        ('Cast Resin', 'Cast Resin'),
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='transformer')
    transformer_type = models.CharField(max_length=100, choices=TRANSFORMER_TYPE_CHOICES)
    transformer_unit_capacity_kW = models.FloatField(validators=[MinValueValidator(0)])
    quantity_installed_number = models.PositiveIntegerField()
    total_installed_capacity_kW = models.FloatField(validators=[MinValueValidator(0)], 
                                                  help_text="Including redundancy")
    E_DC_power_kW = models.FloatField(validators=[MinValueValidator(0)])
    average_utilization = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    core_loss_factor_percent = models.FloatField(validators=[MinValueValidator(0)])
    load_loss_factor_percent = models.FloatField(validators=[MinValueValidator(0)])
    TX_total_loss_factor_percent = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True,
                                                   help_text="= k (Core Loss %) + (Load loss %) x (Actual Load kW / Rated Load kW)")
    TX_total_loss_kW = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)

class Lighting(models.Model):
  
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='lighting')
    lighting_type = models.CharField(
        max_length=100,
        choices=[], 
        help_text="Select the type of lighting from the dropdown to determine the lighting load"
        ) #dropdown handled in admin.py / in form
    lighting_load_input_Wm2 = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)], 
                    help_text="Input the lighting load in W/m2 to override the default value")
    lighting_load_Wm2 = models.FloatField(editable=False, null=True, blank=True, validators=[MinValueValidator(0)], 
                    help_text="Look up table based on type of lighting") #lookup handled in calculations.py
    lighting_controls = models.CharField(
        max_length=100, 
        choices=[], 
        help_text="Select the type of lighting control to determine hours per year"
        ) #dropdown handled in admin.py / in form
    on_for_hoursyear = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)], 
                    help_text="Hours per year the lighting is on. If provided, this overrides the default value from lighting controls.")
   
    def __str__(self):
        return f"{self.project.project_name}"

    def save(self, *args, **kwargs):
        """Override save to trigger energy calculations"""
        if hasattr(self, 'project' ): 
            calculator = EnergyCalculations(self.project)
            calculator.calculate_lighting_energy()
            
        super().save(*args, **kwargs)

class Datahall(models.Model):
    AIR_COOLING_TYPE_CHOICES = [
        ('CRAH (chilled water)', 'CRAH (chilled water)'),
        ('CRAC (DX)', 'CRAC (DX)'),
        # Add other types as needed
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='datahall')
    area_m2 = models.FloatField(validators=[MinValueValidator(0)], help_text="Required for lighting calculation")
    design_load_density_kWm2 = models.FloatField(validators=[MinValueValidator(0)], 
                                               help_text="Optional input for CRAH calculations")
    design_IT_load_kW = models.FloatField(validators=[MinValueValidator(0)])
    server_dT_in_Kelvin = models.FloatField(validators=[MinValueValidator(0)], default=12, 
                                           help_text="Assumption default")
    type_air_cooling = models.CharField(max_length=100, choices=AIR_COOLING_TYPE_CHOICES,
                                      help_text="Determines what config is used for cooling energy calculations")

class CRAH(models.Model):
    REDUNDANCY_CHOICES = [
        ('N+1', 'N+1'),
        ('N+20%', 'N+20%'),
        ('2N', '2N'),
        # Add other redundancy options as needed
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='crah')
    cooling_capacity_in_kW = models.FloatField(validators=[MinValueValidator(0)])
    rated_airflow_m3s = models.FloatField(validators=[MinValueValidator(0)])
    max_fan_power_kW = models.FloatField(validators=[MinValueValidator(0)])
    average_dT_in_Kelvin = models.FloatField(validators=[MinValueValidator(0)], 
                                           help_text="Input or assumption depending on datahall containment level")
    supply_air_temperature_in_C = models.FloatField(validators=[MinValueValidator(0)])
    return_air_temperature_avg_in_C = models.FloatField(validators=[MinValueValidator(0)], 
                                                      help_text="Supply air temperature plus average delta T")
    air_to_water_approach_temperature_in_C = models.FloatField(validators=[MinValueValidator(0)])
    chilled_water_exit_temperature_in_C = models.FloatField(validators=[MinValueValidator(0)], 
                                                          help_text="RAT average minus the air-water-approach")
    required_airflow_m3s = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    min_fan_speed_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    design_redundancy = models.CharField(max_length=50, choices=REDUNDANCY_CHOICES)
    redundancy_factor = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    quantity_for_N_redundancy = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    quantity_installed_estimate = models.IntegerField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    quantity_installed_input = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True,
                                                 help_text="If user inputs a figure then we use this in calculations")
    quantity_installed_used = models.IntegerField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    maximum_total_CRAH_airflow_m3s = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    average_fan_speed_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], 
                                                editable=False, null=True, blank=True)
    average_fan_power_kW = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    total_fan_power_kW = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)


class CHWPump(models.Model):
    PUMP_TYPE_CHOICES = [
        ('Inline', 'Inline'),
        ('Close Coupled', 'Close Coupled'),
        # Add other types as needed
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='chw_pump')
    pump_type = models.CharField(max_length=100, choices=PUMP_TYPE_CHOICES)
    pump_design_thermal_load_kW = models.FloatField(validators=[MinValueValidator(0)], 
                                                  help_text="Design IT load plus additional thermal load")
    qty_pumps_running_in_parallel = models.IntegerField(validators=[MinValueValidator(0)], 
                                                      help_text="Normally designed for N+1, 1 pump running")
    design_pressure_kPa = models.FloatField(validators=[MinValueValidator(0)], 
                                          help_text="Typical design point is 250-350kPA")
    design_efficiency_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], 
                                                help_text="Typical design point is 50% at peak pressure delivery")
    design_pump_flow_kgs = models.FloatField(validators=[MinValueValidator(0)])
    volume_flow_m3s = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    pump_rated_power_kW = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)
    minimum_pump_speed_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    chilled_water_load_kW = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True,
                                            help_text="Sum of IT, CRAH fans, lighting, and UPS cooling")
    chilled_water_operating_dT_in_Kelvin = models.FloatField(validators=[MinValueValidator(0)], 
                                                           help_text="Based on approach temp and average RAT inputs")
    chilled_water_flow_kgs = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True,
                                             help_text="Actual flow calc using load and Q = m cp dT")
    chilled_water_flow_per_pump_kgs = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True,
                                                      help_text="Divided by number of pumps operating")
    pump_speed_un_limited_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], 
                                                    editable=False, null=True, blank=True)
    pump_speed_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], 
                                         editable=False, null=True, blank=True)
    pump_power_kW = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)

class ChilledWaterSetting(models.Model):
    GLYCOL_CHOICES = [
        ('0%', '0%'),
        ('10%', '10%'),
        ('20%', '20%'),
        ('30%', '30%'),
        ('40%', '40%'),
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='chilled_water_settings')
    glycol_content = models.CharField(max_length=20, choices=GLYCOL_CHOICES, 
                                     help_text="Modifies the specific heat capacity")
    chw_supply_temp_degC = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(25)])
    cp_water_kJkg_1K = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True,
                                       help_text="Index matched to the reference table")
    design_delta_T_in_Kelvin = models.FloatField(validators=[MinValueValidator(0)], 
                                               help_text="Typically ranges from 6 to 10C")

class Chiller(models.Model):
    WATER_SIDE_ECONOMIZER_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='chiller_settings')
    chiller_redundancy_n_plus = models.IntegerField(validators=[MinValueValidator(0)], 
                                                  help_text="Insert the N+ number")
    water_side_economizer = models.CharField(max_length=10, choices=WATER_SIDE_ECONOMIZER_CHOICES)
    cooling_capacity_kW_thermal = models.FloatField(validators=[MinValueValidator(0)], 
                                                  help_text="Thermal design capacity of the chillers")
    minimum_CHWS_temp_degC = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(30)])
    maximum_CHWS_temp_degC = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(30)])
    economizer_approach_in_Kelvin = models.FloatField(validators=[MinValueValidator(0)], 
                                                    help_text="Approach between CHWS and Ambient temp for economizer")
    SCOP = models.FloatField(validators=[MinValueValidator(0)], 
                           help_text="Will be inferred from model selection and weather")
    total_chilled_water_load_kW_thermal = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True,
                                                          help_text="Excludes TX room as assumed has natural ventilation")
    chiller_average_power_kW = models.FloatField(validators=[MinValueValidator(0)], editable=False, null=True, blank=True)

    
    
    


