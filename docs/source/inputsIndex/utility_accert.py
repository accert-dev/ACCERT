from prettytable import PrettyTable
import textwrap

class Utility_methods:


    def __init__(self):
        pass

    def print_table(self, c, align_key=None,align=None,format_col=None):
        """
        Prints the table in an organized format via the PrettyTable library.

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
        results = c.fetchall()
        columns = c.description
        field_names = [i[0] for i in c.description]
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
        """
        Prints the account table.

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
            c.execute("""SELECT *
                                FROM account
                                WHERE level <= %(u_i_level)s;""",{'u_i_level': str(level)})
        else:
            c.execute("""SELECT ind,
                                code_of_account, 
                                account_description,
                                total_cost,
                                unit,
                                level,
                                review_status
                                FROM account
                                WHERE level <= %(u_i_level)s;""",{'u_i_level': str(level)})

        align_key=["code_of_accout", "account_description", "total_cost"] 
        align=[ "l", "l", "r"]
        if cost_unit=='million':
            results = c.fetchall()
            columns = c.description
            field_names = [i[0] for i in c.description]
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

    def print_leveled_accounts(self, c, all=False, cost_unit='dollar',level=3):
        """
        Prints the output account table with COA line up as a nested list.

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
            c.execute("""select account.level,
                                rankedcoa.COA as code_of_account,
                                account.account_description,
                                sorted_ce.fac_cost,
                                sorted_ce.lab_cost,
                                sorted_ce.mat_cost,
                                account.total_cost,	
                                account.unit,
                                account.review_status
                                FROM account
                                JOIN 
                                (SELECT node.code_of_account,
                                        CONCAT( REPEAT(' ', COUNT(parent.code_of_account) - 1), node.code_of_account) AS COA
                                    FROM account AS node,
                                        account AS parent
                                    WHERE node.lft BETWEEN parent.lft AND parent.rgt
                                    GROUP BY node.code_of_account) as rankedcoa
                                        ON account.code_of_account=rankedcoa.code_of_account
                                        JOIN (SELECT splt_act.code_of_account,
                                    cef.cost_2017 as fac_cost,
                                    cel.cost_2017 as lab_cost,
                                    cem.cost_2017 as mat_cost
                                    FROM
                                    (SELECT code_of_account,total_cost,
                                        SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ',', 1), ',', -1) as fac_name,
                                        SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ',', 2), ',', -1) as lab_name,
                                        SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ',', 3), ',', -1) as mat_name
                                    FROM accert_db.account) as splt_act
                                    LEFT JOIN cost_element as cef 
                                    ON cef.cost_element = splt_act.fac_name
                                    LEFT JOIN cost_element as cel
                                    ON cel.cost_element = splt_act.lab_name
                                    LEFT JOIN cost_element as cem
                                    ON cem.cost_element = splt_act.mat_name
                                    ) as sorted_ce
                                ON sorted_ce.code_of_account = account.code_of_account
                                WHERE account.level <= %(u_i_level)s
                                ORDER BY account.lft;""",{'u_i_level': str(level)})
            align_key=["code_of_account", "account_description", "fac_cost", "lab_cost", "mat_cost", "total_cost"] 
            align=[ "l", "l", "r", "r", "r", "r"]
        else:
            c.execute("""SELECT rankedcoa.code_of_account,
                                account.account_description,
                                account.total_cost,	
                                account.unit,	
                                account.level,
                                account.review_status	
                        FROM account
                        JOIN 
                        (
                        SELECT node.code_of_account AS COA, CONCAT( REPEAT(' ', COUNT(parent.code_of_account) - 1), node.code_of_account) AS code_of_account
                        FROM account AS node,
                                        account AS parent
                        WHERE node.lft BETWEEN parent.lft AND parent.rgt
                        GROUP BY node.code_of_account) as rankedcoa
                        ON account.code_of_account=rankedcoa.COA
                        WHERE account.level <= %(u_i_level)s
                        ORDER BY account.lft;""",{'u_i_level': str(level)})
            align_key=["code_of_account", "account_description", "total_cost"] 
            align=[ "l", "l", "r"]
        
        if cost_unit=='million':
            results = c.fetchall()
            columns = c.description
            field_names = [i[0] for i in c.description]
            x = PrettyTable(field_names)
            for row in results:
                row = list(row)
                # NOTE the index of the row need to have a function
                # just place this as a temporary solution
                if all:
                    row[3:7] = list(map(lambda x: '{:,.2f}'.format(x/1000000), row[3:7]))
                    row[7] = 'million'
                else:
                    row[2] = '{:,.2f}'.format(row[2]/1000000)
                    row[3] = 'million'
                x.add_row(row)
            if align_key:
                for i,k in enumerate(align_key):
                    x.align[k] = align[i]
            print (x)
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
        c.execute("""SELECT * 
                    FROM algorithm;
                    """)
        self.print_table(c)
        return None

    def print_cost_element(self, c):
        """Prints the output cost element table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM cost_element;
                    """)
        self.print_table(c)
        return None

    def print_facility(self, c):
        """Prints the output facility table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM facility;
                    """)
        self.print_table(c)
        return None

    def print_escalation(self, c):
        """Prints the output escalation table.

        Parameters
        ----------
        c : MySQLCursor 
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM escalation;
                    """)
        self.print_table(c)
        return None

    def print_variable(self, c):
        """Prints the output variable table.
        
        Parameters
        ----------
        c : MySQLCursor 
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM variable;
                    """)
        self.print_table(c)
        return None

    def print_abr_account(self, c):
        """Prints the output abr account table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM abr_account;
                    """)
        self.print_table(c)
        return None

    def print_abr_cost_element(self, c):
        """Prints the output abr cost element table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM abr_cost_element;
                    """)
        self.print_table(c)
        return None

    def print_abr_variable(self, c):
        """Prints the output abr variable table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM abr_variable;
                    """)
        self.print_table(c)
        return None

    def print_abr_variable_links(self, c):
        """Prints the output abr variable links table.
        
        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT *
                    FROM abr_variable_links;
                    """)
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
        if all:
            c.execute("""SELECT va.ind, va.var_name, affectv.ce_affected
                        FROM accert_db.variable as va JOIN
                        (SELECT variable,group_concat(ce) as ce_affected
                        FROM accert_db.variable_links
                        group by variable) as affectv
                        on va.var_name = affectv.variable
                        where va.var_value IS NULL
                        order by va.ind;""")
            self.print_table(c)
        else:
            c.execute("""SELECT va.var_name,affectv.ce_affected
                        FROM accert_db.variable as va JOIN
                        (SELECT variable,group_concat(ce) as ce_affected
                        FROM accert_db.variable_links
                        group by variable) as affectv
                        on va.var_name = affectv.variable
                        where va.var_value IS NULL
                        order by va.ind;""")
            results = c.fetchall()
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
        c.execute("""SELECT ind,
                            cost_element, 
                            cost_2017,	
                            sup_cost_ele, 
                            account,
                            updated 
                    FROM cost_element
                    WHERE updated = 1""")
        self.print_table(c)

    def extract_original_cost_elements(self, c):
        """Extracts the original affected cost elements from the cost element table. (This function is ONLY used for debugging)

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        # # ce.updated, ce.algno
        c.execute(""" SELECT ce.cost_element,	ce.cost_2017 as orignal_cost
                        FROM cost_element as ce JOIN 
                        (SELECT vl.ce
                        FROM
                        (SELECT * FROM variable
                        WHERE user_input = 1) as va
                        JOIN variable_links as vl
                        on va.var_name = vl.variable) as ce_affected
                        on ce.cost_element = ce_affected.ce""")
        self.print_table(c)
        return None
        
    def extract_affected_cost_elements(self,c):
        """Extracts affected cost elements from cost element table and groups them by changed variables.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Extracting affected cost elements '.center(100,'='))
        print('\n')
        c.execute(""" SELECT vl.variable, group_concat(vl.ce)
                        FROM
                        (SELECT * FROM variable
                        WHERE user_input = 1) as va
                        JOIN variable_links as vl
                        on va.var_name = vl.variable
                        GROUP BY vl.variable""")
        results = c.fetchall()
        for row in results:
            print('variable "{}" affects cost element(s):'.format(row[0]))
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
        c.execute("""SELECT var_name,var_description, var_value, var_unit 
                        FROM `accert_db`.`variable` 
                        WHERE user_input = 1
                        ORDER BY var_name;""")
        self.print_table(c,format_col=[3])
        return None

    def extract_changed_cost_elements(self,c):
        """Extracts changed cost elements from cost element table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print('Extracting changed cost elements'.center(100,'='))
        c.execute("""SELECT cost_element, cost_2017
                    FROM `accert_db`.`cost_element`
                    WHERE updated != 0
                    ORDER BY account, cost_element;""")
        self.print_table(c,format_col=[2])
        return None

    def extract_user_changed_abr_variables(self,c):
        """Extracts user changed abr variables from abr variable table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print('Extracting user changed variables'.center(100,'='))
        c.execute("""SELECT var_name, var_description, var_value, var_unit 
                        FROM `accert_db`.`abr_variable` 
                        WHERE user_input = 1
                        ORDER BY var_name;""")
        self.print_table(c,format_col=[3])
        return None

    def extract_affected_abr_cost_elements(self,c):
        """Extracts the affected abr cost elements from the abr cost element table group by changed variables.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        print(' Extracting affected cost elements '.center(100,'='))
        print('\n')
        c.execute(""" SELECT vl.variable, group_concat(vl.ce)
                        FROM
                        (SELECT * FROM abr_variable
                        WHERE user_input = 1) as va
                        JOIN abr_variable_links as vl
                        on va.var_name = vl.variable
                        GROUP BY vl.variable""")
        results = c.fetchall()
        for row in results:
            print('variable "{}" affects cost element(s):'.format(row[0]))
            print('{}\n'.format(textwrap.fill(row[1], 100)))
        return None

    def print_updated_abr_cost_elements(self,c):
        """Prints the output updated abr cost elements table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        """
        c.execute("""SELECT ind,
                            cost_element, 
                            cost_2017,	
                            sup_cost_ele, 
                            account,
                            updated 
                        FROM abr_cost_element
                                WHERE updated = 1""")
        self.print_table(c)
        return None

    def print_leveled_abr_accounts(self, c, abr_fac,abr_lab,abr_mat,all=False, 
                                    cost_unit='dollar',level=3):
        """Prints the output leveled abr accounts table.

        Parameters
        ----------
        c : MySQLCursor
            MySQLCursor class instantiates objects that can execute MySQL statements.
        abr_fac : float
            Abr_fac is the ABR-1000 factor for factory cost.
        abr_lab : float
            Abr_lab is the ABR-1000 factor for labor cost.
        abr_mat : float
            Abr_mat is the ABR-1000 factor for material cost.
        all : bool, optional
            All is the flag to print all accounts or not. (By default False, or not)
        cost_unit : str, optional
            Cost_unit is the cost unit. (By default 'dollar')
        level : int, optional
            Level is the level of the account. (By default 3)
        """
        if all:
            c.execute("""SELECT abr_account.level,
                                rankedcoa.COA as code_of_account,
                                abr_account.account_description,
                                sorted_ce.fac_cost,
                                sorted_ce.lab_cost,
                                sorted_ce.mat_cost,
                                abr_account.total_cost,	
                                abr_account.unit,
                                abr_account.review_status
                            FROM abr_account 
                            JOIN 
                            (SELECT node.code_of_account,
                                    CONCAT( REPEAT(' ', COUNT(parent.code_of_account) - 1), node.code_of_account) AS COA
                                FROM abr_account AS node,
                                    abr_account AS parent
                                WHERE node.lft BETWEEN parent.lft AND parent.rgt
                                GROUP BY node.code_of_account) as rankedcoa
                                    ON abr_account.code_of_account=rankedcoa.code_of_account
                                    JOIN (SELECT splt_act.code_of_account,
                                                cef.cost_2017 as fac_cost,
                                                cel.cost_2017 as lab_cost,
                                                cem.cost_2017 as mat_cost
                                                FROM
                                                (SELECT code_of_account,total_cost,supaccount,
                                                SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ',', 1), ',', -1) as fac_name,
                                                SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ',', 2), ',', -1) as lab_name,
                                                SUBSTRING_INDEX(SUBSTRING_INDEX(cost_elements, ',', 3), ',', -1) as mat_name
                                                FROM accert_db.abr_account) as splt_act
                                                LEFT JOIN abr_cost_element as cef 
                                                ON cef.cost_element = splt_act.fac_name
                                                LEFT JOIN abr_cost_element as cel
                                                ON cel.cost_element = splt_act.lab_name
                                                LEFT JOIN abr_cost_element as cem
                                                ON cem.cost_element = splt_act.mat_name) as sorted_ce
                            ON sorted_ce.code_of_account = abr_account.code_of_account
                            WHERE abr_account.level <= 3
                            ORDER BY abr_account.lft;""")
            align_key=["code_of_account", "account_description", "fac_cost", "lab_cost", "mat_cost", "total_cost"] 
            align=[ "l", "l", "r", "r", "r", "r"]
        else:
            c.execute("""SELECT rankedcoa.code_of_account,
                                abr_account.account_description,
                                abr_account.total_cost,	
                                abr_account.unit,	
                                abr_account.level,
                                abr_account.review_status	
                            FROM abr_account
                            JOIN 
                            (
                            SELECT node.code_of_account AS COA, CONCAT( REPEAT(' ', COUNT(parent.code_of_account) - 1), node.code_of_account) AS code_of_account
                            FROM abr_account AS node,
                                            abr_account AS parent
                            WHERE node.lft BETWEEN parent.lft AND parent.rgt
                            GROUP BY node.code_of_account) as rankedcoa
                            ON abr_account.code_of_account=rankedcoa.COA
                            WHERE abr_account.level <= %(u_i_level)s
                            ORDER BY abr_account.lft;""",{'u_i_level': str(level)})
            align_key=["code_of_account", "account_description", "total_cost"] 
            align=[ "l", "l", "r"]
        
        if cost_unit=='million':
            results = c.fetchall()
            columns = c.description
            # print()
            # field_names = [i[0] for i in c.description]
            field_names = [i[0] for i in columns]
            x = PrettyTable(field_names)
            row0=list(results[0])
            if all:
                row0[3]="{:,.2f}".format(abr_fac/1000000)
                row0[4]="{:,.2f}".format(abr_lab/1000000)
                row0[5]="{:,.2f}".format(abr_mat/1000000)
                row0[6]="{:,.2f}".format(row0[6]/1000000)
                row0[7]="million"
            else:
                row0[2] = '{:,.2f}'.format(row0[2]/1000000)
                row0[3] = 'million'
            x.add_row(row0)
            for row in results[1:]:
                row = list(row)
                # NOTE the index of the row need to have a function
                # just place this as a temporary solution
                if all:
                    row[3:7] = list(map(lambda x: '{:,.2f}'.format(x/1000000), row[3:7]))
                    row[7] = 'million'
                else:
                    row[2] = '{:,.2f}'.format(row[2]/1000000)
                    row[3] = 'million'
                x.add_row(row)
            if align_key:
                for i,k in enumerate(align_key):
                    x.align[k] = align[i]
            print (x)
        else:
            self.print_table(c, align_key, align)
        return None