class  Variable:
    def __init__(self, ind,	var_name,	var_description,	var_value,	var_unit,	var_alg,	var_need,   v_linked,	user_input):
        self.ind = ind
        self.name = var_name
        self.description = var_description
        self.value = var_value
        self.unit = var_unit
        self.alg = var_alg
        self.need = var_need
        self.linked = v_linked
        self.user_input = user_input
    

    def __repr__(self):
        return "Variable(%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.ind, self.name, self.description, self.value, self.unit, self.alg, self.need, self.linked, self.user_input)
