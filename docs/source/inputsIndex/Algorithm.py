
class Algorithm:
    def __init__(self, ind, alg_name, alg_for, alg_description, alg_python, alg_formulation, alg_units, variables, constants):
        self.ind = ind
        self.name = alg_name
        self.for_ = alg_for
        self.description = alg_description
        self.formulation = alg_formulation
        self.units = alg_units
        self.variables = variables
        self.constants = constants

    def __repr__(self):
        return "Algorithm(%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.ind, self.name, self.for_, self.description, self.formulation, self.units, self.variables, self.constants)

    def run(self, data):
        raise NotImplementedError
    def _run_alg(self, data):
        raise NotImplementedError
