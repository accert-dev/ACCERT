import pytest
import os
import sys
import glob
import shutil
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


@pytest.fixture
def input_params_data():
    input_params_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OT01A_i1_r5_rev6.csv")
    return pd.read_csv(input_params_file).set_index("var_name").transpose()


@pytest.fixture
def conn(tmp_path):
    from sqlite_accert_connection import connect

    source_db = os.path.join(SRC_PATH, "accertdb.sqlite")
    test_db = tmp_path / "accertdb.sqlite"
    shutil.copy2(source_db, test_db)
    conn = connect(db_path=test_db)
    yield conn
    conn.close()

@pytest.fixture
def cursor(conn):
    return conn.cursor()

@pytest.fixture
def prepare_environment():
    """Clean up ACCERT output files before running the test."""
    cleanup_patterns = [
        "output.out",
        "*_upd_acc_*.csv",
        "*_upd_ce_*.csv",
        "*_aff_ce_*.csv",
        "*_post_*.csv",
        "*_updated_account.xlsx",
        "*_updated_cost_element.xlsx",
        "*_variable_affected_cost_elements.xlsx",
    ]
    cleanup_dirs = [os.getcwd(), os.path.dirname(os.path.abspath(__file__))]
    
    # Remove files matching the patterns
    for cleanup_dir in cleanup_dirs:
        for pattern in cleanup_patterns:
            for filename in glob.glob(os.path.join(cleanup_dir, pattern)):
                os.remove(filename)
    yield

@pytest.fixture
def csv_patterns():
    return ["*_upd_acc_*.csv", "*_upd_ce_*.csv", "*_aff_ce_*.csv"]
