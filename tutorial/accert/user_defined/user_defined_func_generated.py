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
        # run the algorithm using self.name not self.alg_name
        return self._run_algorithm(self.name, [inputs[var.strip()] for var in self.variables.split(",") if var.strip()])
    
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
            raise ValueError(f"Algorithm {{alg_name}} not found")
    
    @staticmethod
    # ud211: description of ud211 optional
    def ud211(v1, v2, v3):
        # TODO: Implement the logic for ud211
        # The output unit should be million
        pass
    
    @staticmethod
    # ud212: description of ud212 optional
    def ud212(v5, v8, v7):
        # TODO: Implement the logic for ud212
        # The output unit should be dollar
        pass
    
    @staticmethod
    # ud2131: description of ud2131 optional
    def ud2131(v3, v2, v5):
        # TODO: Implement the logic for ud2131
        # The output unit should be million
        pass
    
    @staticmethod
    # ud2132: description of ud2132 optional
    def ud2132(v8, v4, v6):
        # TODO: Implement the logic for ud2132
        # The output unit should be million
        pass
    
    @staticmethod
    # ud_cal_v6: description of ud_cal_v6 optional
    def ud_cal_v6(v1, v3):
        # TODO: Implement the logic for ud_cal_v6
        # The output unit should be million
        pass
