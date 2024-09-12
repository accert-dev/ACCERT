import sys
import os

src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)
from utility_accert import Utility_methods 
import pytest


ut = Utility_methods()
ut.acc_tabl = 'account'
ut.cel_tabl = 'cost_element'
ut.var_tabl = 'variable'
ut.alg_tabl = 'algorithm'
ut.esc_tabl = 'escalation'
ut.fac_tabl = 'facility'

print(dir(ut))
def test_util_methods(cursor):
    """  Test the utility methods. Nothing should be returned. But the methods should run and print all 
    the tables. if using pytest -s, the output will be printed."""
    assert ut.extract_affected_cost_elements(cursor)==None
    assert ut.extract_changed_cost_elements(cursor)==None
    assert ut.extract_user_changed_variables(cursor)==None
    assert ut.print_account(cursor)==None
    assert ut.print_algorithm(cursor)==None
    assert ut.print_cost_element(cursor)==None
    assert ut.print_escalation(cursor)==None
    assert ut.print_facility(cursor)==None
    assert ut.print_leveled_accounts(cursor)==None
    assert ut.print_updated_cost_elements(cursor)==None
    assert ut.print_user_request_parameter(cursor)==None
    assert ut.print_variable(cursor)==None
