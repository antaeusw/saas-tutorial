from equipment.models import LightingSpecs, LightingControlSpecs, TransformerSpecs
from termcolor import colored

class EnergyCalculations:
    """Service for handling complex energy calculations across multiple models"""
    
    def __init__(self, project):
        self.project = project
    
    def calculate_all(self):
        """Run all calculations in the correct order"""
        self.calculate_PUE_input() #for the PUE bassed on E_IT_input_kWh and E_DC_input_kWh
        self.calculate_ups_losses()
        self.calculate_transformer_losses()
        self.calculate_lighting_energy()
        #self.calculate_crah_energy()
        #self.calculate_chw_pump_energy()
        #self.calculate_chiller_energy()
        #self.calculate_total_energy()
        self.calculate_PUE_input()
        self.calculate_E_DC_calc()
        self.calculate_pue()
    
    def calculate_ups_losses(self):
        # Implementation here
        pass
    
    def calculate_transformer_losses(self):
        """
        To calculated Transformer_losses_kW, use the following formula:
        Transformer_losses_kW = k [ ( Core Loss %) + (Load loss %) x (Actual Load kW / Rated Load kW)]
        PL = Load losses (kW)
        k = Rated capacity of transformer (kW)
        L = Actual load (kW)
        LR = Rated load (kW)
        """
        # Check if the project has a transformer configuration
        if not hasattr(self.project, 'transformer'):
            print(colored("WARNING: Project has no transformer configuration", "light_yellow"))
            return
        
        transformer = self.project.transformer
       
       # Get the energy results for updating
        energy_results = self.project.energy_results
              
        # Update loss factors from specs if not manually input
        if transformer.transformer_type:
            if transformer.core_loss_factor_percent_input is not None:
                transformer.core_loss_factor_percent = transformer.core_loss_factor_percent_input
            else:
                transformer.core_loss_factor_percent = transformer.transformer_type.core_losses_percent
                
            if transformer.load_loss_factor_percent_input is not None:
                transformer.load_loss_factor_percent = transformer.load_loss_factor_percent_input
            else:
                transformer.load_loss_factor_percent = transformer.transformer_type.load_losses_percent
            
            core_loss_factor = transformer.core_loss_factor_percent
            load_loss_factor = transformer.load_loss_factor_percent

       # Calculate installed capacity of transformer
        if (transformer.transformer_unit_capacity_kW is not None and
            transformer.quantity_installed_number is not None):
            installed_capacity_kW = transformer.transformer_unit_capacity_kW * transformer.quantity_installed_number
            if not(transformer.total_installed_capacity_kW == installed_capacity_kW):
                transformer.total_installed_capacity_kW = installed_capacity_kW
                print(colored(f"SUCCESS! Transformer installed capacity updated to {installed_capacity_kW} kW", "green")) 
       
        # Calculate E_DC_power_kW
        if energy_results.E_DC_input_kWh is not None:
            E_DC_power_kW = energy_results.E_DC_input_kWh / 8760
            transformer.E_DC_power_kW = E_DC_power_kW
        #else (FUTURE IMPROVEMENT) calculate this from E_DC_calc_kWh with an iterative process until TX losses don´t change much.
        else:
            print(colored("WARNING: E_DC_input_kWh is not set, cannot calculate transformer losses", "light_yellow"))
            return

        # Calculate transformer losses
        average_utilization = E_DC_power_kW / installed_capacity_kW
        transformer.average_utilization = average_utilization
        total_loss_factor = core_loss_factor + (load_loss_factor * average_utilization)
        transformer.TX_total_loss_factor_percent = total_loss_factor  # Convert back to percentage
        
        # Calculate the total transformer losses in kW
        transformer_losses_kW = installed_capacity_kW * total_loss_factor
        transformer.TX_total_loss_kW = transformer_losses_kW
        
        # Calculate annual energy losses in kWh (assuming 24/7 operation)
        transformer_losses_kWh = transformer_losses_kW * 8760  # 8760 hours in a year
        
        # Update the energy results
        if not(energy_results.E_TX_calc_kWh == transformer_losses_kWh):
            energy_results.E_TX_calc_kWh = transformer_losses_kWh
            print(colored(f"SUCCESS! Transformer energy losses updated to {energy_results.E_TX_calc_kWh} kWh", "green"))
            energy_results.save()
    
    def calculate_lighting_energy(self):
        """
        Calculate lighting energy consumption based on lighting load and data hall area.
        If lighting_load_input_Wm2 is provided, use that value instead of the default.
        If on_for_hoursyear is provided, use that value instead of the default from lighting controls.
        Formula: lighting_energy_kWh = lighting_load_Wm2 * data_hall_area_m2 * hours_per_year / 1000
        """
       #Check if the project has a lighting configuration
        if not hasattr(self.project, 'lighting'):
            print(colored("WARNING: Project has no lighting configuration", "light_yellow"))
            return
        
        lighting = self.project.lighting
        
        # Access the datahall for area information
        if not hasattr(self.project, 'datahall'):
            print(colored("WARNING: Project has no datahall configuration", "light_yellow"))
            return
        
        datahall = self.project.datahall
        
        # Determine lighting load (W/m²)
        if lighting.lighting_type is not None:
            if lighting.lighting_load_input_Wm2 is not None:
                lighting.lighting_load_Wm2 = lighting.lighting_load_input_Wm2
            else:
                qs = LightingSpecs.objects.filter(lighting_type=lighting.lighting_type).first()
                if not(lighting.lighting_load_Wm2 == qs.lighting_load_Wm2):
                    lighting.lighting_load_Wm2 = qs.lighting_load_Wm2
                    print(colored(f"SUCCESS! Lighting load updated: {lighting.lighting_load_Wm2} W/m²", "green"))
        
        # Determine hours per year based on lighting controls
        hours_per_year = 8760  # Default to 24/7 operation (365 days * 24 hours)
        
        if lighting.on_for_hoursyear_input is not None:
            # Use manually input hours if provided
            hours_per_year = lighting.on_for_hoursyear_input
            lighting.on_for_hoursyear = hours_per_year
        elif lighting.lighting_controls is not None:
            # Otherwise look up from the LightingControlSpecs table
            control_specs = LightingControlSpecs.objects.filter(control_type=lighting.lighting_controls).first()
            if control_specs:
                hours_per_year = control_specs.hours_per_year
                # Update the lighting model with the hours from the specs
                lighting.on_for_hoursyear = hours_per_year
                
                    
        # Calculate lighting energy if we have both load and area
        if lighting.lighting_load_Wm2 is not None and datahall.area_m2 is not None:
            # Calculate lighting energy in kWh (W/m² * m² * hours / 1000)
            lighting_energy_kWh = (
                lighting.lighting_load_Wm2 * 
                datahall.area_m2 * 
                hours_per_year / 
                1000
            )
            #print(f"Lighting energy calculated: {lighting_energy_kWh} kWh")
            
            #Update the total energy results
            energy_results = self.project.energy_results
            if not(energy_results.E_lighting_calc_kWh == lighting_energy_kWh):
                energy_results.E_lighting_calc_kWh = lighting_energy_kWh
                print(colored(f"SUCCESS! Lighting energy updated to {energy_results.E_lighting_calc_kWh} kWh", "green"))
                energy_results.save()
                
    
    def calculate_PUE_input(self):
        """
        Calculate PUE based on the input values of E_IT_input_kWh and E_DC_input_kWh
        Can only be calculated if both E_IT_input_kWh and E_DC_input_kWh are set.
        """
        energy_results = self.project.energy_results
        
        if (energy_results.E_IT_input_kWh and energy_results.E_DC_input_kWh):
            PUE_calc_input = energy_results.E_DC_input_kWh / energy_results.E_IT_input_kWh
            if not(energy_results.PUE_calc_input == PUE_calc_input):
                energy_results.PUE_calc_input = PUE_calc_input
                print(colored(f"SUCCESS! PUE_input updated to {energy_results.PUE_calc_input}", "green"))

    def calculate_E_DC_calc(self):
        """Calculate E_DC_calc based on all energy components"""
        energy_results = self.project.energy_results
        E_DC_calc_kWh = (
                                energy_results.E_IT_input_kWh +
                                energy_results.E_chiller_calc_kWh +
                                energy_results.E_cooling_tower_calc_kWh +
                                energy_results.E_pump_cw_calc_kWh +
                                energy_results.E_pump_chw_primary_calc_kWh +
                                energy_results.E_pump_chw_secondary_calc_kWh +
                                energy_results.E_CRAH_calc_kWh +
                                energy_results.E_CRAC_calc_kWh +
                                energy_results.E_MAU_calc_kWh +
                                energy_results.E_Humidifier_InRoom_kWh +
                                energy_results.E_Dehum_InRoom_kWh +
                                energy_results.E_UPS_calc_kWh +
                                energy_results.E_TX_calc_kWh +
                                energy_results.E_generator_heating_calc_kWh +
                                energy_results.E_lighting_calc_kWh +
                                energy_results.E_cable_losses_calc_kWh
                                )
        if not(energy_results.E_DC_calc_kWh == E_DC_calc_kWh):
            energy_results.E_DC_calc_kWh = E_DC_calc_kWh
            print(colored(f"SUCCESS! E_DC_calc updated to {energy_results.E_DC_calc_kWh} kWh", "green"))
            
            E_un_accounted_calc_kWh = energy_results.E_DC_input_kWh - energy_results.E_DC_calc_kWh
            energy_results.E_un_accounted_calc_kWh = E_un_accounted_calc_kWh
        
    def calculate_pue(self):
        """Calculate PUE based on total facility energy and IT energy"""
        energy_results = self.project.energy_results
        PUE_calc = energy_results.E_DC_calc_kWh / energy_results.E_IT_input_kWh
        if not(energy_results.PUE_calc == PUE_calc):
            energy_results.PUE_calc = PUE_calc
            print(colored(f"SUCCESS! Calculated PUE updated to {energy_results.PUE_calc}", "green"))
