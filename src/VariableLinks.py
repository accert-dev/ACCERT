class  Variable_links:
    def __init__(self, ind,	variable,	var_ind,	ce_ind,	ce):
        self.ind = ind
        self.variable = variable
        self.var_ind = var_ind
        self.ce_ind = ce_ind
        self.ce = ce

    def __repr__(self):
        return "Variable_links(%s, %s, %s, %s, %s)" % (self.ind, self.variable, self.var_ind, self.ce_ind, self.ce)
