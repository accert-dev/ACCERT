import numpy as np
from .Algorithm import Algorithm

class FusionFunc(Algorithm):
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
    def acc211(csi, lsa, cland):
        lsa = int(lsa)
        cmlsa=[0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc211= csi*cmlsa[lsa-1] + cland
        return acc211

    def acc2171(ucad, admvol, exprb, lsa):
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0] 
        acc2171 = 1.0e-6*ucad*admvol**exprb* cmlsa[lsa - 1]
        return acc2171