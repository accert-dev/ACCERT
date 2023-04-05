
class Account:
    def __init__(self, ind, code_of_account, account_description, total_cost, unit, level, main_subaccouts, supaccount, cost_elements, review_status):
        self.ind = ind
        self.code_of_account = code_of_account
        self.account_description = account_description
        self.total_cost = total_cost
        self.unit = unit
        self.level = level
        self.main_subaccouts = main_subaccouts
        self.supaccount = supaccount
        self.cost_elements = cost_elements
        self.review_status = review_status

    def __repr__(self):
        return "Account(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.ind, self.code_of_account, self.account_description, self.total_cost, self.unit, self.level, self.main_subaccouts, self.supaccount, self.cost_elements, self.review_status)