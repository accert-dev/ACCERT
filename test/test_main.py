import sys
import os

src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)
from utility_accert import Utility_methods 
from Main import Accert
import pytest


ut = Utility_methods()
accert_path = os.path.dirname(os.getcwd())
input_path = os.path.join(os.getcwd(), 'accert_unit_test_input.son')
accert = Accert(input_path, accert_path)
accert.ref_model = 'pwr12-be'
accert.acc_tabl = 'account'
accert.cel_tabl = 'cost_element'
accert.var_tabl = 'variable'
accert.alg_tabl = 'algorithm'
accert.esc_tabl = 'escalation'
accert.fac_tabl = 'facility'

def test_get_current_COAs(cursor):
    """  Test the main function. """
    expect_output = (['21', '22', '23', '24', '25', '26'], 
            [(2,), (25,), (80,), (87,), (94,), (100,)]) 
    assert accert.get_current_COAs(cursor, '2') == expect_output

def test_update_account_before_insert(cursor):
    """ test function update_account_before_insert """
    # set up an empty place to insert the new COA
    assert accert.update_account_before_insert(cursor, 24) == None
    # ind 24 will be empty
    cursor.execute("""SELECT *
                    FROM account
                    WHERE ind = 24;""")
    assert cursor.fetchall()==[]

def test_insert_new_COA(cursor):
    """ test function insert_new_COA """
    # insert a new COA with ind 24 and name "new"
    assert accert.insert_new_COA(cursor, 24, "218", 3, 'new_coa', 'new des', 20 ) == None
    # check if the new COA is added
    cursor.execute("""SELECT *
                    FROM account
                    WHERE ind = 24;""")
    #NOTE if ind=24 might get 2 rows, one for the new COA and one for the original COA? might need to check

    expect_output = (24, 'new_coa', 'new des', 20.0, 3, '218', 'Added', 0.0, None, None, None, None)
    assert expect_output in cursor.fetchall()

def test_update_input_variable(cursor):
    """ test function update_input_variable """
    # update the input variable "c_213_fac" to 1.8 million for pwr12be
    assert accert.update_input_variable(cursor,"c_213_fac",0,"million")==None
    # check if the value is updated
    cursor.execute("""SELECT var_name,var_value, var_unit
                    FROM variable 
                    WHERE var_name = "c_213_fac";""")
    expect_output = ('c_213_fac',  0.0, 'million') 
    assert expect_output in cursor.fetchall()

def test_update_variable_info_on_name(cursor):
    """ test function update_variable_info_on_name """
    # update the variable "c_213_fac" to 1.8 for pwr12be
    assert accert.update_variable_info_on_name(cursor,"c_213_fac",0,"million")==None
    # check if the value is updated
    cursor.execute("""SELECT var_name,var_value, var_unit
                    FROM variable
                    WHERE var_name = "c_213_fac";""")
    expect_output = ('c_213_fac',  0.0, 'million') 
    assert expect_output in cursor.fetchall()

def test_update_super_variable(cursor):
    """ test function update_super_variable also test get_var_value_by_name"""
    # update the super variable "n_231" for pwr12be
    assert accert.update_super_variable(cursor,"n_231")==None
    # check if the value is updated only check the user_input column
    cursor.execute("""SELECT var_name,user_input
                    FROM variable 
                    WHERE var_name = "n_231";""")
    expect_output = ('n_231', 1)
    assert expect_output in cursor.fetchall()

def test_update_total_cost(cursor):
    """ test function update_total_cost """
    # update the total cost for pwr12be
    assert accert.update_total_cost(cursor,"211", 1000, "thousand")==None
    # check if the value is updated
    cursor.execute("""SELECT code_of_account, total_cost
                    FROM account 
                    WHERE code_of_account = "211";""")
    expect_output = ('211',  1000000.0) 
    assert expect_output in cursor.fetchall()

def test_update_total_cost_on_name(cursor):
    """ test function update_total_cost_on_name """
    # update the total cost for pwr12be
    assert accert.update_total_cost_on_name(cursor, "211", 1000000)==None
    # check if the value is updated
    cursor.execute("""SELECT code_of_account, total_cost
                    FROM account 
                    WHERE code_of_account = "211";""")
    expect_output = ('211',  1000000.0 ) 
    assert expect_output in cursor.fetchall()

def test_update_cost_element_on_name(cursor):
    """ test function update_cost_element_on_name """
    # update the cost element "211_fac" for pwr12be
    assert accert.update_cost_element_on_name(cursor, "211_fac", 2000)==None
    # check if the value is updated
    cursor.execute("""SELECT cost_element, cost_2017, updated
                    FROM cost_element
                    WHERE cost_element = "211_fac";""")
    expect_output = ('211_fac', 2000.0, 1)
    assert expect_output in cursor.fetchall()

def test_roll_up_cost_elements(cursor):
    """ test function roll_up_cost_elements, this function will roll up the cost 
    element for pwr12be, also test the function roll_up_cost_elements_by_level"""
    # roll up the cost element for pwr12be
    assert accert.roll_up_cost_elements(cursor)==None
    # only the higher level cost element is updated
    # check updated column
    cursor.execute("""SELECT cost_element, updated
                    FROM cost_element
                    WHERE updated = 1;""")
    expect_output = [('218_fac', 1), ('21_fac', 1),('2_fac', 1)]
    real_output = cursor.fetchall()
    for tup in expect_output:
        assert tup in real_output

def test_roll_up_account_table(cursor):
    """ test function roll_up_account_table,this function will roll up the account table and also test the function roll_up_account_table_by_level"""
    # roll up the account table for pwr12be 
    assert accert.roll_up_account_table(cursor)==None
    # only the higher level account is updated
    # check updated column
    cursor.execute("""SELECT code_of_account, review_status
                    FROM account 
                    WHERE review_status = 'updated';""")
    expect_output = [('218', 'Updated'), ('21', 'Updated'), ('2', 'Updated')]
    real_output = cursor.fetchall()
    for tup in expect_output:
        assert tup in real_output


def test_roll_up_lmt_account_table(cursor):
    """ test function roll_up_lmt_account_table, this function will roll up the
    account table for abr1000 only level 3 to 2, which is the COA 222, it also 
    test the function roll_up_lmt_account,sum_up_lmt_account_2C, and
    sum_up_lmt_direct_cost_2C"""
    accert.acc_tabl = 'abr_account'
    # roll up the account table for abr1000 
    assert accert.roll_up_lmt_account_table(cursor)==None
    # only the higher level account is updated
    # check updated column
    cursor.execute("""SELECT code_of_account, review_status
                    FROM abr_account
                    WHERE review_status = 'updated';""")
    expect_output = [('222', 'Updated')]
    accert.acc_tabl = 'account'
    assert expect_output==cursor.fetchall()

def test_sum_cost_elements_2C(cursor):
    """ test function sum_cost_elements_2C, this function will sum up the cost elements for abr1000"""
    # sum up the cost element for abr1000
    accert.cel_tabl = 'abr_cost_element'
    assert accert.sum_cost_elements_2C(cursor)==None
    # check if the value is updated
    cursor.execute("""SELECT cost_element, updated
                    FROM abr_cost_element 
                    WHERE account = "2";""")
    expect_output = [('2c_fac',1), ('2c_lab', 1), ('2c_mat',1)]
    real_output = cursor.fetchall()
    for tup in expect_output:
        assert tup in real_output

def test_roll_up_lmt_account_2C(cursor):
    """ test function roll_up_lmt_account_2C, this function will sum up the account table for abr1000"""
    # sum up the account table for abr1000 
    accert.acc_tabl = 'abr_account'
    assert accert.roll_up_lmt_account_2C(cursor)==None
    # check if the value is updated
    cursor.execute("""SELECT code_of_account, review_status
                    FROM abr_account
                    WHERE code_of_account = "2C";""")
    expect_output = [('2C', 'Ready for Review')]
    assert expect_output==cursor.fetchall()

def test_roll_up_lmt_direct_cost(cursor):
    """ test function sum_up_abr_direct_cost, this function will sum up the direct cost for abr1000"""
    # sum up the direct cost for abr1000 
    accert.acc_tabl = 'abr_account'    
    assert accert.roll_up_lmt_direct_cost(cursor)==None
    # check if the value is updated
    cursor.execute("""SELECT code_of_account, review_status
                    FROM abr_account
                    WHERE code_of_account = "2";""")
    expect_output = [('2', 'Ready for Review')]
    assert expect_output==cursor.fetchall()

def test_none_functions(cursor):
    """ test function returned None, those functions are not used until user input new data """
    assert accert.update_new_cost_elements(cursor)==None
    assert accert.update_account_table_by_cost_elements(cursor)==None

def test_extract_variable_info_on_name(cursor):
    """ test function extract_variable_info_on_name, this function will extract the variable 
    information including value and unit from the variable table."""
    assert accert.extract_variable_info_on_name(cursor,'scale_1.0')== (1.0, '1')

def test_extract_super_val(cursor):
    """ test function extract_super_val, this function will extract the super variable from the 
    variable table. where the variable is c_pump_ap1000, the super variable is c_pump_per_unit_fac,"""
    assert accert.extract_super_val(cursor,'c_pump_ap1000') == 'c_pump_per_unit_fac'

def test_extract_total_cost_on_name(cursor):
    """ test function extract_total_cost_on_name, this function will extract the total cost from the 
    account table. where the COA is the name of the account, for example, 220A.27, the total cost is
    0"""
    accert.acc_tabl = 'account'    
    assert accert.extract_total_cost_on_name(cursor,'220A.27')== ('220A.27', 
                                                                    'Instrumentation And Control (NSSS)', 
                                                                    0.0)

def test_check_unit_conversion():
    """ test function check_unit_conversion, this function will check if the unit conversion is 
    possible. for example, if the unit is dollar and the new unit is million, the function will
    return True"""
    assert accert.check_unit_conversion('dollar','million')==True

def test_convert_unit():
    """ test function convert_unit, this function will return the converted value of the
    unit. for example, if the current_value is 1000,000, and current_unit is dollar, the 
    to_unit is million, the function will return the converted value 1. this function 
    also test convert_unit_scale"""
    assert accert.convert_unit(1000000,'dollar','million')==1

def test_run_pre_alg():
    """ test function run_pre_alg, this function will run the pre programed algorithm. the pre algorithm
    will update the cost element table for PWR12 BE and ABR1000. NOTE: all the pre programed algorithm
    output unit is million"""
    alg='sum(kwargs.values())'
    kwargs={'v_1': 1, 'v_2': 2}
    assert accert.run_pre_alg(alg, **kwargs)==3

def test_cal_direct_cost_elements(cursor,conn):
    """ test function cal_direct_cost_elements, this function will calculate the direct cost for 
    each cost element. This function will update the cost element table for ABR1000."""
    accert.acc_tabl = 'abr_account'
    real_ouput= accert.cal_direct_cost_elements(cursor)
    # the real value is (852973431.1169341, 382841817.9556325, 183971968.309387) unit in dollar
    # however, the value is too long, so I only test the digits in million
    for i in range(3):
        assert round(real_ouput[i],-6)==round((852973431.1169341, 382841817.9556325, 183971968.309387)[i],-6)

def test_generate_results_table(cursor,conn):
    """ test function generate_results_table, this function will generate the results table for 
    each cost element. This function will update the cost element table for PWR12BE. Also, this
    function will test write_to_excel function"""
    accert.ref_model = 'pwr12-be'
    accert.acc_tabl = 'account'
    accert.cel_tabl = 'cost_element'
    accert.var_tabl = 'variable'
    assert accert.generate_results_table(cursor, conn, level=3)==None
    # check whether the results xlsx file is generated
    assert os.path.isfile('pwr12-be_updated_account.xlsx')==True
    assert accert.generate_results_table_with_cost_elements(cursor, conn, level=3)==None

    assert os.path.isfile('pwr12-be_variable_affected_cost_elements.xlsx')==True
    assert os.path.isfile('pwr12-be_updated_cost_element.xlsx')==True
    # remove the generated xlsx file
    os.remove('pwr12-be_updated_account.xlsx')
    os.remove('pwr12-be_variable_affected_cost_elements.xlsx')
    os.remove('pwr12-be_updated_cost_element.xlsx')
