"""Smoke tests for the bundled ACCERT SQLite database."""


def _sqlite_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row[0] for row in cursor.fetchall()}


def _sqlite_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def test_sqlite_connection(conn):
    assert conn.is_connected()


def test_database_tables_exist(cursor):
    tables = _sqlite_tables(cursor)
    assert {
        "abr_account",
        "abr_cost_element",
        "abr_variable",
        "account",
        "algorithm",
        "cost_element",
        "escalation",
        "facility",
        "variable",
    }.issubset(tables)


def test_table_columns(cursor):
    expected_columns = {
        "abr_account": {
            "ind",
            "code_of_account",
            "account_description",
            "total_cost",
            "level",
            "supaccount",
            "review_status",
            "prn",
        },
        "abr_cost_element": {
            "ind",
            "cost_element",
            "cost_2017",
            "sup_cost_ele",
            "alg_name",
            "fun_unit",
            "variables",
            "account",
            "algno",
            "updated",
        },
        "abr_variable": {
            "ind",
            "var_name",
            "var_description",
            "var_value",
            "var_unit",
            "var_alg",
            "var_need",
            "v_linked",
            "user_input",
        },
        "account": {
            "ind",
            "code_of_account",
            "account_description",
            "total_cost",
            "level",
            "supaccount",
            "review_status",
            "prn",
        },
        "algorithm": {
            "ind",
            "alg_name",
            "alg_for",
            "alg_description",
            "alg_python",
            "alg_formulation",
            "alg_units",
            "variables",
            "constants",
        },
        "cost_element": {
            "ind",
            "cost_element",
            "cost_2017",
            "sup_cost_ele",
            "alg_name",
            "fun_unit",
            "variables",
            "account",
            "algno",
            "updated",
        },
        "escalation": {
            "ind",
            "name",
            "description",
            "revision",
            "value",
            "year_of_interest",
        },
        "facility": {
            "ind",
            "name",
            "description",
            "account",
            "references",
            "reference_year",
            "year_of_interest",
            "escalation_name",
            "escalation_factorsValue",
        },
        "variable": {
            "ind",
            "var_name",
            "var_description",
            "var_value",
            "var_unit",
            "var_alg",
            "var_need",
            "v_linked",
            "user_input",
        },
    }

    for table_name, columns in expected_columns.items():
        assert columns.issubset(_sqlite_columns(cursor, table_name))
