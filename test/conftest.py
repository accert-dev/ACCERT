import pytest
import mysql.connector
import os
import configparser


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
    database="accert_db_test",
    auth_plugin="mysql_native_password"
    )
    return conn

@pytest.fixture
def cursor(conn):
    return conn.cursor()

