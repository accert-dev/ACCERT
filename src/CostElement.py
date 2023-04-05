class Cost_element:
    def __init__(self, ind,	cost_element,	cost_2011,	cost_1987,	cost_2017,	sup_cost_ele,	alg_names,	fun_unit,	variables,	account,	algno, updated):
        self.ind = ind
        self.cost_element = cost_element
        self.cost_2011 = cost_2011
        self.cost_1987 = cost_1987
        self.cost_2017 = cost_2017
        self.sup_cost_ele = sup_cost_ele
        self.alg_names = alg_names
        self.fun_unit = fun_unit
        self.variables = variables
        self.account = account
        self.algno = algno
        self.updated = updated

    def __repr__(self):
        return "Cost_element(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.ind, self.cost_element, self.cost_2011, self.cost_1987, self.cost_2017, self.sup_cost_ele, self.alg_names, self.fun_unit, self.variables, self.account, self.algno, self.updated)