
class Algorithm:
    # ind, alg_name, alg_for, alg_description, alg_python, alg_formulation, alg_units, variables, constants
    def __init__(self, ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants):
        self.ind = ind
        self.name = alg_name
        self.for_ = alg_for
        self.description = alg_description
        self.formulation = alg_formulation
        self.units = alg_units
        self.variables = variables
        self.constants = constants


    def __repr__(self):
        return f"Algorithm({self.ind}, {self.name}, {self.for_}, {self.description}, {self.formulation}, {self.units}, {self.variables}, {self.constants})"
    
    def run(self, inputs):
        # Run the algorithm
        pass

    def _run_algorithm(self, alg_name, variables):
        # Run the algorithm
        pass
