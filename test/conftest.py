import pytest
import mysql.connector
import os
import sys
import configparser
import glob
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


@pytest.fixture
def input_params_data():
    input_params_file = "./OT01A_i1_r5_rev6.csv"
    return pd.read_csv(input_params_file).set_index("var_name").transpose()


@pytest.fixture
def conn():
    test_folder = os.path.dirname(os.path.abspath(__file__))
    code_folder = os.path.join(test_folder, os.pardir)
    initfile = os.path.join(code_folder, 'src/install.conf')
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
    return conn

@pytest.fixture
def cursor(conn):
    return conn.cursor()

@pytest.fixture
def prepare_environment():
    """Clean up 'output.out' and any relevant Excel files before running the test."""
    # Patterns for files to clean up
    cleanup_patterns = ["output.out", "*_updated_account.xlsx", "*_updated_cost_element.xlsx", "*_variable_affected_cost_elements.xlsx"]
    
    # Remove files matching the patterns
    for pattern in cleanup_patterns:
        for filename in glob.glob(pattern):
            os.remove(filename)
    yield

@pytest.fixture
def excel_patterns():
    return ["*_updated_account.xlsx", "*_updated_cost_element.xlsx", "*_variable_affected_cost_elements.xlsx"]
