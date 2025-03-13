from equipment.models import LightingSpecs, LightingControlSpecs

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
        # Implementation here
        
        pass
    
    def calculate_lighting_energy(self):
        """
        Calculate lighting energy consumption based on lighting load and data hall area.
        If lighting_load_input_Wm2 is provided, use that value instead of the default.
        If on_for_hoursyear is provided, use that value instead of the default from lighting controls.
        Formula: lighting_energy_kWh = lighting_load_Wm2 * data_hall_area_m2 * hours_per_year / 1000
        """
       #Check if the project has a lighting configuration
        if not hasattr(self.project, 'lighting'):
            print("Project has no lighting configuration")
            return
        
        lighting = self.project.lighting
        
        # Access the datahall for area information
        if not hasattr(self.project, 'datahall'):
            print("Project has no datahall configuration")
            return
        
        datahall = self.project.datahall
        
        # Determine lighting load (W/m²)
        if lighting.lighting_type is not None:
            if lighting.lighting_load_input_Wm2 is not None:
                lighting.lighting_load_Wm2 = lighting.lighting_load_input_Wm2
            else:
                qs = LightingSpecs.objects.filter(lighting_type=lighting.lighting_type).first()
                lighting.lighting_load_Wm2 = qs.lighting_load_Wm2
        
        # Determine hours per year based on lighting controls
        hours_per_year = 8760  # Default to 24/7 operation (365 days * 24 hours)
        
        if lighting.on_for_hoursyear is not None:
            # Use manually input hours if provided
            hours_per_year = lighting.on_for_hoursyear
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
                energy_results.save()
                print(f"Lighting energy updated: {energy_results.E_lighting_calc_kWh} kWh")
    
    def calculate_PUE_input(self):
        """
        Calculate PUE based on the input values of E_IT_input_kWh and E_DC_input_kWh
        Can only be calculated if both E_IT_input_kWh and E_DC_input_kWh are set.
        """
        energy_results = self.project.energy_results
        if (energy_results.E_IT_input_kWh and energy_results.E_DC_input_kWh):
            energy_results.PUE_calc_input = energy_results.E_DC_input_kWh / energy_results.E_IT_input_kWh
            

    def calculate_E_DC_calc(self):
        """Calculate E_DC_calc based on all energy components"""
        energy_results = self.project.energy_results
        energy_results.E_DC_calc_kWh = (
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
        energy_results.E_un_accounted_calc_kWh = energy_results.E_DC_input_kWh - energy_results.E_DC_calc_kWh
                    

    def calculate_pue(self):
        """Calculate PUE based on total facility energy and IT energy"""
        energy_results = self.project.energy_results
        if energy_results.E_IT_input_kWh and energy_results.E_DC_calc_kWh:
            energy_results.PUE_calc = energy_results.E_DC_calc_kWh / energy_results.E_IT_input_kWh
            