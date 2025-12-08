import numpy as np
from .Algorithm import Algorithm

class Stellarator(Algorithm):
    def __init__(self, ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants):
        super().__init__(ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants)
    
    def run(self, inputs: dict) -> float:
        """
        Executes the algorithm specified by the name in the instance variables.
        
        Parameters:
        inputs (dict): Dictionary of input variables required for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        """
        # run the algorithm use self.name not self.alg_name
        return self._run_algorithm(self.name, [inputs[var] for var in self.variables.split(",")])

    def _run_algorithm(self, alg_name: str, variables: list) -> float:
        """
        Runs the specified algorithm with given variables.
        
        Parameters:
        alg_name (str): The name of the algorithm to run.
        variables (list): List of input variables for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        """
        try:
            algorithm = getattr(self, alg_name)
            return algorithm(*variables)
        except AttributeError:
            raise ValueError(f"Algorithm {alg_name} not found")


    @staticmethod
    #calaintmass: TF INTERCOIL STRUCTURE MASS CALCULATION
    def stcalaintmass(st_f_b, denstl, intercoil_surface):
        calaintmass = 0.18e0 * st_f_b**2 * intercoil_surface * denstl
        return calaintmass
    
    @staticmethod
    #calintercoil_surface: INTERCOIL SURFACE AREA
    def stcalintercoil_surface(stella_config_coilsurface, st_f_r, tftort, stella_config_coillength, st_f_n):
        calintercoil_surface = (
                stella_config_coilsurface * st_f_r**2
                - tftort
                * stella_config_coillength
                * st_f_r
                * st_f_n)
        return calintercoil_surface
    
    @staticmethod
    #calclgsmass: CALCULATION OF TF COIL GRAVITY SUPPORT STRUCTURE
    def stcalclgsmass(aintmass):
        calclgsmass = 0.2*aintmass
        return calclgsmass
