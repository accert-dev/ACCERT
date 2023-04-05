import mysql.connector
import os
from prettytable import PrettyTable
import configparser
import xml2obj
from utility_accert import Utility_methods
from Algorithm import Algorithm
import numpy as np
import sys
import pandas.io.sql as sql
import pandas as pd
import warnings
from typing import Union

warnings.filterwarnings('ignore')
PathLike = Union[str, bytes, os.PathLike]

class Accert:
    def __init__(self, input_path, accert_path):
        self.input_path = input_path
        self.accert_path = accert_path
        self.input = self.load_obj(self.input_path, self.accert_path)

    def load_obj(self, input_path, accert_path):
        """convert son file to xml stream and create python data structure

        Parameters
        ----------
        input_path : PathLike
            input file path
        accert_path: PathLike
            ACCERT repository path

        Returns
        -------
        A Python object converted from the input file
        """    

        import subprocess
        sonvalidxml = accert_path + "/bin/sonvalidxml"
        schema = accert_path + "/src/etc/accert.sch"
        cmd = ' '.join([sonvalidxml, schema, input_path])
        xmlresult = subprocess.check_output(cmd, shell=True)
        ### obtain pieces of input by name for convenience
        # from .wasppy import xml2obj
        return xml2obj.xml2obj(xmlresult)

    def get_current_COAs(self, c, inp_id):
        """get current Code of accounts based on the input id of SupAccount

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements. 
        inp_id : str
            COA id

        Returns
        -------
        coa_lst
            list of COAs
        coa_others
            list of COAs' other info, including ind, lft, rgt
        """
        c.execute("""SELECT code_of_account, ind, rgt FROM account WHERE supaccount = '{}';""".format(inp_id))
        coa_info = c.fetchall()
        coa_lst = []
        coa_other =[]
        for coa in coa_info:
            coa_lst.append(coa[0])
            coa_other.append(coa[1:])
        return coa_lst , coa_other

    def update_account_before_insert(self, c, max_ind, max_rgt):
        """ update the current COAs' ind, lft, rgt

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        max_ind : int
            original ind of the account next to the inserted COA
        max_rgt : int
            original rgt of the account next to the inserted COA
        """
        c.execute("UPDATE accert_db.account SET ind = ind + 1 WHERE ind > {}".format(max_ind))
        c.execute("UPDATE accert_db.account SET lft = lft + 2 WHERE lft > {}".format(max_rgt))
        c.execute("UPDATE accert_db.account SET rgt = rgt + 2 WHERE rgt > {}".format(max_rgt))
        return None

    def insert_new_COA(self, c, ind, supaccount, level, lft, rgt, 
                        code_of_account, account_description= None,var_value=None, 
                        var_unit=None, total_cost=0, unit='dollar',main_subaccounts=None, 
                        cost_elements=None, review_status='Added', prn='0'):
        """insert new COA into account table

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ind : int
            ind of the new inserted COA
        supaccount : str
            SupAccount of the new inserted COA
        level : int
            level of the new inserted COA
        lft : int
            lft index for nested model of the new inserted COA
        rgt : int
            rgt index for nested model of the new inserted COA
        code_of_account : str, optional
            COA of the new inserted COA, by default "new"
        account_description : str, optional
            account description of the new inserted COA, by default None
        total_cost : int, optional
            total cost of the new inserted COA, by default 0, unit in dollar
        unit : str, optional
            unit of the new inserted COA, by default 'dollar'
        main_subaccounts : List[str], optional
            main subaccounts of the new inserted COA, by default None
        cost_elements : List[str], optional
            cost elements of the new inserted COA, by default None
        review_status : str, optional
            review status of the new inserted COA, by default 'Unchanged'
        prn : str(float), optional
            percentage of the total cost of new inserted COA, by default '0'
        """       

        c.execute("""INSERT INTO 
        accert_db.account (ind, code_of_account, account_description, 
                            total_cost, unit, level, main_subaccounts,
                            supaccount, cost_elements, review_status, 
                            lft, rgt, prn) 
        VALUES (%(ind)s, %(code_of_account)s, %(account_description)s,
                %(total_cost)s, %(unit)s, %(level)s, %(main_subaccounts)s,
                %(supaccount)s, %(cost_elements)s, %(review_status)s,
                %(lft)s, %(rgt)s, %(prn)s)""",
        {'ind': ind, 'code_of_account': code_of_account, 
        'account_description': account_description, 
        'total_cost': total_cost, 'unit': unit, 'level': level, 
        'main_subaccounts': main_subaccounts, 'supaccount': supaccount, 
        'cost_elements': cost_elements, 'review_status': 
        review_status, 'lft': lft, 'rgt': rgt, 'prn': prn})
        return None                   

    def insert_COA(self, c, sup_coa):
        """insert new COA into account table
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        sup_coa : str
            SupAccount of the new inserted COA
        """    
        # collect current COAs
        # current_COAs are list of current COAs' code_of_account
        # current_COA_others are list of current COAs' other info
        # include current COAs' ind lft rgt 
        current_COAs, current_COA_others = self.get_current_COAs(c, sup_coa)
        max_ind = max(current_COA_others,key=lambda item:item[0])[0]
        max_rgt = max(current_COA_others,key=lambda item:item[1])[1]
        # NOTE : if new COA is added, it will be added to the end of the current suplist
        # TODO : return a new COA id with the COA list as input
        # new_COA = get_new_COA_id(current_COAs)
        new_COA = "new"
        c.execute("SELECT level FROM accert_db.account WHERE code_of_account = %s", (sup_coa,))
        sup_coa_level = c.fetchone()[0]
        coa_level = sup_coa_level + 1
        # before inserting new COA, update the current COAs' ind, lft, rgt
        self.update_account_before_insert(c, max_ind, max_rgt)
        # insert new COA
        ## NOTE need to fix this for passing supaccount
        self.insert_new_COA(c, ind=max_ind+1, supaccount=str(l1_inp.id), level = coa_level, lft=max_rgt+1, rgt=max_rgt+2, code_of_account= new_COA )
        return None

    def add_new_alg(self, c,alg_name, alg_for,  alg_description, 
                    alg_python, alg_formulation, alg_units, variables, constants):
        """add new algorithm into algorithm table

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        alg_name : str
            name of the algorithm
        alg_for : str
            whether the algorithm is for cost element or for variable
        alg_description : str
            description of the algorithm
        alg_python : str
            python code of the algorithm, variables should be in the form of 'var1', 'var2', 'var3'... 
        alg_formulation : str
            print info of the algorithm
        alg_units : str
            units of the output of algorithm
        variables : List[str]
            variables of the algorithm
        constants : List[str]
            constants of the algorithm
        """    

        c.execute("""INSERT INTO 
        accert_db.algorithm ( alg_name, alg_for,  alg_description, 
                            alg_python, alg_formulation, alg_units, variables, constants)
        VALUES (%(alg_name)s, %(alg_for)s, %(alg_description)s, 
                %(alg_python)s, %(alg_formulation)s, %(alg_units)s, 
                %(variables)s, %(constants)s)""",
                { 'alg_name': alg_name, 'alg_for': alg_for, 'alg_description': alg_description,
                'alg_python': alg_python, 'alg_formulation': alg_formulation, 'alg_units': alg_units,
                'variables': variables, 'constants': constants})
        return None

    def extract_variable_info_on_name(self, c,var_id):
        """
        extract variable info on variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id

        Returns
        -------
        var_info : List[str]
            variable info including variable name, variable unit
        """
        c.execute("""SELECT var_value, var_unit 
                    FROM `accert_db`.`variable` 
                    WHERE var_name = %(u_i_var_name)s ;""",{'u_i_var_name': var_id})
        results = c.fetchall()
        var_info = results[0]
        return var_info

    def extract_abr_variable_info_on_name(self, c,var_id):
        """
        extract variable info on variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id

        Returns
        -------
        var_info : List[str]
            variable info including variable name, variable unit
        """    
        c.execute("""SELECT var_value, var_unit 
                    FROM `accert_db`.`abr_variable` 
                    WHERE var_name = %(u_i_var_name)s ;""",{'u_i_var_name': var_id})
        results = c.fetchall()
        var_info = results[0]
        return var_info

    def extract_super_val(self, c,var_id):
        """
        extract SuperVariable info on variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id

        Returns
        -------
        sup_val : List[str]
            SuperVariable info including SuperVariable name
        """    
        c.execute("""SELECT v_linked from variable where var_name=%(var_id)s""",{'var_id':var_id})
        results = c.fetchone()
        if results is not None:
            sup_val = results[0]
        else:
            sup_val = None
        return sup_val

    def extract_abr_super_val(self, c,var_id):
        """
        extract SuperVariable info on variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id

        Returns
        -------
        sup_val : List[str]
            SuperVariable info including SuperVariable name
        """
        c.execute("""SELECT v_linked from abr_variable where var_name=%(var_id)s""",{'var_id':var_id})
        results = c.fetchone()
        if results is not None:
            sup_val = results[0]
        else:
            sup_val = None
        return sup_val

    def update_input_variable(self, c,var_id,u_i_var_value,
                              u_i_var_unit,var_type='', quite=False):
        """
        update input variable value and unit

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id
        u_i_var_value : float
            variable value
        u_i_var_unit : str
            variable unit
        var_type : str, optional
            variable type, by default ''
        quite : bool, optional
            whether to print the update info, by default False
        """

        if not quite:
            print('[Updating] {}Variable {}'.format(var_type,var_id))
        org_var_info = self.extract_variable_info_on_name(c,var_id)
        # NOTE: org_var_info is a tuple
        org_var_value = float(org_var_info[0])
        org_var_unit = str(org_var_info[1])
        unit_convert = self.check_unit_conversion(org_var_unit,u_i_var_unit)
        if unit_convert:
            u_i_var_value = self.convert_unit(u_i_var_value,u_i_var_unit,org_var_unit)
            u_i_var_unit = org_var_unit
        # # DEBUG print
        self.update_variable_info_on_name(c,var_id,u_i_var_value,u_i_var_unit)
        if not quite:
            print('[Updated]  Changed from {} {} to {} {}\n'.format(org_var_value,org_var_unit, u_i_var_value, u_i_var_unit))
        return None

    def update_abr_input_variable(self, c,var_id,u_i_var_value,
                                  u_i_var_unit,var_type='', quite=False):
        """
        update input variable value and unit and convert unit if needed

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id
        u_i_var_value : float
            variable value
        u_i_var_unit : str
            variable unit
        var_type : str, optional
            variable type, by default ''
        quite : bool, optional
            whether to print the update info, by default False
        """
        
        if not quite:
            print('[Updating] {}Variable {}'.format(var_type,var_id))
        org_var_info = self.extract_abr_variable_info_on_name(c,var_id)
        # NOTE: org_var_info is a tuple
        org_var_value = float(org_var_info[0])
        org_var_unit = str(org_var_info[1])
        unit_convert = self.check_unit_conversion(org_var_unit,u_i_var_unit)
        if unit_convert:
            u_i_var_value = self.convert_unit(u_i_var_value,u_i_var_unit,org_var_unit)
            u_i_var_unit = org_var_unit
        # # DEBUG print
        self.update_abr_variable_info_on_name(c,var_id,u_i_var_value,u_i_var_unit)
        if not quite:
            print('[Updated]  Changed from {} {} to {} {}\n'.format(org_var_value,org_var_unit, u_i_var_value, u_i_var_unit))
        return None

    def update_abr_variable_info_on_name(self, c,var_id,var_value,var_unit):
        """
        update variable info on variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id
        var_value : float
            variable value
        var_unit : str
            variable unit
        """
        c.execute(""" UPDATE abr_variable
                    SET var_value = %(value)s,
                    var_unit = %(unit)s,
                    user_input = %(revised)s
                    WHERE var_name = %(u_i_var_name)s;""",
                    {'u_i_var_name': var_id,
                    'value': float(var_value),
                    'unit': var_unit,
                    'revised': 1})
        return None 

    def update_variable_info_on_name(self, c,var_id,var_value,var_unit):
        """
        update variable info on variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id
        var_value : float   
            variable value
        var_unit : str
            variable unit
        """
        c.execute("""UPDATE variable
                    SET var_value = %(value)s,
                    var_unit = %(unit)s,
                    user_input = %(revised)s
                    WHERE var_name = %(u_i_var_name)s;""",
                    {'u_i_var_name': var_id,
                    'value': float(var_value),
                    'unit': var_unit,
                    'revised': 1})
        return None    

    def update_super_variable(self, c,var_id):
        """
        update super variable info on variable name
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id
        """
        c.execute(""" SELECT variable.ind, 
                            variable.var_name, 
                            variable.var_value, 
                            variable.var_alg, 
                            variable.var_need, 
                            alg.ind,
                            alg.alg_python, 
                            alg.alg_formulation,
                            alg.alg_units, 
                            variable.var_unit
        FROM variable JOIN algorithm as alg
        ON variable.var_alg=alg.alg_name
        WHERE variable.var_name=%(var_id)s""",{'var_id':var_id})
        result = c.fetchone()
        ### results is a tuple
        sup_var_name = result[1]
        org_var_value = result[2]
        alg_name = result[3]
        var_name_lst = [x.strip() for x in result[4].split(',')]
        alg_no = result[5]
        alg = result[6]
        alg_form = result[7]
        alg_unit = result[8]
        sup_var_unit = result[9]
        # # # create a value list for debugging
        # # var_value_lst = []
        variables = {}
        for var_ind, var_name in enumerate(var_name_lst):
            # var_value_lst.append(get_var_value_by_name(c, var_name))
            variables['v_{}'.format(var_ind+1)] = self.get_var_value_by_name(c, var_name)
        # print('variables',variables)
        print('[Updating] Sup Variable {}, running algorithm: [{}], \n[Updating] with formulation: {}'.format(sup_var_name, alg_name, alg_form))
        alg_value = self.run_pre_alg(alg, **variables)
        self.update_input_variable(c,sup_var_name,alg_value,sup_var_unit,quite = True)
        if alg_unit == '1':
            alg_unit=''
            sup_var_unit=''
        print('[Updated]  Reference value is : {} {}, calculated value is: {} {}'.format(org_var_value,alg_unit,alg_value,sup_var_unit))
        print(' ')
        return None

    def update_abr_super_variable(self, c,var_id):
        """
        update super variable info on variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            variable id
        """
        c.execute(""" SELECT abr_variable.ind, 
                            abr_variable.var_name, 
                            abr_variable.var_value, 
                            abr_variable.var_alg, 
                            abr_variable.var_need, 
                            alg.ind,
                            alg.alg_python, 
                            alg.alg_formulation,
                            alg.alg_units, 
                            abr_variable.var_unit
        FROM abr_variable JOIN algorithm as alg
        ON abr_variable.var_alg=alg.alg_name
        WHERE abr_variable.var_name=%(var_id)s""",{'var_id':var_id})
        result = c.fetchone()
        ### results is a tuple
        sup_var_name = result[1]
        org_var_value = result[2]
        alg_name = result[3]
        var_name_lst = [x.strip() for x in result[4].split(',')]
        alg_no = result[5]
        alg = result[6]
        alg_form = result[7]
        alg_unit = result[8]
        sup_var_unit = result[9]
        # # # create a value list for debugging
        # # var_value_lst = []
        variables = {}
        for var_ind, var_name in enumerate(var_name_lst):
            # var_value_lst.append(get_var_value_by_name(c, var_name))
            variables['v_{}'.format(var_ind+1)] = self.get_abr_var_value_by_name(c, var_name)
        print('[Updating] Sup Variable {}, running algorithm: [{}], \n[Updating] with formulation: {}'.format(sup_var_name, alg_name, alg_form))
        alg_value = self.run_pre_alg(alg, **variables)
        self.update_abr_input_variable(c,sup_var_name,alg_value,sup_var_unit,quite = True)
        if alg_unit == '1':
            alg_unit=''
            sup_var_unit=''
        print('[Updated]  Reference value is : {} {}, calculated value is: {} {}'.format(org_var_value,alg_unit,alg_value,sup_var_unit))
        print(' ')
        return None

    def extract_total_cost_on_name(self, c,tc_id):
        """
        extract total cost on total cost name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            total cost id
        """
        ## Keep the note here for ref
        ## example with tuple
        # c.execute("""SELECT code_of_account, account_description, total_cost, unit
        #             FROM `accert_db`.`account` 
        #             WHERE code_of_account = %s;""",(tc_id,))

        ## example with direct format string
        c.execute("""SELECT code_of_account, account_description, total_cost, unit
                    FROM `accert_db`.`account` 
                    WHERE code_of_account = "{}" ;
                    """.format(tc_id))
        ## example with direct format string
        # c.execute("""SELECT code_of_account, account_description, total_cost, unit
        #             FROM `accert_db`.`account` 
        #             WHERE code_of_account = %(u_i_tc_name)s ;""",{'u_i_tc_name': str(tc_id).replace('"','')})
        results = c.fetchall()
        tc_info = results[0]
        return tc_info

    def extract_abr_total_cost_on_name(self, c,tc_id):
        """
        extract total cost on total cost name
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            total cost id
        """
        c.execute("""SELECT code_of_account, account_description, total_cost, unit
                    FROM `accert_db`.`abr_account` 
                    WHERE code_of_account = "{}" ;
                    """.format(tc_id))
        results = c.fetchall()
        tc_info = results[0]
        return tc_info

    def check_unit_conversion(self, org_unit, new_unit):
        """
        check if unit conversion is needed

        Parameters
        ----------
        org_unit : str
            original unit
        new_unit : str
            new unit
        """
        if org_unit == new_unit:
            return False
        else:
            return True

    def convert_unit(self, current_value, current_unit, to_unit):
        """
        convert unit from current unit to new unit
        
        Parameters
        ----------
        current_value : float
            current value to be converted
        current_unit : str
            current unit
        to_unit : str
            unit to be converted to
        
        Returns
        -------
        to_value : float
            converted value
        """

        scale = float(self.convert_unit_scale(current_unit,to_unit))
        to_value = current_value * scale
        if to_unit != 'dollar':
            print("[Unit Changed] Converted input from {} {} to {} {}".format(current_value, current_unit,to_value,to_unit))
        return to_value

    def convert_unit_scale(self, current_unit, to_unit):
        """
        convert unit from current unit to new unit

        Parameters
        ----------
        current_unit : str
            current unit
        to_unit : str
            unit to be converted to

        Returns
        -------
        scale : float
        """       
        if current_unit == to_unit:
            return 1
        elif current_unit == 'KW':
            if to_unit == 'MW':
                return 0.001
            elif to_unit == 'GW':
                return 0.000001
        elif current_unit == 'MW':
            if to_unit == 'KW':
                return 1000
            elif to_unit == 'GW':
                return 0.001
        elif current_unit == 'GW':
            if to_unit == 'KW':
                return 1000000
            elif to_unit == 'MW':
                return 1000
        elif current_unit == 'million':
            if to_unit == 'dollar':
                return 1000000
            elif to_unit == 'thousand':
                return 1000
        elif current_unit == 'thousand':
            if to_unit == 'million':
                return 1/1000
            elif to_unit == 'dollar':
                return 1000
        elif current_unit == 'dollar':
            if to_unit == 'thousand':
                return 1/1000
            elif to_unit == 'million':
                return 1/1000000
        elif current_unit == 'lbs':
            if to_unit == 'kg':
                return 0.453592
            elif to_unit == 'ton':
                return 0.000453592
        elif current_unit == 'kg':
            if to_unit == 'lbs':
                return 2.20462
            elif to_unit == 'ton':
                return 0.001
        elif current_unit == 'ton':
            if to_unit == 'lbs':
                return 2204.62
            elif to_unit == 'kg':
                return 1000
        elif current_unit == 'bar':
            if to_unit == 'psi':
                return 14.5038
            elif to_unit == 'psf':
                return 2088.54
        elif current_unit == 'psi':
            if to_unit == 'bar':
                return 0.068947572927646
            elif to_unit == 'psf':
                return 144
        else:
            print('Cannot convert unit from ',current_unit,'to',to_unit)
            raise ValueError

    def update_total_cost(self, c,tc_id, u_i_tc_value, u_i_tc_unit):
        """
        update total cost on total cost name, check if unit conversion is needed

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            COA of the total cost
        u_i_tc_value : float
            total cost value
        u_i_tc_unit : str
            total cost unit
        """
        print('[Updating] Total cost of account {}'.format(tc_id))
        org_tc_info = self.extract_total_cost_on_name(c,tc_id)
        org_tc_value = float(org_tc_info[2])
        org_tc_unit = org_tc_info[3]
        unit_convert = self.check_unit_conversion(org_tc_unit,u_i_tc_unit)
        if unit_convert:
            u_i_tc_value = self.convert_unit(u_i_tc_value,u_i_tc_unit,org_tc_unit)
            u_i_tc_unit = org_tc_unit
        self.update_total_cost_on_name(c,tc_id,u_i_tc_value,u_i_tc_unit)   
        print('[Updated]  Changed from {:,.2f} {} to {:,.2f} {}\n'.format( org_tc_value,org_tc_unit, int(u_i_tc_value), u_i_tc_unit))
        return None

    def update_total_cost_on_name(self, c, tc_id, u_i_tc_value, u_i_tc_unit):
        """
        update total cost on total cost name without checking unit conversion

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            COA of the total cost
        u_i_tc_value : float
            total cost value
        u_i_tc_unit : str
            total cost unit
        """
        ## NOTE I'm not sure if this is the best way to update the total cost
        ## Statement is not working as expected when passing in a string in a dictionary
        ## but it works when passing in the string directly in .format() method

        # c.execute("""UPDATE `accert_db`.`account`
        #             SET `total_cost` = %(u_i_tc_value)s ,
        #             `unit` =  %(u_i_tc_unit)s ,
        #             `review_status` = 'User Input'  
        #             WHERE `code_of_account` = "%(u_i_tc_name)s";""",
        #             {'u_i_tc_value':int(u_i_tc_value),
        #               'u_i_tc_unit':u_i_tc_unit,
        #               'u_i_tc_name':tc_id})
        c.execute("""UPDATE `accert_db`.`account`
                    SET `total_cost` = {},
                    `unit` =  "{}" ,
                    `review_status` = 'User Input'
                    WHERE `code_of_account` = "{}";""".format(u_i_tc_value,u_i_tc_unit,tc_id))
        return None

    def update_abr_total_cost(self, c,tc_id, u_i_tc_value, u_i_tc_unit):
        """
        update total cost on total cost name for ABR, check if unit conversion is needed

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            COA of the total cost
        u_i_tc_value : float
            total cost value
        u_i_tc_unit : str
            total cost unit
        """
        print('[Updating] Total cost of account {}'.format(tc_id))
        org_tc_info = self.extract_abr_total_cost_on_name(c,tc_id)
        org_tc_value = float(org_tc_info[2])
        org_tc_unit = org_tc_info[3]
        unit_convert = self.check_unit_conversion(org_tc_unit,u_i_tc_unit)
        if unit_convert:
            u_i_tc_value = self.convert_unit(u_i_tc_value,u_i_tc_unit,org_tc_unit)
            u_i_tc_unit = org_tc_unit
        self.update_abr_total_cost_on_name(c,tc_id,u_i_tc_value,u_i_tc_unit)   
        print('[Updated]  Changed from {:,.2f} {} to {:,.2f} {}\n'.format( org_tc_value,org_tc_unit, int(u_i_tc_value), u_i_tc_unit))
        return None

    def update_abr_total_cost_on_name(self, c, tc_id, u_i_tc_value, u_i_tc_unit):
        """
        update total cost on total cost name for ABR without checking unit conversion

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            COA of the total cost
        u_i_tc_value : float
            total cost value
        u_i_tc_unit : str
            total cost unit
        """
        c.execute("""UPDATE `accert_db`.`abr_account`
                    SET `total_cost` = {},
                    `unit` =  "{}" ,
                    `review_status` = 'User Input'
                    WHERE `code_of_account` = "{}";""".format(u_i_tc_value,u_i_tc_unit,tc_id))
        return None

    def get_var_value_by_name(self, c, var_name):
        """
        get variable value by variable name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_name : str
            variable name

        Returns
        -------
        var_value : str
            variable value
        """
        c.execute("""SELECT var_value FROM variable WHERE var_name = '{}';""".format(var_name))
        var_value = c.fetchone()[0]
        return var_value

    def get_abr_var_value_by_name(self, c, var_name):
        """
        get variable value by variable name for ABR

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_name : str
            variable name
        
        Returns
        ------- 
        var_value : str
            variable value
        """
        c.execute("""SELECT var_value FROM abr_variable WHERE var_name = '{}';""".format(var_name))
        var_value = c.fetchone()[0]
        return var_value

    def run_pre_alg(self, alg, **kwargs):
        """
        run pre-algorithm

        Parameters
        ----------
        alg : str
            pre-algorithm name
        **kwargs : dict
            keyword arguments
        """
        # NOTE: comments below is the original note from Patrick,
        #       I would want to keep the original note for future reference
        # add the variables in kwargs to the local
        # function namespace
        # (equivalent to c1 = 10; c2 = 10; c3 = 40.5)
        locals().update(kwargs)
        # report back the user algorithm
        # evaluate the algorithm
        alg_value = eval(alg)
        # print('Value: {}'.format(alg_value))
        return alg_value

    def update_cost_element_on_name(self, c, ce_name, alg_value):
        """
        update cost element on cost element name, turn off safe update mode

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ce_name : str
            cost element name starting with the COA of the account
        alg_value : float
            cost element value
        """
        c.execute("""SET SQL_SAFE_UPDATES = 0;""")
        c.execute(""" UPDATE cost_element
                    set cost_2017 = %(ce_value)s,
                    updated = %(updated)s
                    where cost_element = %(ce_name)s ;""",
                    {'ce_value': float(alg_value),
                    'updated': 1,
                    'ce_name': ce_name})         
        return None

    def update_new_cost_elements(self, c):
        """
        Calculate and update affected cost elements based on user input

        Parameters
        ----------
        c : MySQLCursor 
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Updating cost elements '.center(100,'='))
        print('\n')
        c.execute(""" SELECT ce_org.ind,	ce_org.cost_element,	
                ce_org.cost_2017,	ce_org.alg_name,	
                ce_org.variables,	ce_org.algno, 
                alg.alg_python, alg.alg_formulation,alg.alg_units from
                (SELECT ind,	cost_element,	
                cost_2017,	alg_name,	
                variables,	algno
                FROM cost_element as ce JOIN 
                (SELECT vl.ce  
                    FROM (SELECT * FROM variable
                        WHERE user_input = 1) as va
                    JOIN variable_links as vl
                    on va.var_name = vl.variable) as ce_affected
                on ce.cost_element = ce_affected.ce) as ce_org
                JOIN algorithm as alg
                on ce_org.alg_name = alg.alg_name;""")
        results = c.fetchall()
        for row in results:
            ce_name = row[1]
            org_ce_value = row[2]
            alg_name = row[3]
            var_name_lst = [x.strip() for x in row[4].split(',')]
            alg_no = row[5]
            alg = row[6]
            alg_form = row[7]
            alg_unit = row[8]
            # NOTE cost element unit is always in USD dollar
            # maybe the unit for cost element can be added to the cost_element table later???
            # # create a value list for debugging
            # var_value_lst = []
            variables = {}
            for var_ind, var_name in enumerate(var_name_lst):
                # var_value_lst.append(get_var_value_by_name(c, var_name))
                variables['v_{}'.format(var_ind+1)] = self.get_var_value_by_name(c, var_name)
            print('[Updating] Cost element [{}], running algorithm: [{}], \n[Updating] with formulation: {}'.format(ce_name, alg_name, alg_form))
            alg_value = self.run_pre_alg(alg, **variables)
            unit_convert = self.check_unit_conversion('dollar',alg_unit)
            if unit_convert:
                alg_value = self.convert_unit(alg_value,alg_unit,'dollar')
            print('[Updated]  Reference value is : ${:<11,.0f}, calculated value is: ${:<11,.0f} '.format(org_ce_value,alg_value))
            self.update_cost_element_on_name(c,ce_name,alg_value) 
            print(' ')
        return None

    def update_abr_cost_element_on_name(self, c, ce_name, alg_value):
        """
        update cost element on cost element name

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ce_name : str
            COA of the cost element
        alg_value : float
            cost element value calculated by algorithm
        """

        c.execute(""" UPDATE abr_cost_element
                    set cost_2017 = %(ce_value)s,
                    updated = %(updated)s
                    where cost_element = %(ce_name)s ;""",
                    {'ce_value': float(alg_value),
                    'updated': 1,
                    'ce_name': ce_name})
        return None

    def update_new_abr_cost_elements(self, c):
        print(' Updating cost elements '.center(100,'='))
        print('\n')
        c.execute(""" SELECT ce_org.ind,	ce_org.cost_element,	
                    ce_org.cost_2017,	ce_org.alg_name,	
                    ce_org.variables,	ce_org.algno, 
                    alg.alg_python, alg.alg_formulation,alg.alg_units from
                    (SELECT ind,	cost_element,	
                    cost_2017,	alg_name,	
                    variables,	algno
                    FROM abr_cost_element as ce JOIN 
                    (SELECT vl.ce  
                    FROM (SELECT * FROM abr_variable
                            WHERE user_input = 1) as va
                    JOIN abr_variable_links as vl
                    on va.var_name = vl.variable) as ce_affected
                    on ce.cost_element = ce_affected.ce) as ce_org
                    JOIN algorithm as alg
                    on ce_org.alg_name = alg.alg_name;""")
        results = c.fetchall()
        for row in results:
            ce_name = row[1]
            org_ce_value = row[2]
            alg_name = row[3]
            var_name_lst = [x.strip() for x in row[4].split(',')]
            alg_no = row[5]
            alg = row[6]
            alg_form = row[7]
            alg_unit = row[8]
            # NOTE cost element unit is always in USD dollar
            # maybe the unit for cost element can be added to the cost_element table later???
            # # create a value list for debugging
            # var_value_lst = []
            variables = {}
            for var_ind, var_name in enumerate(var_name_lst):
                # var_value_lst.append(get_var_value_by_name(c, var_name))
                variables['v_{}'.format(var_ind+1)] = self.get_abr_var_value_by_name(c, var_name)
            # print(textwrap.fill('[Updating] Cost element [{}], running algorithm: [{}], with formulation: {}'.format(ce_name, alg_name, alg_form), 120))  
            print('[Updating] Cost element [{}], running algorithm: [{}], \n[Updating] with formulation: {}'.format(ce_name, alg_name, alg_form))
            alg_value = self.run_pre_alg(alg, **variables)
            unit_convert = self.check_unit_conversion('dollar',alg_unit)
            if unit_convert:
                alg_value = self.convert_unit(alg_value,alg_unit,'dollar')
            print('[Updated]  Reference value is : ${:<11,.0f}, calculated value is: ${:<11,.0f} '.format(org_ce_value,alg_value))
            self.update_abr_cost_element_on_name(c,ce_name,alg_value) 
            print(' ')
        return None

    def update_account_table_by_cost_elements(self, c):
        """
        update account table from the sum of the cost elements

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Updating account table '.center(100,'='))
        print('\n')
        print('[Updating] Updating account table by cost elements')
        c.execute("""UPDATE account,
                    (SELECT account.code_of_account,	
                            ce.total_cost as cost,
                            ce.updated as updated,
                            account.unit
                    FROM `accert_db`.`account` 
                    JOIN (SELECT account, 
                                sum(cost_2017) as total_cost,
                                sum(updated) as updated
                        FROM `accert_db`.`cost_element`
                        GROUP BY `cost_element`.`account` ) as ce
                    on account.code_of_account = ce.account 
                    ORDER BY account.ind) as updated_account
                    SET account.total_cost = updated_account.cost,
                    review_status = 'Ready for Review'
                    WHERE updated_account.updated > 0
                    and account.code_of_account = updated_account.code_of_account;""")
        print('[Updated]  Account table updated from cost elements\n')
        # print_accounts(c)
        return None

    def update_abr_account_table_by_cost_elements(self, c):
        """
        update account table from the sum of the cost elements

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Updating account table '.center(100,'='))
        print('\n')
        print('[Updating] Updating account table by cost elements')
        c.execute("""UPDATE abr_account,
                    (SELECT account.code_of_account,	
                            ce.total_cost as cost,
                            ce.updated as updated,
                            account.unit
                    FROM `accert_db`.`abr_account` as account
                    JOIN (SELECT account, 
                                sum(cost_2017) as total_cost,
                                sum(updated) as updated
                        FROM `accert_db`.`abr_cost_element`
                        GROUP BY `abr_cost_element`.`account` ) as ce
                    on account.code_of_account = ce.account 
                    ORDER BY account.ind) as updated_account
                    SET abr_account.total_cost = updated_account.cost,
                    review_status = 'Ready for Review'
                    WHERE updated_account.updated > 0
                    and abr_account.code_of_account = updated_account.code_of_account;""")
        print('[Updated]  Account table updated from cost elements\n')
        # print_accounts(c)
        return None

    def roll_up_abr_cost_elements(self, c):
        """
        roll up cost elements from level 3 to 2 for ABR

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Roll up cost elements '.center(100,'='))
        print('\n')
        print('[Rolling up] Roll up cost elements')
        c.execute("""UPDATE abr_cost_element,
                    (SELECT a2.cost_element as ac2_ce, 
                        sum(ua3.cost_2017) as a2_cal_cost
                    FROM abr_cost_element as ua3
                    JOIN abr_cost_element as a2 
                    on ua3.sup_cost_ele=a2.cost_element
                    group by a2.cost_element
                    ) as updated_ce2
                                SET
                                    abr_cost_element.cost_2017 = updated_ce2.a2_cal_cost,
                                    abr_cost_element.updated = %(updated)s
                                WHERE
                                    abr_cost_element.cost_element = updated_ce2.ac2_ce;""",{
                                    'updated': 1})
        print('[Rolled up] Cost elements rolled up\n')
        # print_accounts(c)
        return None

    def roll_up_cost_elements(self, c):
        """
        roll up cost elements from level 3 to 0

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Roll up cost elements '.center(100,'='))
        print('\n')
        self.roll_up_cost_elements_by_level(c,3,2)
        self.roll_up_cost_elements_by_level(c,2,1)
        self.roll_up_cost_elements_by_level(c,1,0)
        print('[Updated] Cost elements rolled up\n')
        return None

    def roll_up_cost_elements_by_level(self, c,from_level,to_level):
        """
        roll up cost elements from from_level to to_level

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        from_level : int
            roll up from level
        to_level : int
            roll up to level
        """

        print('[Updating] Roll up cost elements from level {} to level {}'.format(from_level,to_level))
        c.execute("""UPDATE cost_element,
                    (SELECT c%(to)s.cost_element as ce%(to)s_ce, 
                        sum(uc%(from)s.cost_2017) as c%(to)s_cal_total_cost
                    FROM cost_element as uc%(from)s
                    JOIN cost_element as c%(to)s
                    on uc%(from)s.sup_cost_ele=c%(to)s.cost_element
                    join account as ac%(to)s
                    on c%(to)s.account = ac%(to)s.code_of_account
                    where ac%(to)s.level=%(to)s
                    group by c%(to)s.cost_element) as updated_ce%(to)s
                    SET
                    cost_element.cost_2017 = updated_ce%(to)s.c%(to)s_cal_total_cost,
                    cost_element.updated = 1
                    WHERE
                    cost_element.cost_element = updated_ce%(to)s.ce%(to)s_ce;""",{
                                    'from': from_level,
                                    'to': to_level})  # print_accounts(c)
        return None

    def roll_up_account_table(self, c):
        """
        roll up account table from level 3 to 0
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Rolling up account table '.center(100,'='))
        print('\n')
        self.roll_up_account_table_by_level(c,from_level=3,to_level=2)
        self.roll_up_account_table_by_level(c,from_level=2,to_level=1)
        self.roll_up_account_table_by_level(c,from_level=1,to_level=0)

        print('[Updated]  Account table rolled up\n')

        return None

    def roll_up_account_table_by_level(self, c, from_level, to_level):
        """
        roll up account table from from_level to to_level

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        from_level : int
            roll up from level
        to_level : int
            roll up to level
        """

        print('[Updating] Rolling up account table from level {} to level {} '.format(from_level,to_level))
        c.execute("""
                UPDATE account,
                (SELECT a%(to)s.code_of_account as ac%(to)s_coa, 
                        sum(ua%(from)s.total_cost) as a%(to)s_cal_total_cost
                FROM account as ua%(from)s
                JOIN account as a%(to)s on ua%(from)s.supaccount=a%(to)s.code_of_account
                where ua%(from)s.level=%(from)s and a%(to)s.level=%(to)s
                group by a%(to)s.code_of_account) as updated_ac%(to)s
                SET
                    account.total_cost = updated_ac%(to)s.a%(to)s_cal_total_cost,
                    account.review_status = 'Updated'
                WHERE
                    account.code_of_account = updated_ac%(to)s.ac%(to)s_coa 
            """,{'from':from_level,'to':to_level})
        return None

    def roll_up_abr_account(self, c):
        """
        roll up account table for ABR from level 3 to 2

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """

        print('ABR1000 model only roll up level 3 to 2')
        ##NOTE inner join only update 222
        print('[Updating] Rolling up account table from level {} to level {} '.format(3,2))
        c.execute("""
                UPDATE abr_account,
                (SELECT a2.code_of_account as ac2_coa, 
                        sum(ua3.total_cost) as a2_cal_total_cost
                FROM abr_account as ua3
                JOIN abr_account as a2 on ua3.supaccount=a2.code_of_account
                where ua3.level=3 and a2.level=2
                group by a2.code_of_account) as updated_ac2
                SET
                    abr_account.total_cost = updated_ac2.a2_cal_total_cost,
                    abr_account.review_status = 'Updated'
                WHERE
                    abr_account.code_of_account = updated_ac2.ac2_coa 
            """)
        return None

    def sum_cost_elements_2C(self, c):
        """
        sum cost element for ABR COA 2c (calculated cost) 

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """

        print(' Summing cost elements for direct cost '.center(100,'='))
        print('\n')
        print('[Updating] Summing cost elements')
        c.execute("""SELECT sum(cef.cost_2017) from
                    (SELECT t1.code_of_account,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(t1.cost_elements, ',', 1), ',', -1) as fac_name
                    FROM accert_db.abr_account AS t1 
                    LEFT JOIN abr_account as t2
                    ON t1.code_of_account = t2.supaccount
                    WHERE t2.code_of_account IS NULL 
                    and t1.code_of_account!='2' 
                    and t1.code_of_account!='2C' )as ac
                    join accert_db.abr_cost_element as cef
                            on cef.cost_element = ac.fac_name
                            where ac.code_of_account!='2C'""")
        sum_2c_fac = c.fetchone()[0]
        c.execute("""UPDATE abr_cost_element
                    SET cost_2017 = %(sum_2c_fac)s,
                    updated = %(updated)s
                    WHERE cost_element = '2C_fac'""",{'sum_2c_fac':float(sum_2c_fac),'updated':1})

        c.execute("""SELECT sum(cef.cost_2017) from
                    (SELECT t1.code_of_account,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(t1.cost_elements, ',', 2), ',', -1) as lab_name
                    FROM accert_db.abr_account AS t1 
                    LEFT JOIN abr_account as t2
                    ON t1.code_of_account = t2.supaccount
                    WHERE t2.code_of_account IS NULL 
                    and t1.code_of_account!='2' 
                    and t1.code_of_account!='2C' )as ac
                    join accert_db.abr_cost_element as cef
                            on cef.cost_element = ac.lab_name
                            where ac.code_of_account!='2C'""")
        sum_2c_lab = c.fetchone()[0]
        c.execute("""UPDATE abr_cost_element
                    SET cost_2017 = %(sum_2c_lab)s,
                    updated = %(updated)s
                    WHERE cost_element = '2C_lab'""",{'sum_2c_lab':float(sum_2c_lab),'updated':1})
        c.execute("""SELECT sum(cef.cost_2017) from
                    (SELECT t1.code_of_account,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(t1.cost_elements, ',', 3), ',', -1) as mat_name
                    FROM accert_db.abr_account AS t1 
                    LEFT JOIN abr_account as t2
                    ON t1.code_of_account = t2.supaccount
                    WHERE t2.code_of_account IS NULL 
                    and t1.code_of_account!='2' 
                    and t1.code_of_account!='2C' )as ac
                    join accert_db.abr_cost_element as cef
                            on cef.cost_element = ac.mat_name
                            where ac.code_of_account!='2C'""")
        sum_2c_mat = c.fetchone()[0]
        c.execute("""UPDATE abr_cost_element
                    SET cost_2017 = %(sum_2c_mat)s,
                    updated = %(updated)s
                    WHERE cost_element = '2C_mat'""",{'sum_2c_mat':float(sum_2c_mat),'updated':1})

        print('[Updated] Cost elements summed\n')
        return None

    def sum_up_abr_account_2C(self, c):
        """
        sum up total cost of account 2C for ABR

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """

        print(' Summing up account table '.center(100,'='))
        print('\n')
        c.execute("""UPDATE abr_account,
                (SELECT  sum(t1.total_cost) as tc, sum(t1.prn) as tprn FROM
                    abr_account AS t1 LEFT JOIN abr_account as t2
                    ON t1.code_of_account = t2.supaccount
                    WHERE t2.code_of_account IS NULL 
                    and t1.code_of_account!='2' 
                    and t1.code_of_account!='2C') as dircost
                SET abr_account.total_cost = dircost.tc,
                abr_account.prn=dircost.tprn,
                review_status = 'Ready for Review'
                WHERE abr_account.code_of_account = '2C';""")
        print('[Updated]  Account table summed up for calculated direct cost.\n')
        return None

    def sum_up_abr_direct_cost(self, c):
        """
        sum up total cost of account 2 from account 2c for ABR

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""UPDATE abr_account,
                (SELECT  (total_cost/prn) as talcost 
                    FROM abr_account as pre_abr
                    WHERE pre_abr.code_of_account ='2C') as calcost
                SET abr_account.total_cost = calcost.talcost,
                review_status = 'Ready for Review'
                WHERE abr_account.code_of_account = '2';""")
        print('[Updated]  Account table summed up for direct cost.\n')
        return None

    def cal_direct_cost_elements(self, c):
        """
        calculate direct cost elements for ABR including 2C_fac, 2C_lab, 2C_mat

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT  sum(t1.prn) as tprn FROM
                    abr_account AS t1 LEFT JOIN abr_account as t2
                    ON t1.code_of_account = t2.supaccount
                    WHERE t2.code_of_account IS NULL 
                    and t1.code_of_account!='2' 
                    and t1.code_of_account!='2C';""")
        tprn  = c.fetchone()[0]      
        c.execute("""SELECT cost_2017 FROM accert_db.abr_cost_element
                    where account='2'
                    and cost_element='2c_fac' """)
        fac = c.fetchone()[0]/tprn
        c.execute("""SELECT cost_2017 FROM accert_db.abr_cost_element
                    where account='2'
                    and cost_element='2c_lab' """)
        lab = c.fetchone()[0]/tprn
        c.execute("""SELECT cost_2017 FROM accert_db.abr_cost_element
                    where account='2'
                    and cost_element='2c_mat' """)     
        mat = c.fetchone()[0]/tprn        
        # print(' Direct cost calculation '.center(100,'='))
        # print(fac, lab,mat)
        # print('[Updated]  Account table summed up for direct cost.\n')
        return fac,lab,mat

    def roll_up_abr_account_table(self, c):
        """
        roll up account table for ABR

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Rolling up account table '.center(100,'='))
        print('\n')
        ### only update account 222 and account 2C
        self.roll_up_abr_account(c)
        print('[Updated]  Account table rolled up\n')
        self.sum_up_abr_account_2C(c)
        self.sum_up_abr_direct_cost(c)
        return None

    def print_logo(self):
        """ 
        print logo
        """
        print('\n')
        print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(":::'###:::::'######:::'######::'########:'########::'########:")
        print("::'## ##:::'##... ##:'##... ##: ##.....:: ##.... ##:... ##..::")
        print(":'##:. ##:: ##:::..:: ##:::..:: ##::::::: ##:::: ##:::: ##::::")
        print("'##:::. ##: ##::::::: ##::::::: ######::: ########::::: ##::::")
        print(" #########: ##::::::: ##::::::: ##...:::: ##.. ##:::::: ##::::")
        print(" ##.... ##: ##::: ##: ##::: ##: ##::::::: ##::. ##::::: ##::::")
        print(" ##:::: ##:. ######::. ######:: ########: ##:::. ##:::: ##::::")
        print("..:::::..:::.......::::......::........::..:::::..:::::..:::::")
        print('\n')

    def generate_results_table(self, c, conn, level=3):
        """
        generate results tables

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        level : int
            level of detail in the results table
        """

        statement="SELECT rankedcoa.code_of_account, account.account_description, account.total_cost,	 account.unit,	 account.level, account.review_status	 FROM account JOIN (SELECT node.code_of_account AS COA,  CONCAT( REPEAT(' ', COUNT(parent.code_of_account) - 1), node.code_of_account) AS code_of_account FROM account AS node, account AS parent WHERE node.lft BETWEEN parent.lft AND parent.rgt GROUP BY node.code_of_account) as rankedcoa ON account.code_of_account=rankedcoa.COA WHERE account.level <={} ORDER BY account.lft;".format(level)
        filename = 'ACCERT_updated_account.xlsx'
        # filename = 'ACCERT_updated_account.csv'
        self.write_to_excel(statement, filename,conn)

        statement="SELECT va.var_name, va.var_description, affectv.ce_affected FROM accert_db.variable as va JOIN (SELECT variable,group_concat(ce) as ce_affected FROM accert_db.variable_links group by variable) as affectv on va.var_name = affectv.variable WHERE va.user_input = 1 order by va.ind"
        filename = 'ACCERT_variable_affected_cost_elements.xlsx'
        # filename = 'ACCERT_variable_affected_cost_elements.csv'

        self.write_to_excel(statement, filename,conn)

        statement="SELECT ce.cost_element, ce.cost_2017 as cost, ce.sup_cost_ele, ce.alg_name, ce.account FROM accert_db.cost_element as ce WHERE ce.updated != 0 order by ce.ind"
        filename = 'ACCERT_updated_cost_element.xlsx'    
        # filename = 'ACCERT_updated_cost_element.csv'
        self.write_to_excel(statement, filename,conn)

    def generate_abr_results_table(self, c, conn, level=3):
        """
        generate results tables for ABR

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        level : int
            level of detail in the results table
        """
        statement="SELECT rankedcoa.code_of_account, abr_account.account_description, abr_account.total_cost,	 abr_account.unit,	 abr_account.level,abr_account.prn as pct,abr_account.review_status FROM abr_account JOIN (SELECT node.code_of_account AS COA, CONCAT( REPEAT(' ', COUNT(parent.code_of_account) - 1), node.code_of_account) AS code_of_account FROM abr_account AS node, abr_account AS parent WHERE node.lft BETWEEN parent.lft AND parent.rgt GROUP BY node.code_of_account) as rankedcoa ON abr_account.code_of_account=rankedcoa.COA WHERE abr_account.level <=3 ORDER BY abr_account.lft;".format(level)
        filename = 'ACCERT_updated_account.xlsx'
        # filename = 'ACCERT_updated_account.csv'

        self.write_to_excel(statement, filename,conn)

        statement="SELECT va.var_name, va.var_description, affectv.ce_affected FROM accert_db.abr_variable as va JOIN (SELECT variable,group_concat(ce) as ce_affected FROM accert_db.abr_variable_links group by variable) as affectv on va.var_name = affectv.variable WHERE va.user_input = 1 order by va.ind"
        filename = 'ACCERT_variable_affected_cost_elements.xlsx'
        # filename = 'ACCERT_variable_affected_cost_elements.csv'

        self.write_to_excel(statement, filename,conn)

        statement="SELECT ce.cost_element, ce.cost_2017 as cost, ce.sup_cost_ele, ce.alg_name, ce.account FROM accert_db.abr_cost_element as ce WHERE ce.updated != 0 order by ce.ind"
        filename = 'ACCERT_updated_cost_element.xlsx'
        # filename = 'ACCERT_updated_cost_element.csv'

        self.write_to_excel(statement, filename,conn)

    def write_to_excel(self, statement, filename,conn):
        """
        write results to excel file

        Parameters
        ----------
        statement : str
            SQL statement
        filename : str
            filename of the excel file
        conn : MySQLConnection
            MySQLConnection class instantiates objects that represent a connection to the MySQL database server.
        """
        df=sql.read_sql(statement,conn)
        df.to_excel(filename,index=False)       
        print("Successfully created excel file {}".format(filename))

    def execute_accert(self, c, ut):
        self.print_logo()
        ut.print_user_request_parameter(c)   
        accert = self.load_obj(input_path, accert_path).accert

        print(' Reading user input '.center(100,'='))
        print('\n')
        if accert.ref_model is not None:
            print('[USER_INPUT]', 'Reference model is',str(accert.ref_model.value),'\n')
        if accert.power is not None:
            for ind, inp in enumerate(accert.power):
                print('[USER_INPUT]', str(inp.id),'power is',str(inp.value.value),str(inp.unit.value),'\n')
                if str(inp.id)=='Thermal':
                    var_id = 'mwth'
                if str(inp.id)=='Electric':
                    var_id = 'mwe'
                var_value = str(inp.value.value)
                var_unit = str(inp.unit.value)
                if "abr1000" in str(accert.ref_model.value).lower():
                    self.update_abr_variable_info_on_name(c,var_id,var_value,var_unit)
                    sup_val_lst= self.extract_abr_super_val(c,var_id)
                if "pwr12-be" in str(accert.ref_model.value).lower():    
                    self.update_variable_info_on_name(c,var_id,var_value,var_unit)
                    sup_val_lst= self.extract_super_val(c,var_id)
            if sup_val_lst:
                sup_val_lst= sup_val_lst.split(',')     
            while sup_val_lst:
                sup_val = sup_val_lst.pop(0)
                if sup_val:
                    if "pwr12-be" in str(accert.ref_model.value).lower(): 
                        self.update_super_variable(c,sup_val)
                        new_sup_val = self.extract_super_val(c,sup_val)
                        if new_sup_val:
                            sup_val_lst.extend(new_sup_val.split(',')) 
                    elif "abr1000" in str(accert.ref_model.value).lower():
                        self.update_abr_super_variable(c,sup_val)
                        new_sup_val = self.extract_abr_super_val(c,sup_val)
                        if new_sup_val:
                            sup_val_lst.extend(new_sup_val.split(','))


        if accert.var is not None:
            for var_ind, var_inp in enumerate(accert.var):
                u_i_var_value = float(str(var_inp.value.value))
                u_i_var_unit = str(var_inp.unit.value)
                var_id = str(var_inp.id).replace('"','')
                if "pwr12-be" in str(accert.ref_model.value).lower():
                    self.update_input_variable(c,var_id,u_i_var_value,u_i_var_unit)
                    # sup_val = extract_super_val(c,var_id)
                    sup_val_lst= self.extract_super_val(c,var_id)
                    if sup_val_lst:
                        sup_val_lst= sup_val_lst.split(',')
                    while sup_val_lst:
                        sup_val = sup_val_lst.pop(0)
                        if sup_val:
                            self.update_super_variable(c,sup_val)
                            new_sup_val = self.extract_super_val(c,sup_val)
                            if new_sup_val:
                                sup_val_lst.extend(new_sup_val.split(',')) 
                if "abr1000" in str(accert.ref_model.value).lower():
                    self.update_abr_input_variable(c,var_id,u_i_var_value,u_i_var_unit)
                    sup_val_lst= self.extract_abr_super_val(c,var_id)
                    if sup_val_lst:
                        sup_val_lst= sup_val_lst.split(',')
                    while sup_val_lst:
                        sup_val = sup_val_lst.pop(0)
                        if sup_val:
                            self.update_abr_super_variable(c,sup_val)
                            new_sup_val = self.extract_abr_super_val(c,sup_val)
                            if new_sup_val:
                                sup_val_lst.extend(new_sup_val.split(','))
        if accert.l0COA is not None:
            if accert.l0COA.l1COA is not None:
                # TODO: check if print info can be verbose or not
                # # DEBUG print
                # print('l1')
                for l1_ind, l1_inp in enumerate(accert.l0COA.l1COA):
                    # # DEBUG print
                    # print('',l1_ind, l1_inp.id)
                    if l1_inp.l2COA is not None:
                        # # DEBUG print
                        # print(' l2')
                        for l2_ind, l2_inp in enumerate(l1_inp.l2COA):
                            if "new" in str(l2_inp.id):
                                self.insert_COA(c, str(l1_inp.id))
                            # # DEBUG print
                            # print(' ', l2_inp.id)
                            if l2_inp.ce is not None:
                                # # DEBUG print
                                # print('    l2ce')
                                for l2ce_ind, l2ce_inp in enumerate(l2_inp.ce):
                                    # # DEBUG print
                                    # print('     ', l2ce_inp.id)
                                    if l2ce_inp.alg is not None:
                                        # # DEBUG print
                                        # print('        l2ce alg')
                                        for l2ce_alg_ind, l2ce_alg_inp in enumerate(l2ce_inp.alg):
                                            # # DEBUG print
                                            # print('         ', l2ce_alg_inp.id)
                                            if l2ce_alg_inp.var is not None:
                                                # # DEBUG print
                                                # print('            l2ce alg var')
                                                for l2ce_alg_var_ind, l2ce_alg_var_inp in enumerate(l2ce_alg_inp.var):
                                                    if l2ce_alg_var_inp.alg is None:
                                                        ### NOTE variable will be user input values
                                                        u_i_var_value = float(str(l2ce_alg_var_inp.value.value))
                                                        u_i_var_unit = str(l2ce_alg_var_inp.unit.value)
                                                        var_id = str(l2ce_alg_var_inp.id).replace('"','')
                                                        self.update_input_variable(c,var_id,u_i_var_value,u_i_var_unit)
                                                        sup_val_lst= self.extract_super_val(c,var_id)
                                                        if sup_val_lst:
                                                            sup_val_lst= sup_val_lst.split(',')     
                                                        while sup_val_lst:
                                                            sup_val = sup_val_lst.pop(0)
                                                            if sup_val:
                                                                self.update_super_variable(c,sup_val)
                                                                new_sup_val = self.extract_super_val(c,sup_val)
                                                                if new_sup_val:
                                                                    sup_val_lst.extend(new_sup_val.split(',')) 


                                                        # sup_val = extract_super_val(c,var_id)
                                                        # if sup_val is not None:
                                                        # update_super_variable(c,sup_val)
                                                    else:
                                                        ### NOTE variable need to be calculated
                                                        for l2ce_alg_var_alg_ind, l2ce_alg_var_alg_inp in enumerate(l2ce_alg_var_inp.alg):
                                                            if l2ce_alg_var_alg_inp.var is not None:
                                                                ### update sub_variable info for each sup_variable in the algorithm(for sup_variable)
                                                                for l2ce_alg_var_alg_var_ind, l2ce_alg_var_alg_var_inp in enumerate(l2ce_alg_var_alg_inp.var):
                                                                    var_id = str(l2ce_alg_var_alg_var_inp.id).replace('"','')
                                                                    u_i_var_value = float(str(l2ce_alg_var_alg_var_inp.value.value))
                                                                    u_i_var_unit = str(l2ce_alg_var_alg_var_inp.unit.value)
                                                                    self.update_input_variable(c,var_id,u_i_var_value,u_i_var_unit,var_type='Sub ')
                                                        ### updating sup_variable 
                                                        var_id = str(l2ce_alg_var_inp.id).replace('"','')
                                                        self.update_super_variable(c,var_id)
                            if l2_inp.l3COA is not None:
                                # # DEBUG print
                                # print('    l3')
                                for l3_ind, l3_inp in enumerate(l2_inp.l3COA):
                                    ## NOTE this is not a great way to check if the 'new'
                                    ## is in the string, but it works for now
                                    if "new" in str(l3_inp.id):
                                        self.insert_COA(c, str(l2_inp.id))
                                    # # DEBUG print
                                    # print('     ', l3_inp.id)
                                    if l3_inp.ce is not None:
                                        # # DEBUG print
                                        # print('        l3ce')
                                        for l3ce_ind, l3ce_inp in enumerate(l3_inp.ce):
                                            # # DEBUG print
                                            # print('         ', l3ce_inp.id)
                                            if l3ce_inp.alg is not None:
                                                # # DEBUG print
                                                # print('            l3ce alg')
                                                for l3ce_alg_ind, l3ce_alg_inp in enumerate(l3ce_inp.alg):
                                                    # # DEBUG print
                                                    # print('             ', l3ce_alg_inp.id)
                                                    if l3ce_alg_inp.var is not None:
                                                        # # DEBUG print
                                                        # print('                l3ce alg var')
                                                        for l3ce_alg_var_ind, l3ce_alg_var_inp in enumerate(l3ce_alg_inp.var):
                                                            if l3ce_alg_var_inp.alg is None:
                                                                ### NOTE variable will be user input values
                                                                u_i_var_value = float(str(l3ce_alg_var_inp.value.value))
                                                                u_i_var_unit = str(l3ce_alg_var_inp.unit.value)
                                                                var_id = str(l3ce_alg_var_inp.id).replace('"','')
                                                                self.update_input_variable(c,var_id,u_i_var_value,u_i_var_unit)
                                                                sup_val_lst= self.extract_super_val(c,var_id)
                                                                if sup_val_lst:
                                                                    sup_val_lst= sup_val_lst.split(',')
                                                                while sup_val_lst:
                                                                    sup_val = sup_val_lst.pop(0)
                                                                    if sup_val:
                                                                        self.update_super_variable(c,sup_val)
                                                                        new_sup_val = self.extract_super_val(c,sup_val)
                                                                        if new_sup_val:
                                                                            sup_val_lst.extend(new_sup_val.split(',')) 


                                                                # sup_val = extract_super_val(c,var_id)
                                                                # if sup_val is not None:
                                                                #     update_super_variable(c,sup_val)

                                                            else:
                                                                ### NOTE variable need to be calculated
                                                                for l3ce_alg_var_alg_ind, l3ce_alg_var_alg_inp in enumerate(l3ce_alg_var_inp.alg):
                                                                    if l3ce_alg_var_alg_inp.var is not None:
                                                                        ### update sub_variable info for each sup_variable in the algorithm(for sup_variable)
                                                                        for l3ce_alg_var_alg_var_ind, l3ce_alg_var_alg_var_inp in enumerate(l3ce_alg_var_alg_inp.var):
                                                                            var_id = str(l3ce_alg_var_alg_var_inp.id).replace('"','')
                                                                            u_i_var_value = float(str(l3ce_alg_var_alg_var_inp.value.value))
                                                                            u_i_var_unit = str(l3ce_alg_var_alg_var_inp.unit.value)
                                                                            self.update_input_variable(c,var_id,u_i_var_value,u_i_var_unit,var_type='Sub ')
                                                                ### updating sup_variable 
                                                                var_id = str(l3ce_alg_var_inp.id).replace('"','')
                                                                self.update_super_variable(c,var_id)
                                    if l3_inp.total_cost is not None:
                                        # # DEBUG print
                                        # print('     l3 total cost')
                                        for l3_total_cost_ind, l3_total_cost_inp in enumerate(l3_inp.total_cost):
                                            # # DEBUG print
                                            # print('     ', l3_inp.id, l3_total_cost_inp.value.value, l3_total_cost_inp.unit.value)
                                            tc_id = str(l3_inp.id).replace('"','')
                                            u_i_tc_value = float(str(l3_total_cost_inp.value.value))
                                            u_i_tc_unit = str(l3_total_cost_inp.unit.value)
                                            self.update_total_cost(c, tc_id, u_i_tc_value, u_i_tc_unit)
                            if l2_inp.total_cost is not None:
                                # # DEBUG print
                                # print('    l2 total cost')
                                for l2_total_cost_ind, l2_total_cost_inp in enumerate(l2_inp.total_cost):
                                    # # DEBUG print
                                    # print('     ', l2_inp.id, l2_total_cost_inp.value.value, l2_total_cost_inp.unit.value)
                                    tc_id = str(l2_inp.id).replace('"','')
                                    u_i_tc_value = float(str(l2_total_cost_inp.value.value))
                                    u_i_tc_unit = str(l2_total_cost_inp.unit.value)
                                    if "abr1000" in str(accert.ref_model.value).lower():
                                        self.update_abr_total_cost(c,tc_id,u_i_tc_value,u_i_tc_unit)
                                    elif "pwr12-be" in str(accert.ref_model.value).lower():
                                        self.update_total_cost(c,tc_id,u_i_tc_value,u_i_tc_unit)
                                    else:
                                        print("ERROR: model not found ")
                                        print(accert.ref_model.value)
                                        print("Exiting")
                                        sys.exit(1)
                                    # update_total_cost(c,tc_id,u_i_tc_value,u_i_tc_unit)
        ######################

        if "abr1000" in str(accert.ref_model.value).lower():
            ### print changed variables
            ut.extract_user_changed_abr_variables(c)
            ### print changed total cost_elements
            ut.extract_affected_abr_cost_elements(c)
            ### calculate and new cost_elements value update to the database in table cost_elements and also update the account table:
            self.update_new_abr_cost_elements(c)
            ###NOTE: cost elements should be rolled up as well
            # ut.print_updated_abr_cost_elements(c)
            ### update the account table:
            self.roll_up_abr_cost_elements(c)

            self.sum_cost_elements_2C(c)
            self.update_abr_account_table_by_cost_elements(c)

            ### roll up the account table:
            self.roll_up_abr_account_table(c)
            abr_fac,abr_lab,abr_mat = self.cal_direct_cost_elements(c)
            print(' Generating results table for review '.center(100,'='))
            print('\n')  
            ut.print_leveled_abr_accounts(c, abr_fac,abr_lab,abr_mat,all=False,cost_unit='million',level=3)

            self.generate_abr_results_table(c, conn,level=3)

        elif "pwr12-be" in str(accert.ref_model.value).lower():  
            ### print changed variables
            ut.extract_user_changed_variables(c)
            ### print changed total cost_elements
            ut.extract_affected_cost_elements(c)
            ### NOTE: uncomment to print original and cost element values
            # ### print original cost_elements value:
            # extract_original_cost_elements(c)
            ### calculate and new cost_elements value update to the database in table cost_elements and also update the account table:
            self.update_new_cost_elements(c)
            # ut.extract_changed_cost_elements(c)
            self.roll_up_cost_elements(c)
            ### NOTE uncomment below to print new cost_elements value
            # print_updated_cost_elements(c)
            ### update the account table:
            self.update_account_table_by_cost_elements(c)
            ### roll up the account table:
            self.roll_up_account_table(c)
            ### print the account table:
            print(' Generating results table for review '.center(100,'='))
            print('\n')
            ut.print_leveled_accounts(c, all=False,cost_unit='million',level=3)
            self.generate_results_table(c, conn,level=3)


        ### close the connection:

        conn.close()

        sys.stdout.close()
        sys.stdout=stdoutOrigin


if __name__ == "__main__":
    """
    main driver
    """    
    
    stdoutOrigin=sys.stdout 
    sys.stdout = open("output.out", "w")
    # print_logo()

    if len(sys.argv) == 1:
        print("PLEASE ADD [Input_file_for_ACCERT]")
        sys.exit(-1)

    code_folder = os.path.dirname(os.path.abspath(__file__))
    initfile = os.path.join(code_folder, 'install.conf')
    ins = configparser.ConfigParser()
    ins.read(initfile)
    passwd = ins.get("INSTALL","PASSWD")

    conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=passwd,
    database="accert_db",
    auth_plugin="mysql_native_password"
    )
    # conn.commit()
    c = conn.cursor()
    ut = Utility_methods()
    accert_path = os.path.abspath(os.path.join(code_folder, os.pardir))
    user_input = sys.argv[2]  
    if os.path.exists(user_input):
        input_path = os.path.abspath(user_input)
    else:
        print('ACCERT did not find the input file {}'.format(user_input))
        raise SystemExit
    Accert = Accert(input_path,accert_path)
    Accert.execute_accert(c,ut)

