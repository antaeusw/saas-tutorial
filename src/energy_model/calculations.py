class EnergyCalculations:
    """Service for handling complex energy calculations across multiple models"""
    
    def __init__(self, project):
        self.project = project
    
    def calculate_all(self):
        """Run all calculations in the correct order"""
        self.calculate_PUE_input() #for the PUE bassed on E_IT_input_kWh and E_DC_input_kWh
        self.calculate_ups_losses()
        self.calculate_transformer_losses()
        #self.calculate_lighting_energy()
        #self.calculate_crah_energy()
        #self.calculate_chw_pump_energy()
        #self.calculate_chiller_energy()
        #self.calculate_total_energy()
        self.calculate_PUE_input()
        self.calculate_pue()
    
    def calculate_ups_losses(self):
        # Implementation here
        pass
    
    def calculate_transformer_losses(self):
        # Implementation here
        
        pass
    
    # Other calculation methods...
    
    def calculate_PUE_input(self):
        """
        Calculate PUE based on the input values of E_IT_input_kWh and E_DC_input_kWh
        Can only be calculated if both E_IT_input_kWh and E_DC_input_kWh are set.
        """
        energy_results = self.project.energy_results
        if (energy_results.E_IT_input_kWh and energy_results.E_DC_input_kWh):
            energy_results.PUE_calc_input = energy_results.E_DC_input_kWh / energy_results.E_IT_input_kWh
            

    def calculate_pue(self):
        """Calculate PUE based on total facility energy and IT energy"""
        energy_results = self.project.energy_results
        if energy_results.E_IT_input_kWh and energy_results.E_DC_calc_kWh:
            energy_results.PUE_calc = energy_results.E_DC_calc_kWh / energy_results.E_IT_input_kWh
            