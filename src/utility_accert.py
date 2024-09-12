from prettytable import PrettyTable
import textwrap

class Utility_methods:
    """
    Utility class
    """

    def __init__(self):
        self.acc_tabl = None
        self.cel_tabl = None
        self.var_tabl = None
        self.vlk_tabl = None
        self.alg_tabl = None
        self.esc_tabl = None
        self.fac_tabl = None        
        pass
    
    def setup_table_names(self,c,Accert):
        self.acc_tabl = Accert.acc_tabl
        self.cel_tabl = Accert.cel_tabl
        self.var_tabl = Accert.var_tabl
        # self.vlk_tabl = Accert.vlk_tabl
        self.alg_tabl = Accert.alg_tabl
        self.esc_tabl = Accert.esc_tabl
        self.fac_tabl = Accert.fac_tabl

        return None

    def print_table(self, c, align_key=None,align=None,format_col=None):
        """Prints the table in an organized format via the PrettyTable library.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        align_key : list[str], optional
            List of column names to align. (By default none)
        align : list[str], optional
            List of alignments. Left, right or center. (By default none)
        format_col : list[str], optional
            List of column names to format. (By default none)
        """
        for itered in c.stored_results():
            results = itered.fetchall()
            field_names = [i[0] for i in itered.description]

        # results = c.fetchall()
        # columns = c.description
        # field_names = [i[0] for i in c.description]
        x = PrettyTable(field_names)
        for row in results:
            row = list(row)
            if format_col:
                for i in format_col:
                    row[i-1]= '{:,.2f}'.format(row[i-1])
            x.add_row(row)
        if align_key:
            for i,k in enumerate(align_key):
                x.align[k] = align[i]
        print('\n')
        print (x)
        print('\n')
        return None

    def print_account(self, c, all=False, cost_unit='dollar',level=3):
        """Prints the account table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        all : bool, optional
            If True, print all the accounts columns. (By default False)
        cost_unit : str, optional
            Unit of the total cost. (By default 'dollar')
        level : int, optional
            Level of account. (By default 3)
        """    
        if all:
            # DELIMITER $$
            # CREATE DEFINER=`root`@`localhost` PROCEDURE `print_account_all`(IN table_name varchar(50),
            #                                                                 IN level int)
            # BEGIN
            #     SET @stmt=CONCAT('SELECT * FROM ',table_name,' WHERE level <= ?');
            #     PREPARE stmt FROM @stmt;
            #     SET @level=level;
            #     EXECUTE stmt USING @level;
            #     DEALLOCATE PREPARE stmt;
            # END$$
            # DELIMITER ;

            c.callproc('print_account_all', (self.acc_tabl,level))

            # c.execute("""SELECT *
            #                     FROM account
            #                     WHERE level <= %(u_i_level)s;""",{'u_i_level': str(level)})
        else:
            # DELIMITER $$
            # CREATE DEFINER=`root`@`localhost` PROCEDURE `print_account_simple`(IN table_name varchar(50),
            #                                                                    IN level int)
            # BEGIN
            #     SET @stmt=CONCAT('SELECT ind,
            #                             code_of_account,
            #                             account_description,
            #                             total_cost,
            #                             unit,
            #                             level,
            #                             review_status
            #                             FROM ',table_name,' WHERE level <= ?');
            #     PREPARE stmt FROM @stmt;
            #     SET @level=level;
            #     EXECUTE stmt USING @level;
            #     DEALLOCATE PREPARE stmt;
            # END$$
            # DELIMITER ;

            c.callproc('print_account_simple', (self.acc_tabl,level))
            # c.execute("""SELECT ind,
            #                     code_of_account, 
            #                     account_description,
            #                     total_cost,
            #                     unit,
            #                     level,
            #                     review_status
            #                     FROM account
            #                     WHERE level <= %(u_i_level)s;""",{'u_i_level': str(level)})

        align_key=["code_of_accout", "account_description", "total_cost"] 
        align=[ "l", "l", "r"]
        if cost_unit=='million':
            for row in c.stored_results():
                results = row.fetchall()
                field_names = [i[0] for i in row.description]
            # results = c.fetchall()
            # columns = c.description
            # field_names = [i[0] for i in c.description]
            x = PrettyTable(field_names)
            for row in results:
                row = list(row)
            # NOTE the index of the row need to have a function
                row[3]= '{:,.3f}'.format(row[3]/1000000)
                row[4]= 'million'
                x.add_row(row)
            if align_key:
                for i,k in enumerate(align_key):
                    x.align[k] = align[i]
            print (x)
        else:
            # print(c)
            self.print_table(c, align_key, align)
        return None

    def print_leveled_accounts(self, c, all=False,tol_fac=None,tol_lab= None,tol_mat=None, cost_unit='dollar',level=3):
        """Prints the output account table with COA line up as a nested list.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        all : bool, optional
            If True, print all the accounts columns. (By default False)
        cost_unit : str, optional
            Unit of the total cost. (By default 'dollar')
        level : int, optional   
            Level of account. (By default 3)
        """
        if all:
            # DELIMITER $$
            # CREATE DEFINER=`root`@`localhost` PROCEDURE `print_leveled_accounts_all`(IN acc_table varchar(50),
            #                                                                         IN  cel_table varchar(50),
            #                                                                         IN  level int)
            # BEGIN
            #     SET @stmt=CONCAT('SELECT acc.level,
            #                             rankedcoa.COA as code_of_account,
            #                             acc.account_description,
            #                             sorted_ce.fac_cost,
            #                             sorted_ce.lab_cost,
            #                             sorted_ce.mat_cost,
            #                             acc.total_cost,
            #                             acc.unit,
            #                             acc.review_status
            #                             FROM ',acc_table,' as acc
            #                             JOIN
            #                             (SELECT node.code_of_account,
            #                                     CONCAT( REPEAT(" ", COUNT(parent.code_of_account) - 1), node.code_of_account) AS COA
            #                                 FROM ',acc_table,' AS node,
            #                                     ',acc_table,' AS parent
            #                                 WHERE node.lft BETWEEN parent.lft AND parent.rgt
            #                                 GROUP BY node.code_of_account) as rankedcoa
            #                                 ON acc.code_of_account=rankedcoa.code_of_account
            #                                 JOIN (SELECT splt_act.code_of_account,
            #                                     cef.cost_2017 as fac_cost,
            #                                     cel.cost_2017 as lab_cost,
            #                                     cem.cost_2017 as mat_cost
            #                                     FROM 
            #                                     (SELECT code_of_account,total_cost,
            #                                             SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ",", 1), ",", -1) AS fac_name,
            #                                             SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ",", 2), ",", -1) AS lab_name,
            #                                             SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ",", 3), ",", -1) AS mat_name
            #                                             FROM ',acc_table,') as splt_act
            #                                     LEFT JOIN ',cel_table,' as cef
            #                                     ON cef.cost_element= splt_act.fac_name
            #                                     LEFT JOIN ',cel_table,' as cel
            #                                     ON cel.cost_element= splt_act.lab_name
            #                                     LEFT JOIN ',cel_table,' as cem
            #                                     ON cem.cost_element= splt_act.mat_name) as sorted_ce
            #                                     ON sorted_ce.code_of_account=acc.code_of_account
            #                                     WHERE acc.level <= ?
            #                                     ORDER BY acc.lft;');
            #     PREPARE stmt FROM @stmt;
            #     SET @level=level;
            #     EXECUTE stmt USING @level;
            #     DEALLOCATE PREPARE stmt;
            # END$$
            # DELIMITER ;

            c.callproc('print_leveled_accounts_all', (self.acc_tabl,self.cel_tabl,level))
            align_key=["code_of_account", "account_description", "fac_cost", "lab_cost", "mat_cost", "total_cost"] 
            align=[ "l", "l", "r", "r", "r", "r"]
        else:
            # DELIMITER $$
            # CREATE DEFINER=`root`@`localhost` PROCEDURE `print_leveled_accounts_simple`(IN acc_table VARCHAR(255), IN level INT)
            # BEGIN
            #     SET @stmt = CONCAT('SELECT rankedcoa.code_of_account,
            #                     acc.account_description,
            #                     acc.total_cost,
            #                     acc.unit,
            #                     acc.level,
            #                     acc.review_status
            #                     FROM ',acc_table,' as acc
            #                     JOIN
            #                     (SELECT node.code_of_account AS COA , CONCAT( REPEAT(" ", COUNT(parent.code_of_account) - 1), node.code_of_account) AS code_of_account
            #                     FROM ',acc_table,' AS node,
            #                                     ',acc_table,' AS parent
            #                     WHERE node.lft BETWEEN parent.lft AND parent.rgt
            #                     GROUP BY node.code_of_account) as rankedcoa
            #                     ON acc.code_of_account=rankedcoa.COA
            #                     WHERE acc.level <= ?');
            #     PREPARE stmt FROM @stmt;
            #     SET @level=level;
            #     EXECUTE stmt USING @level;
            #     DEALLOCATE PREPARE stmt;
            # END$$
            # DELIMITER ;
            c.callproc('print_leveled_accounts_simple', (self.acc_tabl,level))
            # c.execute("""SELECT rankedcoa.code_of_account,
            #                     account.account_description,
            #                     account.total_cost,	
            #                     account.unit,	
            #                     account.level,
            #                     account.review_status	
            #             FROM account
            #             JOIN 
            #             (
            #             SELECT node.code_of_account AS COA, CONCAT( REPEAT(" ", COUNT(parent.code_of_account) - 1), node.code_of_account) AS code_of_account
            #             FROM account AS node,
            #                             account AS parent
            #             WHERE node.lft BETWEEN parent.lft AND parent.rgt
            #             GROUP BY node.code_of_account) as rankedcoa
            #             ON account.code_of_account=rankedcoa.COA
            #             WHERE account.level <= %(u_i_level)s
            #             ORDER BY account.lft;""",{'u_i_level': str(level)})
            align_key=["code_of_account", "account_description", "total_cost"] 
            align=[ "l", "l", "r"]
        
        if cost_unit=='million':
            for row in c.stored_results():
                results = row.fetchall()
                field_names = [i[0] for i in row.description]
            # results = c.fetchall()
            # columns = c.description
            # field_names = [i[0] for i in c.description]
            x = PrettyTable(field_names)
            for idx, row in enumerate(results):
                row = list(row)
                if all:
                    # if index is 0, and tol_fac, tol_lab, tol_mat are not None, format the values
                    if idx == 0 and tol_fac and tol_lab and tol_mat:
                        # First row special formatting
                        row[3] = "{:,.2f}".format(tol_fac / 1000000)
                        row[4] = "{:,.2f}".format(tol_lab / 1000000)
                        row[5] = "{:,.2f}".format(tol_mat / 1000000)
                        row[6] = "{:,.2f}".format(row[6] / 1000000)
                    else:
                        # Format other rows or print 0 if value is None
                        row[3:7] = ['{:,.2f}'.format(x / 1000000) if x else '0' for x in row[3:7]]
                else:
                    # Format only the third column for other cases
                    row[2] = '{:,.2f}'.format(row[2] / 1000000)
                
                x.add_row(row)

            if align_key:
                for i,k in enumerate(align_key):
                    x.align[k] = align[i]
            print(x)
        else:
            self.print_table(c, align_key, align)
        return None
                                        
    def print_algorithm(self, c):
        """Prints the output algorithm table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `print_table`(IN table_name VARCHAR(255))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT * FROM ',table_name);
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('print_table', (self.alg_tabl,))
        self.print_table(c)
        return None

    def print_cost_element(self, c):
        """Prints the output cost element table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.callproc('print_table', (self.cel_tabl,))
        self.print_table(c)
        return None

    def print_facility(self, c):
        """Prints the output facility table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.callproc('print_table', (self.fac_tabl,))
        # c.execute("""SELECT *
        #             FROM facility;
        #             """)
        self.print_table(c)
        return None

    def print_escalation(self, c):
        """Prints the output escalation table.

        Parameters
        ----------
        c : MySQLCursor 
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.callproc('print_table', (self.esc_tabl,))
        # c.execute("""SELECT *
        #             FROM escalation;
        #             """)
        self.print_table(c)
        return None

    def print_variable(self, c):
        """Prints the output variable table.
        
        Parameters
        ----------
        c : MySQLCursor 
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.callproc('print_table', (self.var_tabl,))
        # c.execute("""SELECT *
        #             FROM variable;
        #             """)
        self.print_table(c)
        return None

    def print_user_request_parameter(self,c, all=False):
        """Prints the output user request parameter table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        all : bool, optional
            If True, prints all columns. (By default False)
        """
            # DELIMITER $$
            # CREATE DEFINER=`root`@`localhost` PROCEDURE `print_user_request_parameter`(IN all_col BOOLEAN,
            #                                                                            IN var_table VARCHAR(50), 
            #                                                                            IN vlk_table VARCHAR(50))
            # BEGIN
            #     IF all_col THEN
            # 		SET @stmt = CONCAT('SELECT va.ind, va.var_name, affectv.ce_affected FROM ',var_table,' as va JOIN 
            # 								(SELECT variable, group_concat(ce) as ce_affected
            # 								FROM ',vlk_table,' as vlk 
            # 								group by variable) as affectv on va.var_name = affectv.variable
            # 								where va.var_value IS NULL
            # 								order by va.ind');
            #     ELSE
            #         SET @stmt = CONCAT('SELECT va.var_name, affectv.ce_affected FROM ',var_table,' as va JOIN
            #                             (SELECT variable, group_concat(ce) as ce_affected
            #                             FROM ',vlk_table,' as vlk
            #                             group by variable) as affectv on va.var_name = affectv.variable
            #                             where va.var_value IS NULL
            #                             order by va.ind;');
            #     END IF;
            #     PREPARE stmt FROM @stmt;
            #     EXECUTE stmt;
            #     DEALLOCATE PREPARE stmt;
            # END$$
            # DELIMITER ;
        if all:
            c.callproc('print_user_request_parameter', (True, self.var_tabl, self.cel_tabl))
            self.print_table(c)
        else:
            c.callproc('print_user_request_parameter', (False, self.var_tabl, self.cel_tabl))
            # c.execute("""SELECT va.var_name,affectv.ce_affected
            #             FROM accert_db_test.variable as va JOIN
            #             (SELECT variable,group_concat(ce) as ce_affected
            #             FROM accert_db_test.variable_links
            #             group by variable) as affectv
            #             on va.var_name = affectv.variable
            #             where va.var_value IS NULL
            #             order by va.ind;""")
            for row in c.stored_results():
                    results = row.fetchall()

            for row in results:
                print('Parameter "{}" is required for cost elements:'.format(row[0]))
                # print(row[1])
                print('{}\n'.format(textwrap.fill(row[1], 100)))
                # print('Parameter "{}" is required\n'.format(row[0]))
        return None

    def print_updated_cost_elements(self, c):
        """Prints the output updated cost elements table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `print_updated_cost_elements`(IN cel_table VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT ind,
        #                                 cost_element,
        #                                 cost_2017,    
        #                                 sup_cost_ele,
        #                                 account,
        #                                 updated
        #                         FROM ',cel_table,'
        #                         WHERE updated = 1');
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;

        c.callproc('print_updated_cost_elements', (self.cel_tabl,))
        self.print_table(c)
 
    def extract_affected_cost_elements(self,c):
        """Extracts affected cost elements from cost element table and groups them by changed variables.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Extracting affected cost elements '.center(100,'='))
        print('\n')
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `extract_affected_cost_elements`(IN cel_table varchar(50),
        #                                                                               IN var_table varchar(50))
        # BEGIN
        #     SET @stmt = CONCAT("SELECT va.var_name, (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        #         FROM ", cel_table, " ce
        #         WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
        #                         FROM
        #                         (SELECT * FROM ",var_table,"
        #                         WHERE user_input = 1) as va
        #                         WHERE (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        # 								FROM ", cel_table, " ce
        # 						WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) IS NOT NULL
        #                         ");
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END
        # DELIMITER ;

        c.callproc('extract_affected_cost_elements',(self.cel_tabl,self.var_tabl))
        for row in c.stored_results():
            results = row.fetchall()
        for row in results:
            print('variable "{}" affects cost element(s):'.format(row[0]))
            print('{}\n'.format(textwrap.fill(row[1], 100)))
        return None

    def extract_affected_accounts(self,c):
        """ Extracts affected accounts from account table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print('Extracting affected accounts'.center(100,'='))
        # DELIMITER $$
        # CREATE DEFINER=`root@`localhost` PROCEDURE `extract_affected_accounts`(IN acc_table VARCHAR(50),
        #                                                                         IN var_table VARCHAR(50)) 
        # BEGIN
        #     SET @stmt = CONCAT('SELECT va.var_name,
        #                             (SELECT GROUP_CONCAT(ac.code_of_account SEPARATOR ", ")
        #                             FROM ',acc_table,' ac
        #                             WHERE FIND_IN_SET(va.var_name, REPLACE(ac.variables, " ", "")) > 0) AS ac_affected
        #                             FROM
        #                             (SELECT * FROM ',var_table,'
        #                             WHERE user_input = 1) as va
        #                             WHERE (SELECT GROUP_CONCAT(ac.code_of_account SEPARATOR ", ")
        #                             FROM ',acc_table,' ac
        #                             WHERE FIND_IN_SET(va.var_name, REPLACE(ac.variables, " ", "")) > 0) IS NOT NULL;');
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('extract_affected_accounts',(self.acc_tabl,self.var_tabl))
        for row in c.stored_results():
            results = row.fetchall()
        for row in results:
            print('variable "{}" affects account(s):'.format(row[0]))
            print('{}\n'.format(textwrap.fill(row[1], 100)))
        return None

    def extract_user_changed_variables(self,c):
        """Extracts user changed variables from variable table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print('Extracting user changed variables'.center(100,'='))
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `extract_user_changed_variables`(IN table_name VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT var_name,var_description, var_value, var_unit
        #                         FROM ', table_name, ' WHERE user_input = 1 ORDER BY var_name;');
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        c.callproc('extract_user_changed_variables',(self.var_tabl,))
        # c.execute("""SELECT var_name,var_description, var_value, var_unit 
        #                 FROM `accert_db_test`.`variable` 
        #                 WHERE user_input = 1
        #                 ORDER BY var_name;""")
        self.print_table(c,format_col=[3])
        return None

    def extract_changed_cost_elements(self,c):
        """Extracts changed cost elements from the cost element table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        # DELIMITER $$
        # CREATE DEFINER=`root`@`localhost` PROCEDURE `extract_changed_cost_elements`(IN cel_table VARCHAR(50))
        # BEGIN
        #     SET @stmt = CONCAT('SELECT cost_element, cost_2017
        #                         FROM ',cel_table,'
        #                         WHERE updated != 0
        #                         ORDER BY account, cost_element;');
        #     PREPARE stmt FROM @stmt;
        #     EXECUTE stmt;
        #     DEALLOCATE PREPARE stmt;
        # END$$
        # DELIMITER ;
        print('Extracting changed cost elements'.center(100,'='))
        c.callproc('extract_changed_cost_elements',(self.cel_tabl,))
        
        # c.execute("""SELECT cost_element, cost_2017
        #             FROM `accert_db_test`.`cost_element`
        #             WHERE updated != 0
        #             ORDER BY account, cost_element;""")
        self.print_table(c,format_col=[2])
        return None
