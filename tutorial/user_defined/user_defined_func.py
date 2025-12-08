import numpy as np
from .Algorithm import Algorithm

class user_defined_func(Algorithm):
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
    #ud211: User defined total cost 211
    def ud211(v1, v2, v3):
        return v1 + v2 + v3
    
    @staticmethod
    #ud212: User defined total cost 212
    def ud212(v5, v8, v7):
        some_calc = v5 * v8 + v7
        return some_calc
    
    @staticmethod
    #ud2131: User defined total cost 2131
    def ud2131(v3, v2, v5):
        some_var = v2 - v3
        other_var = some_var/200
        total_cost = other_var * v5
        return total_cost
    
    @staticmethod
    #ud2132: User defined total cost 2132
    def ud2132(v8, v4, v6):
        if v6 > 52:
            return v4*v8/999
        else:
            return v4*v8/1000

    @staticmethod
    #ud_cal_v6: User defined calculation for v6
    def ud_cal_v6(v1, v3):
        return v1 + v3