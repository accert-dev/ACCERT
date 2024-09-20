# test MySQL connection and query
import pytest

def test_mysql_connection(conn):
    """  Test the connection to the MySQL database. """
    assert conn.is_connected()

def test_database_exists(cursor):
    """  Test the existence of the database. """
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    assert ('accert_db',) in databases

def test_table_exists(cursor):
    """  Test the existence of the table. """
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    assert ('abr_account',) in tables
    assert ('abr_cost_element',) in tables
    assert ('abr_variable',) in tables
    assert ('account',) in tables
    assert ('algorithm',) in tables
    assert ('cost_element',) in tables
    assert ('escalation',) in tables
    assert ('facility',) in tables
    assert ('variable',) in tables

def test_table_columns(cursor):
    """  Test the columns of the table. """
    cursor.execute("SHOW COLUMNS FROM abr_account")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'YES', '', None, '') in columns
    assert ('code_of_account', b'varchar(20)', 'NO', 'PRI', None, '') in columns
    assert ('account_description', b'text', 'YES', '', None, '') in columns
    assert ('total_cost', b'double', 'YES', '', None, '') in columns
    assert ('level', b'int', 'YES', '', None, '') in columns
    assert ('supaccount', b'text', 'YES', '', None, '') in columns
    assert ('review_status', b'text', 'YES', '', None, '') in columns
    assert ('prn', b'double', 'YES', '', None, '') in columns


    cursor.execute("SHOW COLUMNS FROM abr_cost_element")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'NO', 'PRI', None, 'auto_increment') in columns
    assert ('cost_element', b'text', 'YES', '', None, '') in columns
    assert ('cost_2017', b'double', 'YES', '', None, '') in columns
    assert ('sup_cost_ele', b'text', 'YES', '', None, '') in columns
    assert ('alg_name', b'text', 'YES', '', None, '') in columns
    assert ('fun_unit', b'text', 'YES', '', None, '') in columns
    assert ('variables', b'text', 'YES', '', None, '') in columns
    assert ('account', b'text', 'YES', '', None, '') in columns
    assert ('algno', b'text', 'YES', '', None, '') in columns
    assert ('updated', b'int', 'YES', '', None, '') in columns


    cursor.execute("SHOW COLUMNS FROM abr_variable")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'NO', 'PRI', None, 'auto_increment')in columns
    assert ('var_name', b'text', 'YES', '', None, '')in columns
    assert ('var_description', b'text', 'YES', '', None, '')in columns
    assert ('var_value', b'double', 'YES', '', None, '')in columns
    assert ('var_unit', b'text', 'YES', '', None, '')in columns
    assert ('var_alg', b'text', 'YES', '', None, '')in columns
    assert ('var_need', b'text', 'YES', '', None, '')in columns
    assert ('v_linked', b'text', 'YES', '', None, '')in columns
    assert ('user_input', b'int', 'YES', '', None, '')in columns


    cursor.execute("SHOW COLUMNS FROM account")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'YES', '', None, '') in columns
    assert ('code_of_account', b'varchar(20)', 'NO', 'PRI', None, '') in columns
    assert ('account_description', b'text', 'YES', '', None, '') in columns
    assert ('total_cost', b'double', 'YES', '', None, '') in columns
    assert ('level', b'int', 'YES', '', None, '') in columns
    assert ('supaccount', b'text', 'YES', '', None, '') in columns
    assert ('review_status', b'text', 'YES', '', None, '') in columns
    assert ('prn', b'double', 'YES', '', None, '') in columns

    
    cursor.execute("SHOW COLUMNS FROM algorithm")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'NO', 'PRI', None, '') in columns
    assert ('alg_name', b'text', 'YES', '', None, '') in columns
    assert ('alg_for', b'text', 'YES', '', None, '') in columns
    assert ('alg_description', b'text', 'YES', '', None, '') in columns
    assert ('alg_python', b'text', 'YES', '', None, '') in columns
    assert ('alg_formulation', b'text', 'YES', '', None, '') in columns
    assert ('alg_units', b'text', 'YES', '', None, '') in columns
    assert ('variables', b'text', 'YES', '', None, '') in columns
    assert ('constants', b'text', 'YES', '', None, '') in columns

    cursor.execute("SHOW COLUMNS FROM cost_element")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'NO', 'PRI', None, 'auto_increment') in columns
    assert ('cost_element', b'varchar(20)', 'NO', 'PRI', None, '') in columns
    assert ('cost_2017', b'double', 'YES', '', None, '') in columns
    assert ('sup_cost_ele', b'text', 'YES', '', None, '') in columns
    assert ('alg_name', b'text', 'YES', '', None, '') in columns
    assert ('fun_unit', b'text', 'YES', '', None, '') in columns
    assert ('variables', b'text', 'YES', '', None, '') in columns
    assert ('account', b'text', 'YES', '', None, '') in columns
    assert ('algno', b'text', 'YES', '', None, '') in columns
    assert ('updated', b'int', 'YES', '', None, '') in columns

    cursor.execute("SHOW COLUMNS FROM escalation")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'NO', 'PRI', None, 'auto_increment') in columns
    assert ('name', b'varchar(30)', 'NO', '', None, '') in columns
    assert ('description', b'text', 'YES', '', None, '') in columns
    assert ('revision', b'text', 'YES', '', None, '') in columns
    assert ('value', b'double', 'YES', '', None, '') in columns
    assert ('year_of_interest', b'datetime', 'YES', '', None, '') in columns

    cursor.execute("SHOW COLUMNS FROM facility")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'NO', 'PRI', None, 'auto_increment') in columns
    assert ('name', b'varchar(50)', 'NO', 'PRI', None, '') in columns
    assert ('description', b'text', 'YES', '', None, '') in columns
    assert ('account', b'varchar(20)', 'YES', '', None, '') in columns
    assert ('references', b'text', 'YES', '', None, '') in columns
    assert ('reference_year', b'datetime', 'YES', '', None, '') in columns
    assert ('year_of_interest', b'datetime', 'YES', '', None, '') in columns
    assert ('escalation_name', b'varchar(30)', 'YES', '', None, '') in columns
    assert ('escalation_factorsValue', b'double', 'YES', '', None, '') in columns

    cursor.execute("SHOW COLUMNS FROM variable")
    columns = cursor.fetchall()
    assert ('ind', b'int', 'NO', 'PRI', None, 'auto_increment') in columns
    assert ('var_name', b'text', 'YES', '', None, '') in columns
    assert ('var_description', b'text', 'YES', '', None, '') in columns
    assert ('var_value', b'double', 'YES', '', None, '') in columns
    assert ('var_unit', b'text', 'YES', '', None, '') in columns
    assert ('var_alg', b'text', 'YES', '', None, '') in columns
    assert ('var_need', b'text', 'YES', '', None, '') in columns
    assert ('v_linked', b'text', 'YES', '', None, '') in columns
    assert ('user_input', b'int', 'YES', '', None, '') in columns
    