import mysql.connector
import os
from prettytable import PrettyTable
import configparser
import xml2obj
from utility_accert import Utility_methods
from Algorithm import Algorithm
import importlib
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
        """
        Initialize the Accert class.

        Parameters
        ----------
        input_path : PathLike
            Inputs file path.
        accert_path: PathLike
            ACCERT's repository path.
        """
        self.input_path = input_path
        self.accert_path = accert_path
        self.input = self.load_obj(self.input_path, self.accert_path)
        self.ref_model = None
        self.acc_tabl = None
        self.cel_tabl = None
        self.var_tabl = None
        self.alg_tabl = None
        self.esc_tabl = None
        self.fac_tabl = None
        self.use_gncoa = False
        self.gncoa_map = 'gncoamapping'
    
    def setup_table_names(self,xml2obj):
        """Setup different table names in the database.

        Parameters
        ----------
        xml2obj : xml2obj
            xml2obj class instantiates objects that can convert son file to xml stream and create python data structure.

        Returns
        -------
        None
        """
        if xml2obj.use_gncoa is not None:
            self.use_gncoa = str(xml2obj.use_gncoa.value).lower() == 'true'
        if "abr1000" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'abr1000'
            self.acc_tabl = 'abr_account'
            self.cel_tabl = 'abr_cost_element'
            self.var_tabl = 'abr_variable'
            self.alg_tabl = 'algorithm'
            self.esc_tabl = 'escalation'
            self.fac_tabl = 'facility'    
        elif "heatpipe" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'heatpipe'
            self.acc_tabl =  'heatpipe_account'
            self.cel_tabl =  'heatpipe_cost_element'
            self.var_tabl =  'heatpipe_variable'
            self.alg_tabl =  'algorithm'
            self.esc_tabl =  'escalation'
            self.fac_tabl =  'facility'         
        elif "pwr12-be" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'pwr12-be'
            self.acc_tabl = 'account'
            self.cel_tabl = 'cost_element'
            self.var_tabl = 'variable'
            self.alg_tabl = 'algorithm'
            self.esc_tabl = 'escalation'
            self.fac_tabl = 'facility'
        elif "lfr" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'lfr'
            self.acc_tabl = 'lfr_account'
            self.cel_tabl = 'abr_cost_element'
            self.var_tabl = 'abr_variable'
            self.alg_tabl = 'algorithm'
            self.esc_tabl = 'escalation'
            self.fac_tabl = 'facility'
        elif "fusion" in str(xml2obj.ref_model.value).lower():
            self.ref_model = 'fusion'
            self.acc_tabl = 'fusion_acco'
            self.cel_tabl = None
            self.var_tabl = 'fusion_varv'
            self.alg_tabl = 'fusion_alg'
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
        sonvalidxml = os.path.join(accert_path, "bin", "sonvalidxml")
        schema = os.path.join(accert_path, "src", "etc", "accert.sch")
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
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `get_current_COAs`(IN table_name VARCHAR(50), 
        #                                 IN inp_id VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT code_of_account, 
        #                     ind FROM ', table_name, ' WHERE supaccount = ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @inp_id = inp_id;
        #     EXECUTE stmt USING @inp_id;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('get_current_COAs',(self.acc_tabl, inp_id))
        for row in c.stored_results():
            coa_info = row.fetchall()
        coa_lst = []
        coa_other =[]
        for coa in coa_info:
            coa_lst.append(coa[0])
            coa_other.append(coa[1:])
        return coa_lst, coa_other

    def update_account_before_insert(self, c, min_ind):
        """Updates the current COAs ind.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        min_ind : int
            Original index of the account next to the inserted COA.

        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_account_before_insert`(IN table_name VARCHAR(50),
        #                                             IN min_ind INT)
        # BEGIN
        #     SET @stmt = CONCAT('UPDATE ', table_name,
        #                     ' SET ind = ind + 1 WHERE ind > ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @min_ind = min_ind-1;
        #     EXECUTE stmt USING @max_ind;
        #     DEALLOCATE PREPARE stmt;  
        # END$$
        # DELIMITER ;

        c.callproc('update_account_before_insert',(self.acc_tabl, min_ind-1))
        return None

    def insert_new_COA(self, c, ind, supaccount, level, 
                        code_of_account, account_description= None, 
                        total_cost=0, review_status='Added', prn='0'):
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
        code_of_account : str, optional
            COA of the new inserted COA, by default "new"
        account_description : str, optional
            Account description of the new inserted COA. (By default none)
        total_cost : int, optional
            Total cost of the new inserted COA. (Set to 0 dollars by default)
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

        c.callproc('insert_new_COA',(self.acc_tabl, ind, supaccount, level, 
                                   code_of_account, account_description, total_cost, 
                                   review_status, prn))
        return None                   

    def insert_COA(self, c, sup_coa,user_added_coa,user_added_coa_desc,
                   user_added_coa_total_cost):
        """Insert a new COA into the account table.
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        sup_coa : str
            Super account of the new inserted COA.
        user_added_coa : str
            COA of the new inserted COA.
        user_added_coa_desc : str
            Account description of the new inserted COA.
        user_added_coa_total_cost : int
            Total cost of the new inserted COA.
        """    
        # collect current COAs
        # current_COAs are list of current COAs' code_of_account
        # current_COA_others are list of current COAs' other info
        # include current COAs' ind lft rgt 
        current_COAs, current_COA_others = self.get_current_COAs(c, sup_coa)
        print('[Updating] Inserting new COA under COA',sup_coa)
        # print current COAs wrapped word for easy reading
        current_COAs = ', '.join(current_COAs)
        print('[Updating] Current COAs under COA {}: {}'.format(sup_coa, current_COAs))
        print(' ')
        
        min_ind = min(current_COA_others,key=lambda item:item[0])[0]
        # NOTE : if new COA is added, it will be added to the end of the top suplist
        # TODO : return a new COA id with the COA list as input
        # new_COA = get_new_COA_id(current_COAs)

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
        coa_level = sup_coa_level + 1

        # before inserting new COA, update the current COAs' ind
        # for example if the new COA is inserted between 1 and 2,
        # then the min_ind is 2, so the current COAs' ind will be updated
        # from 2 to n change to 3 to n+1
        # and the new COA will be inserted at 2
        self.update_account_before_insert(c, min_ind)
        # insert new COA
        self.insert_new_COA(c, ind=min_ind, supaccount=sup_coa, 
                            level = coa_level, code_of_account=user_added_coa, 
                            account_description=user_added_coa_desc,
                            total_cost= user_added_coa_total_cost)
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
        c.callproc('update_variable_info_on_name', (self.var_tabl, var_id, float(var_value), var_unit))
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
        print('[Updating] Sup Variable {}, running algorithm: [{}], \n[Updating] with formulation: {}'.format(sup_var_name, alg_name, alg_form))
        alg_value = self.run_pre_alg(alg, **variables)
        self.update_input_variable(c,sup_var_name,alg_value,sup_var_unit,quite = True)
        if alg_unit == '1':
            alg_unit=''
            sup_var_unit=''
        # print formatting value for scientific notation
        print('[Updated]  Reference value is : {:,.2e} {}, calculated value is: {:,.2e} {}'.format(org_var_value,alg_unit,alg_value,sup_var_unit))
        # print('[Updated]  Reference value is : {} {}, calculated value is: {} {}'.format(org_var_value,alg_unit,alg_value,sup_var_unit))
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
        #             FROM account
        #             WHERE code_of_account = %s;""",(tc_id,))

        ## example with direct format string
        # c.execute("""SELECT code_of_account, account_description, total_cost
        #             FROM account
        #             WHERE code_of_account = "{}" ;
        #             """.format(tc_id))
        # Stored procedure
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `extract_total_cost_on_name`(IN tc_id VARCHAR(50),
        #                                         IN table_name VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT code_of_account, account_description, total_cost, unit
        #                         FROM ', table_name, ' WHERE code_of_account = ?');
        #     PREPARE stmt FROM @stmt;
        #     SET @tc_id = tc_id;
        #     EXECUTE stmt USING @tc_id;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        tc_id = str(tc_id).replace("'","").replace('"','')
        # remove single quotes or double quotes from the string
        # c.execute("""SELECT code_of_account, account_description, total_cost
        #             FROM account
        #             WHERE code_of_account = %u_i_tc_name;""",{'u_i_tc_name': str(tc_id).replace("'","").replace('"','')})
        c.callproc('extract_total_cost_on_name',(self.acc_tabl, tc_id))
        for row in c.stored_results():
            results = row.fetchall()
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
        org_tc_unit = "dollar"
        unit_convert = self.check_unit_conversion(org_tc_unit,u_i_tc_unit)
        if unit_convert:
            u_i_tc_value = self.convert_unit(u_i_tc_value,u_i_tc_unit,org_tc_unit)
            u_i_tc_unit = org_tc_unit
        self.update_total_cost_on_name(c,tc_id,u_i_tc_value)   
        print('[Updated]  Changed from {:,.2f} {} to {:,.2f} {}\n'.format( org_tc_value,org_tc_unit, int(u_i_tc_value), org_tc_unit))
        return None

    def update_total_cost_on_name(self, c, tc_id, u_i_tc_value):
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

        Returns
        -------
        None
        """
        ## NOTE I'm not sure if this is the best way to update the total cost
        ## Statement is not working as expected when passing in a string in a dictionary
        ## but it works when passing in the string directly in .format() method

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
        u_i_tc_value= float(u_i_tc_value)
        c.callproc('update_total_cost_on_name',(self.acc_tabl,tc_id,u_i_tc_value))

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
        
        Returns
        -------
        alg_value : float
            Algorithm value
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
        return alg_value

    def update_account_value(self, alg_py, alg_name, variables):
        """
        Calls the specified algorithm with the given variables. Only called for fusion model now.
        For PWR, ABR,LFR, HEATPIPE the alg_py is in the form of a string that will be 
        evaluated in the Algorithm table stored in database. For Fusion, the algorithm is in 
        the form of a python file name that stored in Algorithm folder. For example, in 
        Fusion model, the alg_py value is 'FusionFunc' then it should look for FusionFunc.py 
        in the Algorithm folder.


        Parameters
        ----------
        alg_py : str
            Algorithm in python.
        alg_name : str
            Algorithm name.my
        variables : dict
            Variables to be passed to the algorithm.

        Returns
        -------
        result : float
            Algorithm result.

        
        """
        # Dynamically import the module
        module = importlib.import_module(f'Algorithm.{alg_py}')
        
        # Get the class from the module
        class_ = getattr(module, alg_py)
        
        # Create an instance of the class
        algorithm_instance = class_(
            ind=1,  # Dummy value, may be needed for future reference
            alg_name=alg_name,
            alg_for='test',  # Dummy value
            alg_description=f'Description of {alg_name}',  # Dummy value
            alg_formulation=f'Formulation of {alg_name}',  # Dummy value
            alg_units='units',  # Dummy value
            variables=','.join(variables.keys()),  # Convert variable names to a comma-separated string
            constants=''  # Dummy value, replace as needed
        )
        
        # Run the algorithm and get the result
        result = algorithm_instance.run(variables)
        return result

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

        Returns
        -------
        None
        """
        # Turn off safe update mode
        # keep the original note for future reference
        c.execute("""SET SQL_SAFE_UPDATES = 0;""")
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_cost_element_on_name`(
        #     IN table_name VARCHAR(50),
        #     IN ce_name VARCHAR(50),
        #     IN alg_value DECIMAL(20,5)  
        # )
        # BEGIN
        #     -- Disable safe updates for this operation
        #     SET SQL_SAFE_UPDATES = 0;

        #     -- Build the dynamic SQL query
        #     SET @stmt = CONCAT('UPDATE ', table_name, 
        #                     ' SET cost_2017 = ', alg_value, 
        #                     ', updated = 1 WHERE cost_element = ''', ce_name, '''');

        #     -- Prepare and execute the dynamic statement
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;

        #     -- Deallocate the prepared statement
        #     DEALLOCATE PREPARE stmt;

        # END;$$
        # DELIMITER ;

        # NOTE, float is used for alg_value, but it can be changed to DECIMAL(20,15) in the 
        # stored procedure, since float in python is equivalent to double in MySQL, tested 
        # for several values but using float in stored procedure is not recommended since 
        # the rolled up value may not be accurate.
        c.callproc('update_cost_element_on_name',(self.cel_tabl,ce_name,float(alg_value)))

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
        c.callproc('update_new_cost_elements',(self.cel_tabl,self.var_tabl,self.alg_tabl))
        for row in c.stored_results():
            results = row.fetchall()
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_new_cost_elements`(IN cel_tabl_name VARCHAR(50),
        #                                                                         IN var_tabl_name VARCHAR(50),
        #                                                                         IN alg_tabl_name VARCHAR(50))
        # BEGIN
        # 	SET SQL_SAFE_UPDATES = 0;
        #     SET @stmt = CONCAT("SELECT ce.ind, ce.cost_element,
        #        ce.cost_2017, ce.alg_name,
        #        ce.variables, ce.algno,
        #        alg.alg_python, alg.alg_formulation, alg.alg_units 
        # 		FROM ", cel_tabl_name, " AS ce 
        # 		JOIN ", alg_tabl_name, " AS alg ON ce.alg_name = alg.alg_name
        # 		WHERE EXISTS (
        # 			SELECT 1
        # 			FROM ", var_tabl_name, " AS va
        # 			WHERE va.user_input = 1
        # 			AND FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0);");
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
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

    def update_new_accounts(self, c):
        """
        Updates the affected accounts based on the variables. This funstion is called
        when there is no cost element table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        # for fusion or user defined table,  there is no cost_element table
        # so the update_new_cost_elements will not be executed
        # instead, the update_new_accounts will be executed
        print(' Updating accounts '.center(100,'='))
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `update_new_accounts`(IN acc_tabl_name VARCHAR(50),
        #                                                                         IN var_tabl_name VARCHAR(50),
        #                                                                         IN alg_tabl_name VARCHAR(50))
        # BEGIN
        #     SET SQL_SAFE_UPDATES = 0;
        #     SET @stmt = CONCAT("SELECT ac.ind, ac.code_of_account,
        #     ac.total_cost, ac.alg_name,
        #     ac.variables, 
        #     alg.alg_python, alg.alg_formulation, alg.alg_units 
        #         FROM ", acc_tabl_name, " AS ac 
        #         JOIN ", alg_tabl_name, " AS alg ON ac.alg_name = alg.alg_name
        #         WHERE EXISTS (
        #             SELECT 1
        #             FROM ", var_tabl_name, " AS va
        #             WHERE va.user_input = 1
        #             AND FIND_IN_SET(va.var_name, REPLACE(ac.variables, ' ', '')) > 0);");
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        c.callproc('update_new_accounts',(self.acc_tabl,self.var_tabl,self.alg_tabl))
        for row in c.stored_results():
            results = row.fetchall()
        for row in results:
            acc_name = row[1]
            # NOTE only for debugging
            org_acc_value = row[2]
            alg_name = row[3]
            var_name_lst = [x.strip() for x in row[4].split(',')]
            alg_py = row[5]
            alg_form = row[6]
            alg_unit = row[7]
            variables = {}
            for var_ind, var_name in enumerate(var_name_lst):
                variables[var_name] = self.get_var_value_by_name(c, var_name)
            print('[Updating] Account [{}], running algorithm: [{}], \n[Updating] with formulation: {}'.format(acc_name, alg_name, alg_form))
            # alg_py is the algorithm python file name in Algorithm folder
            # alg_name is the function name in the alg_py file
            # now pass the variables and run the algorithm
            alg_value = self.update_account_value(alg_py, alg_name, variables)
            unit_convert = self.check_unit_conversion('dollar',alg_unit)
            if unit_convert:
                alg_value = self.convert_unit(alg_value,alg_unit,'dollar')
            self.update_total_cost(c, acc_name, alg_value, 'dollar')
            print(' ')

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
        return None

    def roll_up_account_table(self, c, from_level=3, to_level=0, gncoa=False):
        """
        Rolls up the account table from level 3 to 0.
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Rolling up account table '.center(100,'='))
        print('\n')
        for i in range(from_level, to_level, -1):
            self.roll_up_account_table_by_level(c,i,i-1,gncoa=gncoa)
        print('[Updated]  Account table rolled up\n')
        return None

    def roll_up_account_table_by_level(self, c, from_level, to_level, gncoa=False):
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
        if gncoa:
            c.callproc('roll_up_account_table_by_gn_level',(self.acc_tabl,from_level,to_level))
        else:
            c.callproc('roll_up_account_table_by_level',(self.acc_tabl,from_level,to_level))
        return None
    
    def roll_up_account_table_GNCOA(self, c):
        """
        Rolls up the account table for the reactor model that only has limited accounts.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Rolling up account table by GNCOA '.center(100,'='))
        # remove 220A first
        c.callproc('remove_specific_row',(self.acc_tabl,'220A'))
        self.roll_up_account_table(c, from_level=4, to_level=0, gncoa=True)
        # print('[Updated]  Account table rolled up\n')
        return None
    
    def sum_cost_elements_2C(self, c):
        """
        Sums the cost elements for COA 2C (Calculated cost).

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """

        def fetch_sum_and_update(cost_type, proc_name):
            """
            Fetches the sum of the cost elements and updates the cost element.

            Parameters
            ----------
            cost_type : str
                Cost type.
            proc_name : str
                Procedure name.
            """
            # Call stored procedure and fetch results
            print(f'[Updating] Summing cost element for {cost_type}')
            c.callproc(proc_name, (self.cel_tabl, self.acc_tabl))
            for row in c.stored_results():
                results = row.fetchall()
            sum_value = results[0][0]

            # Update cost element
            self.update_cost_element_on_name(c, cost_type, sum_value)
            return sum_value
        
        print(' Summing cost elements for direct cost '.center(100, '='))

        # Fetch and update cost elements
        sum_2c_fac = fetch_sum_and_update('2c_fac', 'sum_cost_elements_2C_fac')
        sum_2c_lab = fetch_sum_and_update('2c_lab', 'sum_cost_elements_2C_lab')
        sum_2c_mat = fetch_sum_and_update('2c_mat', 'sum_cost_elements_2C_mat')

        print('[Updated] Cost elements 2c_fac, 2c_lab, 2c_mat are: '
            f'${sum_2c_fac:<11,.0f}, ${sum_2c_lab:<11,.0f}, ${sum_2c_mat:<11,.0f}')
        print('[Updated] Cost elements summed\n')

        return None

    def roll_up_lmt_account_2C(self, c):
        """
        Sums up total cost of account 2C for the reactor model that only has limited accounts.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """

        print(' Rolling up account table '.center(100,'='))
        print('\n')
        c.callproc('roll_up_lmt_account_2C', (self.acc_tabl,))

        print('[Updated]  Account table summed up for calculated direct cost.')
        return None
    
    def roll_up_lmt_direct_cost(self, c):
        """
        Sums up the total cost of account 2 from account 2C for 
        the reactor model that only has limited accounts.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.callproc('roll_up_lmt_direct_cost',(self.acc_tabl,))
        print('[Updated]  Account table rolled up for direct cost.\n')
        return None
    
    def cal_direct_cost_elements(self, c):
        """
        Calculates the direct cost elements for the ABR including the factory, labor, and material costs. (2C_fac, 2C_lab, 2C_mat)

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.callproc('cal_direct_cost_elements', (self.acc_tabl, self.cel_tabl))

        # After the procedure execution, fetch the OUT parameters from the cursor
        # The stored procedure call doesn't return results, but the OUT parameters are updated
        for row in c.stored_results():
            results = row.fetchall()
        fac, lab, mat = results[0]
        return fac,lab,mat
    
    def roll_up_lmt_account_table(self, c):
        """
        Rolls up the account table for the reactor model that only has limited accounts.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements
        """
        ### only update account 222 and account 2C
        self.roll_up_account_table(c, from_level=3, to_level=2)
        # print('[Updated]  Account table rolled up\n')
        self.roll_up_lmt_account_2C(c)
        self.roll_up_lmt_direct_cost(c)
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

    # def write_to_excel(self, statement, filename,conn):
    #     """
    #     Writes the results to an excel file.

    #     Parameters
    #     ----------
    #     statement : str
    #         SQL statement.
    #     filename : str
    #         Filename of the excel file.
    #     conn : MySQLConnection
    #         MySQLConnection class instantiates objects that represent a connection to the MySQL database server.
    #     """
    #     df=sql.read_sql(statement,conn)
    #     df.to_excel(filename,index=False)       
    #     print("Successfully created excel file {}".format(filename))

    def execute_accert(self, c, ut):
        """
        Executes the ACCERT program.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ut : UserTable
            UserTable class instantiates objects that can execute user input statements.
        """
        self.print_logo()

        accert = self.load_obj(input_path, accert_path).accert
        c.execute("USE accert_db")
        print(' Reading user input '.center(100, '='))
        print('\n')

        if accert.ref_model:
            self.process_reference_model(c, ut, accert)
        else:
            print('ERROR: model not found ')
            self.exit_with_error(accert)
        self.process_power_inputs(c, accert)
        self.process_variables(c, accert)
        self.process_COA(c, accert)
        self.finalize_process(c, ut, accert)
        self.generate_results(c, ut, accert)
        conn.close()
        sys.stdout.close()
        sys.stdout = stdoutOrigin

    def process_reference_model(self, c, ut, accert):
        """
        Processes the reference model.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ut : Utility class
            Utility class for processing user input.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """

        print('[USER_INPUT]', 'Reference model is', str(accert.ref_model.value), '\n')
        self.setup_table_names(accert)
        ut.setup_table_names(c, Accert)
        # if ref.model is not fusion or user defined then process cost elements:
        if Accert.ref_model != "fusion":
            ut.print_user_request_parameter(c)
        else:
            pass

    def process_power_inputs(self, c, accert):
        """
        Processes the power inputs.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """

        if accert.power:
            for inp in accert.power:
                print('[USER_INPUT]', str(inp.id), 'power is', str(inp.value.value), str(inp.unit.value), '\n')
                var_id = 'mwth' if str(inp.id) == 'Thermal' else 'mwe' if str(inp.id) == 'Electric' else None
                if var_id:
                    self.update_variable_info_on_name(c, var_id, str(inp.value.value), str(inp.unit.value))
                    self.process_super_values(c, var_id)
        else:
            # warning
            print('WARNING: No power input found in the user input file\n')            

    def process_variables(self, c, accert):
        """
        Processes the variables.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        if accert.var:
            for var_inp in accert.var:
                u_i_var_value = float(str(var_inp.value.value))
                u_i_var_unit = str(var_inp.unit.value)
                var_id = str(var_inp.id).replace('"', '')
                self.update_input_variable(c, var_id, u_i_var_value, u_i_var_unit)
                self.process_super_values(c, var_id)

    def process_super_values(self, c, var_id):
        """
        Processes the super variables.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_id : str
            Variable ID.
        """

        sup_val_lst = self.extract_super_val(c, var_id)
        if sup_val_lst:
            sup_val_lst = sup_val_lst.split(',')
        while sup_val_lst:
            sup_val = sup_val_lst.pop(0)
            if sup_val:
                self.update_super_variable(c, sup_val)
                new_sup_val = self.extract_super_val(c, sup_val)
                if new_sup_val:
                    sup_val_lst.extend(new_sup_val.split(','))

    def process_COA(self, c, accert):
        """
        Change the total cost of the account table by user inputs.
        This function is called before processing the calculation.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        if accert.l0COA and accert.l0COA.l1COA:
            for l1_inp in accert.l0COA.l1COA:
                if l1_inp.l2COA:
                    self.process_level_accounts(c, l1_inp.l2COA, accert, l1_inp.id)

    def process_level_accounts(self, c, level_accounts, accert, parent_id=None):
        """
        Processes the level accounts and begins the calculation.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        level_accounts : list
            List of level accounts.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        parent_id : str
            Parent ID.
        """
        for account in level_accounts:
            if "new" in str(account.id):
                user_added_coa = str(account.newCOA.id)
                user_added_coa_desc = str(account.newCOA.descr.value)
                if account.total_cost:
                    user_added_coa_total_cost = float(str(account.total_cost.value.value))
                    user_added_coa_total_cost_unit = str(account.total_cost.unit.value)
                    org_tc_unit = "dollar"
                    unit_convert = self.check_unit_conversion(org_tc_unit,user_added_coa_total_cost_unit)
                    if unit_convert:
                        user_added_coa_total_cost = self.convert_unit(user_added_coa_total_cost,user_added_coa_total_cost_unit,org_tc_unit)
                else:
                    user_added_coa_total_cost = 0
                print('[USER_INPUT]', 'New account', user_added_coa, user_added_coa_desc, user_added_coa_total_cost, '\n')
                self.insert_COA(c, str(parent_id),user_added_coa,user_added_coa_desc,user_added_coa_total_cost)
            # if ref.model is not fusion then process cost elements:
            if self.ref_model!="fusion":
                self.process_ce(c, account)
            else:
                if account.alg:
                    for alg in account.alg:
                        if alg.var:
                            for var in alg.var:
                                if var.alg is None:
                                    self.process_var(c, var)
                                else:
                                    self.process_alg(c, var)
                elif accout.var:
                    for var in account.var:
                        self.process_var(c, var)
            for i in range(3, 7):
                next_level = getattr(account, f'l{i}COA', None)
                if next_level:
                    self.process_level_accounts(c, next_level, accert, account.id)                

    def process_ce(self, c, account):
        """
        Processes the cost elements, either by changing variables or algorithms.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        account : Account
            Account class instantiates objects that can parse the account.
        """
        if account.ce:
            for ce in account.ce:
                if ce.alg:
                    for alg in ce.alg:
                        if alg.var:
                            for var in alg.var:
                                if var.alg is None:
                                    self.process_var(c, var)
                                else:
                                    self.process_alg(c, var)
                elif ce.var:
                    for var in ce.var:
                        self.process_var(c, var)

    def process_var(self, c, var_inp):
        """
        Processes the variables, changing the variables by user inputs, and updating the super values.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        var_inp : Variable

        """
        u_i_var_value = float(str(var_inp.value.value))
        u_i_var_unit = str(var_inp.unit.value)
        var_id = str(var_inp.id).replace('"', '')
        self.update_input_variable(c, var_id, u_i_var_value, u_i_var_unit)
        self.process_super_values(c, var_id)

    def process_alg(self, c, alg_inp):
        """
        Processes the variables with algorithm.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        alg_inp : Algorithm
        """

        for alg_var in alg_inp.alg:
            if alg_var.var:
                for var in alg_var.var:
                    var_id = str(var.id).replace('"', '')
                    u_i_var_value = float(str(var.value.value))
                    u_i_var_unit = str(var.unit.value)
                    self.update_input_variable(c, var_id, u_i_var_value, u_i_var_unit, var_type='Sub ')
        var_id = str(alg_inp.id).replace('"', '')
        self.update_super_variable(c, var_id)

    def check_and_process_total_cost(self, c, accert):
        """
        Checks and processes the total cost at the end of the calculation, 
        if the total cost has changed by user inputs. It is important to note that
        the total cost may not be reflected correctly in the cost elements table. Since
        the total cost is a sum of the cost elements, the cost elements may have changed
        by user inputs.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        if self.check_total_cost_changed(c, accert):
            print(" IMPORTANT NOTE ".center(100, '='))
            print("Some cost have changed by user inputs and may not be reflected correctly in the cost elements table.\n")
            self.process_total_cost(c, accert)

    def check_total_cost_changed(self, c, accert):
        """
        Checks if the total cost has changed.
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        changed = False
        if accert.l0COA and accert.l0COA.l1COA:
            for l1_inp in accert.l0COA.l1COA:
                if l1_inp.l2COA:
                    changed |= self.check_total_cost_accounts(c, l1_inp.l2COA, accert)
        return changed

    def check_total_cost_accounts(self, c, level_accounts, accert):
        """
        Checks if the total cost has changed for the accounts.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        level_accounts : list
            List of level accounts.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        changed = False
        for account in level_accounts:
            if account.total_cost:
                changed = True
            for i in range(3, 7):
                next_level = getattr(account, f'l{i}COA', None)
                if next_level:
                    changed |= self.check_total_cost_accounts(c, next_level, accert)
        return changed

    def process_total_cost(self, c, accert):
        """
        Changes the total cost for the accounts using the user inputs.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        if accert.l0COA and accert.l0COA.l1COA:
            for l1_inp in accert.l0COA.l1COA:
                if l1_inp.l2COA:
                    self.process_total_cost_accounts(c, l1_inp.l2COA, accert)

    def process_total_cost_accounts(self, c, level_accounts, accert):
        """
        Changes the total cost for the accounts using the user inputs for different levels.
        This function is called after calculation is done.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        level_accounts : list
            List of level accounts.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        for account in level_accounts:
            if account.total_cost:
                for total_cost_inp in account.total_cost:
                    tc_id = str(account.id).replace('"', '')
                    u_i_tc_value = float(str(total_cost_inp.value.value))
                    u_i_tc_unit = str(total_cost_inp.unit.value)
                    if accert.ref_model:
                        # TODO: change the new into any thing else
                        # check if the total cost is a new added account in account table check if
                        # the revivew status is added
                        if "new" in tc_id:
                            user_add_coa_name = str(account.newCOA.id)
                            self.update_total_cost(c, user_add_coa_name, u_i_tc_value, u_i_tc_unit)
                        else:
                            self.update_total_cost(c, tc_id, u_i_tc_value, u_i_tc_unit)
                    else:
                        self.exit_with_error(accert)
            for i in range(3, 7):
                next_level = getattr(account, f'l{i}COA', None)
                if next_level:
                    self.process_total_cost_accounts(c, next_level, accert)

    def exit_with_error(self, accert):
        """
        Exits the program with an error message.

        Parameters
        ----------
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        print("ERROR: model not found ")
        print(accert.ref_model.value)
        print("Exiting")
        sys.exit(1)

    def finalize_process(self, c, ut, accert):
        """
        Finalizes the process by extracting the affected variables, cost elements, and accounts.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ut : Utility class
            Utility class for processing user input.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """

        ut.extract_user_changed_variables(c)
        # if the model is not fusion or user assigned then process the cost elements
        # NOTE: Accert is the instance of the Accert class use Capital A
        if Accert.ref_model!="fusion" and Accert.ref_model!="user_assigned":
            # NOTE the extract_affected_cost_elements will not be executed for fusion model
            ut.extract_affected_cost_elements(c)
            self.update_new_cost_elements(c)
            ut.print_updated_cost_elements(c)
            self.roll_up_cost_elements(c)
        else:
            # if the model is fusion or user assigned model without cost elements
            # then the update_new_accounts will be executed otherwise the update_new_cost_elements should be executed
            ut.extract_affected_accounts(c)
            self.update_new_accounts(c)

    def generate_results(self, c, ut, accert):
        """
        Generates the results.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ut : Utility class
            Utility class for processing user input.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        model = Accert.ref_model
        if model in ["abr1000", "heatpipe", "lfr", "pwr12-be", "fusion"]:
            # generate results for the models in the future we can add more models
            self._generate_common_results(c, ut, accert, model)
            if model != "fusion":
                self.generate_results_table_with_cost_elements(c, conn, level=3)
        self.generate_results_table(c, conn, level=3)

    def _generate_common_results(self, c, ut, accert, model):
        """
        Generates the common results for the models.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ut : Utility class
            Utility class for processing user input.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        model : str

        """
        if model == "abr1000" or model == "heatpipe" or model == "lfr":
            self._common_cost_processing(c, accert)
            fac, lab, mat = self.cal_direct_cost_elements(c)
            all_flag = model != "lfr"
            self._print_results(ut, c, fac, lab, mat, all_flag)
        elif model == "pwr12-be":
            self._pwr12be_processing(c, ut, accert)
        elif model == "fusion":
            self._fusion_processing(c, ut, accert)

    def _common_cost_processing(self, c, accert):
        """
        Common cost processing for the models with limited accounts.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """

        self.sum_cost_elements_2C(c)
        self.update_account_table_by_cost_elements(c)
        self.check_and_process_total_cost(c, accert)
        self.roll_up_lmt_account_table(c)

    def _print_results(self, ut, c, fac, lab, mat, all_flag):
        """
        Prints the results.

        Parameters
        ----------
        ut : Utility class
            Utility class for processing user input.
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        fac : float
            Factory cost.
        lab : float
            Labor cost.
        mat : float
            Material cost.
        all_flag : bool
            Flag to print all accounts.
        """
        print(' Generating results table for review '.center(100, '='))
        print('\n')    
        if self.use_gncoa:
            ut.print_leveled_accounts_gncoa(c, all=False, cost_unit='million', level=3)
        else:
            ut.print_leveled_accounts(c, all=all_flag, tol_fac=fac, tol_lab=lab, tol_mat=mat, cost_unit='million', level=3)


    def _pwr12be_processing(self, c, ut, accert):
        """
        Processing for the pwr12-be model.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ut : Utility class
            Utility class for processing user input.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        self.update_account_table_by_cost_elements(c)
        self.check_and_process_total_cost(c, accert)
        if self.use_gncoa:
            self.roll_up_account_table_GNCOA(c)
            print(' Generating results table for review '.center(100, '='))   
            print('\n')
            ut.print_leveled_accounts_gncoa(c, all=False, cost_unit='million', level=3)
        else:
            self.roll_up_account_table(c, from_level=3, to_level=0)
            print(' Generating results table for review '.center(100, '='))   
            print('\n') 
            ut.print_leveled_accounts(c, all=True, cost_unit='million', level=3)
 

    def _fusion_processing(self, c, ut, accert):
        """
        Processing for the fusion model.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        ut : Utility class
            Utility class for processing user input.
        accert : ACCERT
            xml2obj class instantiates objects that can parse the ACCERT XML file.
        """
        self.check_and_process_total_cost(c, accert)
        self.roll_up_account_table(c, from_level=4, to_level=0)
        print(' Generating results table for review '.center(100, '='))
        print('\n')
        ut.print_leveled_accounts(c, all=False, cost_unit='million', level=4)

    def generate_results_table_with_cost_elements(self, c, conn, level=3):
        """
        Generates the results table with cost elements.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        conn : MySQLConnection
            MySQLConnection class instantiates objects that represent a connection to the MySQL database server.
        level : int
            Level of the account.
        """

        self._generate_excel(c, '_variable_affected_cost_elements.xlsx', 'extract_affected_cost_elements_w_dis', self.cel_tabl, self.var_tabl)
        self._generate_excel(c, '_updated_cost_element.xlsx', 'print_updated_cost_elements', self.cel_tabl, remove_last_col=True)

    def _generate_excel(self, c, filename_suffix, proc_name,  *args, remove_last_col=False):
        """
        Generate an Excel file from stored procedure results.
        
        Parameters:
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        proc_name : str
            Name of the stored procedure.
        filename_suffix : str
            Suffix of the filename.
        args : tuple
            Arguments for the stored procedure.
        remove_last_col : bool
            Remove the last column if required.
        """
        c.callproc(proc_name, args)
        for itered in c.stored_results():
            results = itered.fetchall()
            field_names = [i[0] for i in itered.description]
        df = pd.DataFrame(results, columns=field_names)
        if remove_last_col:
            df = df.iloc[:, :-1]  # Remove the last column if required
        filename = str(self.ref_model) + filename_suffix
        df.to_excel(filename, index=False)
        print(f"Successfully created excel file {filename}")

    def generate_results_table(self, c, conn, level=3):
        """
        Generates the results tables.
        """
        self._generate_excel(c, '_updated_account.xlsx', 'print_leveled_accounts_simple', self.acc_tabl, level)

if __name__ == "__main__":
    """
    main driver
    """    
    
    stdoutOrigin=sys.stdout 
    sys.stdout = open("output.out", "w")
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
    # NOTE: cursor is a class that instantiates objects that can execute MySQL statements
    # only commit when you are sure that the transaction is complete
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