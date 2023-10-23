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
        self.ref_model = None
        self.acc_tabl = None
        self.cel_tabl = None
        self.var_tabl = None
        self.vlk_tabl = None
        self.alg_tabl = None
        self.esc_tabl = None
        self.fac_tabl = None
    
    def setup_table_names(self,c,xml2obj):
        """Setup different table names in the database.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        xml2obj : xml2obj
            xml2obj class instantiates objects that can convert son file to xml stream and create python data structure.

        Returns
        -------
        None
        """
        if "abr1000" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'abr1000'
            self.acc_tabl = 'abr_account'
            self.cel_tabl = 'abr_cost_element'
            self.var_tabl = 'abr_variable'
            self.vlk_tabl = 'abr_variable_links'   
            self.alg_tabl = 'algorithm'
            self.esc_tabl = 'escalation'
            self.fac_tabl = 'facility'    
        elif "heatpipemr" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'abr1000'
            self.acc_tabl = 'abr_account'
            self.cel_tabl = 'abr_cost_element'
            self.var_tabl = 'abr_variable'
            self.vlk_tabl = 'abr_variable_links'   
            self.alg_tabl = 'algorithm'
            self.esc_tabl = 'escalation'
            self.fac_tabl = 'facility'         
        elif "pwr12-be" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'pwr12-be'
            self.acc_tabl = 'account'
            self.cel_tabl = 'cost_element'
            self.var_tabl = 'variable'
            self.vlk_tabl = 'variable_links'
            self.alg_tabl = 'algorithm'
            self.esc_tabl = 'escalation'
            self.fac_tabl = 'facility'
        elif "lfr" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'lfr'
            self.acc_tabl = 'lfr_account'
            self.cel_tabl = 'abr_cost_element'
            self.var_tabl = 'abr_variable'
            self.vlk_tabl = 'abr_variable_links'   
            self.alg_tabl = 'algorithm'
            self.esc_tabl = 'escalation'
            self.fac_tabl = 'facility'
        return None

    def load_obj(self, input_path, accert_path):
        """Convert son file to xml stream and creates a python data structure.

        Parameters
        ----------
        input_path : PathLike
            Inputs file path.
        accert_path: PathLike
            ACCERT's repository path.

        Returns
        -------
        A Python object converted from the input file.
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
        """Get current Code of Accounts based on the input ID of Super Account.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements. 
        inp_id : str
            COA ID

        Returns
        -------
        coa_lst
            List of COA's.
        coa_others
            List of a COA's other info, including ind, lft, rgt.
        """
        c.execute("""SELECT code_of_account, ind, rgt FROM account WHERE supaccount = '{}';""".format(inp_id))
        # CREATE PROCEDURE get_current_COAs(IN table_name VARCHAR(50), 
        #                                   IN inp_id VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT code_of_account, 
        #                        ind, rgt FROM ', table_name, ' WHERE supaccount = ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @inp_id = inp_id;
        #     EXECUTE stmt USING @inp_id;
        #     DEALLOCATE PREPARE stmt;
        # END
        # c.callproc('get_current_COAs',(self.acc_tabl, inp_id))
        coa_info = c.fetchall()
        coa_lst = []
        coa_other =[]
        for coa in coa_info:
            coa_lst.append(coa[0])
            coa_other.append(coa[1:])
        return coa_lst , coa_other

    def update_account_before_insert(self, c, max_ind, max_rgt):
        """Updates the current COAs ind, lft, rgt.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        max_ind : int
            Original index of the account next to the inserted COA.
        max_rgt : int
            Original rgt of the account next to the inserted COA.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_account_before_insert`(IN table_name VARCHAR(50),
        #                                               IN max_ind INT,
        #                                               IN max_rgt INT)
        # BEGIN
        #     SET @stmt = CONCAT('UPDATE ', table_name,
        #                        ' SET ind = ind + 1 WHERE ind > ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @max_ind = max_ind;
        #     EXECUTE stmt USING @max_ind;
        #     DEALLOCATE PREPARE stmt;  
        #     SET @stmt = CONCAT('UPDATE ', table_name,
        #                        ' SET lft = lft + 2 WHERE lft > ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @max_rgt = max_rgt;
        #     EXECUTE stmt USING @max_rgt;
        #     DEALLOCATE PREPARE stmt;
        #     SET @stmt = CONCAT('UPDATE ', table_name,
        #                        ' SET rgt = rgt + 2 WHERE rgt > ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @max_rgt = max_rgt;
        #     EXECUTE stmt USING @max_rgt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('update_account_before_insert',(self.acc_tabl, max_ind, max_rgt))
        # c.execute("UPDATE accert_db.account SET ind = ind + 1 WHERE ind > {}".format(max_ind))
        # c.execute("UPDATE accert_db.account SET lft = lft + 2 WHERE lft > {}".format(max_rgt))
        # c.execute("UPDATE accert_db.account SET rgt = rgt + 2 WHERE rgt > {}".format(max_rgt))
        return None

    def insert_new_COA(self, c, ind, supaccount, level, lft, rgt, 
                        code_of_account, account_description= None,var_value=None, 
                        var_unit=None, total_cost=0, unit='dollar',main_subaccounts=None, 
                        cost_elements=None, review_status='Added', prn='0'):
        """Insert a new COA in between an index in the account table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ind : int
            Index of the new inserted COA.
        supaccount : str
            Super account of the new inserted COA.
        level : int
            Level of the new inserted COA.
        lft : int
            Lft index for nested model of the new inserted COA.
        rgt : int
            Rgt index for nested model of the new inserted COA.
        code_of_account : str, optional
            COA of the new inserted COA, by default "new"
        account_description : str, optional
            Account description of the new inserted COA. (By default none)
        total_cost : int, optional
            Total cost of the new inserted COA. (Set to 0 dollars by default)
        unit : str, optional
            Unit of the new inserted COA. (By default set to dollars)
        main_subaccounts : List[str], optional
            Main subaccounts of the new inserted COA. (By default none)
        cost_elements : List[str], optional
            Cost elements of the new inserted COA. (By default none)
        review_status : str, optional
            Review status of the new inserted COA. (By default 'Unchanged')
        prn : str(float), optional
            Percentage of the total cost of new inserted COA. (Set to 0% by default)
        """       
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `insert_new_COA`(IN table_name VARCHAR(50),
        #                                           IN ind INT,
        #                                           IN supaccount VARCHAR(50),
        #                                           IN level INT,
        #                                           IN lft INT,
        #                                           IN rgt INT,
        #                                           IN code_of_account VARCHAR(50),
        #                                           IN account_description VARCHAR(50),
        #                                           IN total_cost INT,
        #                                           IN unit VARCHAR(50),
        #                                           IN main_subaccounts VARCHAR(100),
        #                                           IN cost_elements VARCHAR(50),
        #                                           IN review_status VARCHAR(50),
        #                                           IN prn VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('INSERT INTO ', table_name,
        #                        ' (ind, supaccount, level, lft, rgt, code_of_account, account_description, 
        #                           total_cost, unit, main_subaccounts, cost_elements, review_status, prn) 
        #                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)');
        # PREPARE stmt FROM @stmt;
        # SET @ind = ind;
        # SET @supaccount = supaccount;
        # SET @level = level;
        # SET @lft = lft;
        # SET @rgt = rgt;
        # SET @code_of_account = code_of_account;
        # SET @account_description = account_description;
        # SET @total_cost = total_cost;
        # SET @unit = unit;
        # SET @main_subaccounts = main_subaccounts;
        # SET @cost_elements = cost_elements;
        # SET @review_status = review_status;
        # SET @prn = prn;
        # EXECUTE stmt USING @ind, @supaccount, @level, @lft, @rgt, @code_of_account, @account_description,
        # @total_cost, @unit, @main_subaccounts, @cost_elements, @review_status, @prn;
        # DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;

        c.callproc('insert_new_COA',(self.acc_tabl, ind, supaccount, level, lft, rgt,
                                   code_of_account, account_description, total_cost, unit,
                                  main_subaccounts, cost_elements, review_status, prn))
        # c.execute("""INSERT INTO 
        # accert_db.account (ind, code_of_account, account_description, 
        #                     total_cost, unit, level, main_subaccounts,
        #                     supaccount, cost_elements, review_status, 
        #                     lft, rgt, prn) 
        # VALUES (%(ind)s, %(code_of_account)s, %(account_description)s,
        #         %(total_cost)s, %(unit)s, %(level)s, %(main_subaccounts)s,
        #         %(supaccount)s, %(cost_elements)s, %(review_status)s,
        #         %(lft)s, %(rgt)s, %(prn)s)""",
        # {'ind': ind, 'code_of_account': code_of_account, 
        # 'account_description': account_description, 
        # 'total_cost': total_cost, 'unit': unit, 'level': level, 
        # 'main_subaccounts': main_subaccounts, 'supaccount': supaccount, 
        # 'cost_elements': cost_elements, 'review_status': 
        # review_status, 'lft': lft, 'rgt': rgt, 'prn': prn})
        return None                   

    def insert_COA(self, c, sup_coa):
        """Insert a new COA into the account table.
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        sup_coa : str
            Super account of the new inserted COA.
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

        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `sup_coa_level`(IN table_name VARCHAR(50),
        #                                           IN supaccount VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT level FROM ', table_name, ' WHERE code_of_account = ?');
        # PREPARE stmt FROM @stmt;
        # SET @supaccount = supaccount;
        # EXECUTE stmt USING @supaccount;
        # DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;

        c.callproc('sup_coa_level',(self.acc_tabl, sup_coa))
        for row in c.stored_results():
            sup_coa_level = row.fetchone()[0]        
        # c.execute("SELECT level FROM accert_db.account WHERE code_of_account = %s", (sup_coa,))
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
        """Adds a new algorithm into algorithm table based of the following parameters:

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        alg_name : str
            Name of the algorithm.
        alg_for : str
            Whether the algorithm is for cost element or for variable.
        alg_description : str
            Description of the algorithm.
        alg_python : str
            Python code of the algorithm. (Variables should be in the form of 'var1', 'var2', 'var3'...)
        alg_formulation : str
            Prints info of the algorithm.
        alg_units : str
            Units of the output of algorithm.
        variables : List[str]
            Variables of the algorithm.
        constants : List[str]
            Constants of the algorithm.
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
        Extracts variable info based on a specific variable name.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            Variable ID.

        Returns
        -------
        var_info : List[str]
            Variable info including variable name and variable unit
        """

        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `extract_variable_info_on_name`(IN table_name VARCHAR(50),
        #                                           IN var_name VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT var_value, var_unit FROM ', table_name, ' WHERE var_name = ?');
        # PREPARE stmt FROM @stmt;
        # SET @var_name = var_name;
        # EXECUTE stmt USING @var_name;
        # DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;

        c.callproc('extract_variable_info_on_name',(self.var_tabl, var_id))
        for row in c.stored_results():
            results = row.fetchall()
        var_info = results[0]
        return var_info

    def extract_super_val(self, c,var_id):
        """
        Extracts information on the super variable based on a specific variable name.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            Variable ID.

        Returns
        -------
        sup_val : List[str]
            Super variable info including the name of the super variable.
        """    
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `extract_super_val`(IN table_name VARCHAR(50),
        #                                          IN var_name VARCHAR(50))
        # BEGIN
        #    SET @stmt = CONCAT('SELECT v_linked FROM ', table_name, ' WHERE var_name = ?');
        # PREPARE stmt FROM @stmt;
        # SET @var_name = var_name;
        # EXECUTE stmt USING @var_name;
        # DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('extract_super_val',(self.var_tabl, var_id))
        for row in c.stored_results():
           results = row.fetchone()    
        if results is not None:
            sup_val = results[0]
        else:
            sup_val = None
        return sup_val

    def update_input_variable(self, c,var_id,u_i_var_value,
                              u_i_var_unit,var_type='', quite=False):
        """
        Updates an input variable value and unit based on variable's ID. (Converts unit if needed)

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            Variable ID.
        u_i_var_value : float
            Variable value.
        u_i_var_unit : str
            Variable unit.
        var_type : str, optional
            Variable type, by default ''
        quite : bool, optional
            Whether or not to print the update info. (By default not, or false)
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

    def update_variable_info_on_name(self, c,var_id,var_value,var_unit):
        """
        Updates variable info based on variable name.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            Variable ID.
        var_value : float   
            Variable value.
        var_unit : str
            Variable unit.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_variable_info_on_name`(IN table_name VARCHAR(50),
        #                             IN `u_i_var_name` VARCHAR(50), IN `value` FLOAT, IN `unit` VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('UPDATE ', table_name, ' SET var_value = ?,
        #                         var_unit = ?,
        #                         user_input = ? WHERE var_name = ?');
        # PREPARE stmt FROM @stmt;
        # SET @var_value = value;
        # SET @var_unit = unit;
        # SET @user_input = 1;
        # SET @var_name = u_i_var_name;
        # EXECUTE stmt USING @var_value, @var_unit, @user_input, @var_name;
        # DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('update_variable_info_on_name', (self.var_tabl, var_id, var_value, var_unit))
        return None    

    def update_super_variable(self, c,var_id):
        """
        Updates super variable info based on variable name.
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            Variable ID.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_super_variable`(IN var_table_name VARCHAR(50),
        #                             IN alg_table_name VARCHAR(50), IN `u_i_var_name` VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT var.ind, var.var_name, var.var_value,
        #                         var.var_alg, var.var_need, alg.ind, alg.alg_python,
        #                         alg.alg_formulation, alg.alg_units, var.var_unit
        #                         FROM ', var_table_name, ' as var JOIN ', alg_table_name, ' as alg
        #                         ON var.var_alg=alg.alg_name
        #                         WHERE var.var_name=?');
        # PREPARE stmt FROM @stmt;
        # SET @var_name = u_i_var_name;
        # EXECUTE stmt USING @var_name;
        # DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('update_super_variable',(self.var_tabl, self.alg_tabl, var_id))
        for row in c.stored_results():
            result = row.fetchone()
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

    def extract_total_cost_on_name(self, c,tc_id):
        """
        Extracts information of the total cost based on a specific total cost's ID.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            Total cost ID.
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

    def check_unit_conversion(self, org_unit, new_unit):
        """
        Checks if unit conversion is needed.

        Parameters
        ----------
        org_unit : str
            Original unit.
        new_unit : str
            New unit.
        """
        if org_unit == new_unit:
            return False
        else:
            return True

    def convert_unit(self, current_value, current_unit, to_unit):
        """
        Converts the current unit to a new unit.
        
        Parameters
        ----------
        current_value : float
            Current value to be converted.
        current_unit : str
            Current unit.
        to_unit : str
            Unit to be converted to.
        
        Returns
        -------
        to_value : float
            Converted value.
        """

        scale = float(self.convert_unit_scale(current_unit,to_unit))
        to_value = current_value * scale
        if to_unit != 'dollar':
            print("[Unit Changed] Converted input from {} {} to {} {}".format(current_value, current_unit,to_value,to_unit))
        return to_value

    def convert_unit_scale(self, current_unit, to_unit):
        """
        Converts the current unit to a new unit in a scale pattern. (I.e. from kiloWatts to megaWatts or gigaWatts)

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
        Updates the total cost based on a total cost ID. (Checks if unit conversion is needed)

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            COA of the total cost.
        u_i_tc_value : float
            Total cost's value.
        u_i_tc_unit : str
            Total cost's unit.
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
        Updates the total cost based on a total cost ID, without checking for unit conversion.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        tc_id : str
            COA of the total cost.
        u_i_tc_value : float
            Total cost's value.
        u_i_tc_unit : str
            Total cost's unit.
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

        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_total_cost_on_name`(IN table_name VARCHAR(50),
        #                                                                         IN `tc_id` VARCHAR(50), 
        #                                                                         IN `u_i_tc_value` FLOAT, 
        #                                                                         IN `u_i_tc_unit` VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('UPDATE ', table_name, ' SET total_cost = ?, unit = ?, 
        #                                               review_status = "User Input" WHERE code_of_account = ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @tc_id = tc_id;
        #     SET @u_i_tc_value = u_i_tc_value;
        #     SET @u_i_tc_unit = u_i_tc_unit;
        #     EXECUTE stmt USING @u_i_tc_value, @u_i_tc_unit, @tc_id;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('update_total_cost_on_name',(self.acc_tabl,tc_id,u_i_tc_value,u_i_tc_unit))
        # c.execute("""UPDATE `accert_db`.`account`
        #             SET `total_cost` = {},
        #             `unit` =  "{}" ,
        #             `review_status` = 'User Input'
        #             WHERE `code_of_account` = "{}";""".format(u_i_tc_value,u_i_tc_unit,tc_id))
        return None

    def get_var_value_by_name(self, c, var_name):
        """
        Get a variable value based on a specific variable name.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_name : str
            Variable name.

        Returns
        -------
        var_value : str
            Variable value.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `get_var_value_by_name`(IN table_name VARCHAR(50),
        #                                                                     IN `var_name` VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT var_value FROM ', table_name, ' WHERE var_name = ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @var_name = var_name;
        #     EXECUTE stmt USING @var_name;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('get_var_value_by_name',(self.var_tabl,var_name))
        for row in c.stored_results():
            var_value = row.fetchone()[0]
        return var_value

    def run_pre_alg(self, alg, **kwargs):
        """
        Runs pre-algorithms.

        Parameters
        ----------
        alg : str
            Pre-algorithm name.
        **kwargs : dict
            Keyword arguments.
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
        Updates the cost element based on cost element name. (Turn off safe update mode)

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ce_name : str
            Cost element name starting with the COA of the account.
        alg_value : float
            Cost element value.
        """
        c.execute("""SET SQL_SAFE_UPDATES = 0;""")
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_cost_element_on_name`(IN table_name VARCHAR(50),
        #                                                                           IN `ce_name` VARCHAR(50),
        #                                                                           IN `alg_value` FLOAT)
        # BEGIN
        #     SET @stmt = CONCAT('UPDATE ', table_name, ' SET cost_2017 = ?, updated = 1 WHERE cost_element = ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @alg_value = alg_value;
        #     SET @ce_name = ce_name;
        #     EXECUTE stmt USING @alg_value, @ce_name;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('update_cost_element_on_name',(self.cel_tabl,ce_name,float(alg_value)))

        # c.execute(""" UPDATE cost_element
        #             set cost_2017 = %(ce_value)s,
        #             updated = %(updated)s
        #             where cost_element = %(ce_name)s ;""",
        #             {'ce_value': float(alg_value),
        #             'updated': 1,
        #             'ce_name': ce_name})         
        return None

    def update_new_cost_elements(self, c):
        """
        Calculates and updates affected cost elements based on the user input.

        Parameters
        ----------
        c : MySQLCursor 
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Updating cost elements '.center(100,'='))
        print('\n')
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_new_cost_elements`(IN cel_tabl_name VARCHAR(50),
        #                                                                         IN var_tabl_name VARCHAR(50),
        #                                                                         IN vlk_tabl_name VARCHAR(50),
        #                                                                         IN alg_tabl_name VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT ce_org.ind, ce_org.cost_element,
        #                         ce_org.cost_2017, ce_org.alg_name,
        #                         ce_org.variables, ce_org.algno,
        #                         alg.alg_python, alg.alg_formulation, alg.alg_units FROM
        #                         (SELECT ind, cost_element,
        #                         cost_2017, alg_name,
        #                         variables, algno
        #                         FROM ', cel_tabl_name, ' AS ce JOIN
        #                         (SELECT vl.ce
        #                             FROM (SELECT * FROM ', var_tabl_name, '
        #                                 WHERE user_input = 1) AS va
        #                             JOIN ', vlk_tabl_name, ' AS vl
        #                             ON va.var_name = vl.variable) AS ce_affected
        #                         ON ce.cost_element = ce_affected.ce) AS ce_org
        #                         JOIN ', alg_tabl_name, ' AS alg
        #                         ON ce_org.alg_name = alg.alg_name;');
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('update_new_cost_elements',(self.cel_tabl,self.var_tabl,self.vlk_tabl,self.alg_tabl))
        for row in c.stored_results():
            results = row.fetchall()
        # c.execute(""" SELECT ce_org.ind,	ce_org.cost_element,	
        #         ce_org.cost_2017,	ce_org.alg_name,	
        #         ce_org.variables,	ce_org.algno, 
        #         alg.alg_python, alg.alg_formulation,alg.alg_units from
        #         (SELECT ind,	cost_element,	
        #         cost_2017,	alg_name,	
        #         variables,	algno
        #         FROM cost_element as ce JOIN 
        #         (SELECT vl.ce  
        #             FROM (SELECT * FROM variable
        #                 WHERE user_input = 1) as va
        #             JOIN variable_links as vl
        #             on va.var_name = vl.variable) as ce_affected
        #         on ce.cost_element = ce_affected.ce) as ce_org
        #         JOIN algorithm as alg
        #         on ce_org.alg_name = alg.alg_name;""")
        # results = c.fetchall()
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

    def update_account_table_by_cost_elements(self, c):
        """
        Updates the account table based on the sum of the cost elements.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Updating account table '.center(100,'='))
        print('\n')
        print('[Updating] Updating account table by cost elements')
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_account_table_by_cost_elements`(IN acc_tabl_name varchar(50),
        #                                                                                     IN cel_tabl_name varchar(50))
        # BEGIN
        #     SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
        #                         '(SELECT ', acc_tabl_name, '.code_of_account,
        #                                 ce.total_cost as cost,
        #                                 ce.updated as updated,
        #                                 ', acc_tabl_name, '.unit
        #                         FROM ', acc_tabl_name, '
        #                         JOIN (SELECT account,
        #                                     sum(cost_2017) as total_cost,
        #                                     sum(updated) as updated
        #                             FROM ', cel_tabl_name, '
        #                             GROUP BY ', cel_tabl_name, '.account ) as ce
        #                         on ', acc_tabl_name, '.code_of_account = ce.account
        #                         ORDER BY ', acc_tabl_name, '.ind) as updated_account
        #                         SET ', acc_tabl_name, '.total_cost = updated_account.cost,
        #                         review_status = \'Ready for Review\'
        #                         WHERE updated_account.updated > 0
        #                         and ', acc_tabl_name, '.code_of_account = updated_account.code_of_account;');
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('update_account_table_by_cost_elements', (self.acc_tabl, self.cel_tabl))
        # c.execute("""UPDATE account,
        #             (SELECT account.code_of_account,	
        #                     ce.total_cost as cost,
        #                     ce.updated as updated,
        #                     account.unit
        #             FROM `accert_db`.`account` 
        #             JOIN (SELECT account, 
        #                         sum(cost_2017) as total_cost,
        #                         sum(updated) as updated
        #                 FROM `accert_db`.`cost_element`
        #                 GROUP BY `cost_element`.`account` ) as ce
        #             on account.code_of_account = ce.account 
        #             ORDER BY account.ind) as updated_account
        #             SET account.total_cost = updated_account.cost,
        #             review_status = 'Ready for Review'
        #             WHERE updated_account.updated > 0
        #             and account.code_of_account = updated_account.code_of_account;""")
        print('[Updated]  Account table updated from cost elements\n')
        return None

    def roll_up_cost_elements(self, c):
        """
        Rolls up cost elements from level 3 to 0 for pwr. Only rolls up level 3 to 2 for ABR.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Roll up cost elements '.center(100,'='))
        print('\n')
        self.roll_up_cost_elements_by_level(c,3,2)
        if self.ref_model=="pwr12-be":
            self.roll_up_cost_elements_by_level(c,2,1)
            self.roll_up_cost_elements_by_level(c,1,0)
        print('[Updated] Cost elements rolled up\n')
        return None

    def roll_up_cost_elements_by_level(self, c,from_level,to_level):
        """
        Rolls up cost elements from an input lower level to a higher level.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        from_level : int
            Roll up from a given level.
        to_level : int
            Roll up to a given level.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `roll_up_cost_elements_by_level`(IN table_name varchar(50), 
        #                                                                   IN from_level int, IN to_level int)
        # BEGIN
        #     SET @stmt = CONCAT('UPDATE ', table_name, ',',
        #                         '(SELECT c',to_level,'.cost_element as ce',to_level,'_ce, ',
        #                             'sum(uc',from_level,'.cost_2017) as c',to_level,'_cal_total_cost ',
        #                         'FROM ', table_name, ' as uc',from_level,
        #                         ' JOIN ', table_name, ' as c',to_level,
        #                         ' on uc',from_level,'.sup_cost_ele=c',to_level,'.cost_element ',
        #                         'join account as ac',to_level,
        #                         ' on c',to_level,'.account = ac',to_level,'.code_of_account ',
        #                         'where ac',to_level,'.level=',to_level,
        #                         ' group by c',to_level,'.cost_element) as updated_ce',to_level,
        #                         ' SET ',
        #                         table_name,'.cost_2017 = updated_ce',to_level,'.c',to_level,'_cal_total_cost,',
        #                         table_name,'.updated = 1 ',
        #                         'WHERE ',
        #                         table_name,'.cost_element = updated_ce',to_level,'.ce',to_level,'_ce');
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('roll_up_cost_elements_by_level',(self.cel_tabl,from_level,to_level))
        print('[Updating] Roll up cost elements from level {} to level {}'.format(from_level,to_level))
        # c.execute("""UPDATE cost_element,
        #             (SELECT c%(to)s.cost_element as ce%(to)s_ce, 
        #                 sum(uc%(from)s.cost_2017) as c%(to)s_cal_total_cost
        #             FROM cost_element as uc%(from)s
        #             JOIN cost_element as c%(to)s
        #             on uc%(from)s.sup_cost_ele=c%(to)s.cost_element
        #             join account as ac%(to)s
        #             on c%(to)s.account = ac%(to)s.code_of_account
        #             where ac%(to)s.level=%(to)s
        #             group by c%(to)s.cost_element) as updated_ce%(to)s
        #             SET
        #             cost_element.cost_2017 = updated_ce%(to)s.c%(to)s_cal_total_cost,
        #             cost_element.updated = 1
        #             WHERE
        #             cost_element.cost_element = updated_ce%(to)s.ce%(to)s_ce;""",{
        #                             'from': from_level,
        #                             'to': to_level})  # print_accounts(c)
        return None

    def roll_up_account_table(self, c):
        """
        Rolls up the account table from level 3 to 0.
        
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
        Rolls up the account table from an input lower level to a higher level.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        from_level : int
            Roll up from a given level.
        to_level : int
            Roll up to a given level.
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
        Rolls up the account table for ABR from level 3 to 2.

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
        Sums the cost element for ABR COA 2C. (Calculated cost) 

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
        Sums up total cost of account 2C for the ABR-1000.

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
        Sums up the total cost of account 2 from account 2C for the ABR-1000.

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
        Calculates the direct cost elements for the ABR including the factory, labor, and material costs. (2C_fac, 2C_lab, 2C_mat)

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
        Rolls up the account table for the ABR-1000.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements
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
        Prints the ACCERT logo.
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
        Generates the results tables.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        level : int
            Level of detail in the results table. (How many levels)
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
        Generates the results tables for the ABR-1000.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        level : int
            Level of detail in the results table. (How many levels)
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
        Writes the results to an excel file.

        Parameters
        ----------
        statement : str
            SQL statement.
        filename : str
            Filename of the excel file.
        conn : MySQLConnection
            MySQLConnection class instantiates objects that represent a connection to the MySQL database server.
        """
        df=sql.read_sql(statement,conn)
        df.to_excel(filename,index=False)       
        print("Successfully created excel file {}".format(filename))

    def execute_accert(self, c, ut):
        self.print_logo()
 
        accert = self.load_obj(input_path, accert_path).accert
        c.execute("USE accert_db")
        print(' Reading user input '.center(100,'='))
        print('\n')
        if accert.ref_model is not None:
            print('[USER_INPUT]', 'Reference model is',str(accert.ref_model.value),'\n')
            self.setup_table_names(c,accert)
            ut.setup_table_names(c,Accert)
        ut.print_user_request_parameter(c)  
        if accert.power is not None:
            for ind, inp in enumerate(accert.power):
                print('[USER_INPUT]', str(inp.id),'power is',str(inp.value.value),str(inp.unit.value),'\n')
                if str(inp.id)=='Thermal':
                    var_id = 'mwth'
                if str(inp.id)=='Electric':
                    var_id = 'mwe'
                var_value = str(inp.value.value)
                var_unit = str(inp.unit.value)
                self.update_variable_info_on_name(c,var_id,var_value,var_unit)
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
        if accert.var is not None:
            for var_ind, var_inp in enumerate(accert.var):
                u_i_var_value = float(str(var_inp.value.value))
                u_i_var_unit = str(var_inp.unit.value)
                var_id = str(var_inp.id).replace('"','')
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
                                    if self.ref_model:
                                        self.update_total_cost(c,tc_id,u_i_tc_value,u_i_tc_unit)
                                    else:
                                        print("ERROR: model not found ")
                                        print(accert.ref_model.value)
                                        print("Exiting")
                                        sys.exit(1)
        ######################


        ### print changed variables
        ut.extract_user_changed_variables(c)
        ### print changed total cost_elements
        ut.extract_affected_cost_elements(c)
        ### calculate and new cost_elements value update to the database in table cost_elements and also update the account table:
        self.update_new_cost_elements(c)

        ###NOTE: cost elements should be rolled up as well
        ### uncomment below to print new cost_elements value
        # ut.print_updated_cost_elements(c)

        self.roll_up_cost_elements(c)

        if self.ref_model=="abr1000":
            self.sum_cost_elements_2C(c)
            ### update the account table:

            self.update_account_table_by_cost_elements(c)

            ### roll up the account table:
            self.roll_up_abr_account_table(c)
            abr_fac,abr_lab,abr_mat = self.cal_direct_cost_elements(c)
            print(' Generating results table for review '.center(100,'='))
            print('\n')  
            ut.print_leveled_abr_accounts(c, abr_fac,abr_lab,abr_mat,all=False,cost_unit='million',level=3)

            self.generate_abr_results_table(c, conn,level=3)
        
        elif self.ref_model=="lfr":
            self.sum_cost_elements_2C(c)
            ### update the account table:

            self.update_account_table_by_cost_elements(c)

            ### roll up the account table:
            self.roll_up_abr_account_table(c)
            abr_fac,abr_lab,abr_mat = self.cal_direct_cost_elements(c)
            print(' Generating results table for review '.center(100,'='))
            print('\n')  
            ut.print_leveled_abr_accounts(c, abr_fac,abr_lab,abr_mat,all=False,cost_unit='million',level=3)

            self.generate_abr_results_table(c, conn,level=3)

        elif self.ref_model=="pwr12-be":

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

