"""Build ACCERT SQLite tables for the TIMCAT LPSR base case."""
from __future__ import annotations

import argparse
import importlib
import os
import sqlite3
import sys
import types
import warnings
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIMCAT = ROOT.parent / "TIMCAT"
DEFAULT_DB = ROOT / "src" / "accertdb.sqlite"

COST_COLUMNS = {
    "fac": "Factory Equipment Cost",
    "lab": "Site Labor Cost",
    "mat": "Site Material Cost",
}

LEVEL_1_DESCRIPTIONS = {
    "21": "Structures and Improvements",
    "22": "Reactor Plant Equipment",
    "23": "Turbine Plant Equipment",
    "24": "Electric Plant Equipment",
    "25": "Miscellaneous Plant Equipment",
    "26": "Heat Rejection System",
}


def _install_bottleneck_stub() -> None:
    """TIMCAT imports bottleneck but its current sum path does not use it."""
    if "bottleneck" not in sys.modules:
        module = types.ModuleType("bottleneck")
        module.__version__ = "1.3.8"
        sys.modules["bottleneck"] = module


def _import_timcat(timcat_dir: Path):
    _install_bottleneck_stub()
    sys.path.insert(0, str(timcat_dir))
    return {
        "cost_sensitivity": importlib.import_module("cost_sensitivity"),
        "fill_scaling_table": importlib.import_module("ncet.fill_scaling_table"),
        "scale_direct_costs": importlib.import_module("ncet.scale_direct_costs"),
        "get_sub_account_iloc": importlib.import_module("ncet.get_sub_account_iloc"),
        "modularize": importlib.import_module("ncet.modularize"),
        "learn": importlib.import_module("ncet.learn"),
        "get_indirect_costs": importlib.import_module("ncet.get_indirect_costs"),
        "sum_accounts": importlib.import_module("ncet.sum_accounts"),
    }


def _read_basis_table(timcat_dir: Path):
    pandas = importlib.import_module("pandas")
    baseline = pandas.read_csv(timcat_dir / "PWR12_ME_inflated_reduced.csv", index_col="Account")
    return baseline.fillna(0)


def _run_lpsr_base_case(timcat_dir: Path):
    modules = _import_timcat(timcat_dir)
    cost_sensitivity = modules["cost_sensitivity"]

    old_cwd = Path.cwd()
    os.chdir(timcat_dir)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            scaling_inputs, scalars = cost_sensitivity.update_input_scaling(
                timcat_dir / "input_scaling_exponents.xlsx"
            )
            scaling_table, plant_characteristics = modules[
                "fill_scaling_table"
            ].fill_scaling_table(
                str(timcat_dir),
                "inputfile_LPSR.xlsx",
                base=str(timcat_dir / "PWR12_ME_inflated_reduced.csv"),
                scaling_table=scaling_inputs,
                scalars_dict=scalars,
            )
            direct = modules["scale_direct_costs"].scale_direct_costs(
                str(timcat_dir / "PWR12_ME_inflated_reduced.csv"),
                scaling_table,
                plant_characteristics,
                scalars,
            )
            index_lookup = modules["get_sub_account_iloc"].get_sub_account_iloc(direct)
            direct, module_index = modules["modularize"].modularize(
                str(timcat_dir),
                "inputfile_LPSR.xlsx",
                direct,
                10,
                scalars,
                )
            learned_plants, learning_rate = modules["learn"].learn(
                str(timcat_dir),
                "inputfile_LPSR.xlsx",
                direct,
                10,
                scalars,
                module_index,
            )
            result = learned_plants[0]
            result = modules["get_indirect_costs"].get_indirect_costs(
                result,
                plant_characteristics,
                learning_rate[0],
                scalars,
            )
            result = modules["sum_accounts"].sum_accounts(result, index_lookup)
    finally:
        os.chdir(old_cwd)

    return result, _read_basis_table(timcat_dir)


def _account_code(timcat_account: str) -> str:
    if timcat_account.startswith("A."):
        timcat_account = timcat_account[2:]
    return timcat_account.strip(".")


def _level_2_accounts(result):
    accounts = []
    for account in result.index:
        account = str(account)
        code = _account_code(account)
        if account.startswith("A.2") and len(code) == 3 and code.isdigit():
            accounts.append(account)
    return accounts


def _level_1_accounts(level_2_accounts: list[str]) -> list[str]:
    return [f"A.{code}." for code in sorted({_account_code(account)[:2] for account in level_2_accounts})]


def _ordered_accounts(level_1_accounts: list[str], level_2_accounts: list[str]) -> list[str]:
    ordered = ["A.2"]
    for level_1 in level_1_accounts:
        ordered.append(level_1)
        parent = _account_code(level_1)
        ordered.extend(
            account for account in level_2_accounts if _account_code(account).startswith(parent)
        )
    return ordered


def _description(row) -> str:
    value = row.get("Account Description")
    return "" if value is None else str(value)


def _cost(row, column: str) -> float:
    value = row.get(column, 0.0)
    return 0.0 if value is None else float(value)


def _baseline_cost(baseline, account: str, column: str) -> float:
    if account not in baseline.index:
        return 1.0
    value = baseline.loc[account].get(column, 0.0)
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0
    return value if value != 0.0 else 1.0


def build_rows(result, baseline):
    account_rows = []
    cost_element_rows = []
    variable_rows = []

    level_2_accounts = _level_2_accounts(result)
    level_1_accounts = _level_1_accounts(level_2_accounts)
    selected_accounts = _ordered_accounts(level_1_accounts, level_2_accounts)
    level_2_by_parent = {
        _account_code(level_1): [
            account for account in level_2_accounts
            if _account_code(account).startswith(_account_code(level_1))
        ]
        for level_1 in level_1_accounts
    }

    for ind, account in enumerate(selected_accounts, start=1):
        code = _account_code(account)
        row = result.loc[account] if account in result.index else None
        if code == "2":
            level = 0
            supaccount = ""
        elif len(code) == 2:
            level = 1
            supaccount = "2"
        else:
            level = 2
            supaccount = code[:2]
        description = LEVEL_1_DESCRIPTIONS.get(code, _description(row) if row is not None else "")
        if row is not None:
            total_cost = _cost(row, "Total Cost")
        elif len(code) == 2:
            total_cost = sum(_cost(result.loc[child], "Total Cost") for child in level_2_by_parent[code])
        else:
            total_cost = 0.0
        account_rows.append(
            (
                ind,
                code,
                description,
                total_cost,
                level,
                supaccount,
                "LPSR base",
                None,
            )
        )

    element_ind = 1
    variable_ind = 1
    for suffix, column in COST_COLUMNS.items():
        direct_cost = 0.0
        for level_1 in level_1_accounts:
            parent_code = _account_code(level_1)
            parent_cost = 0.0
            for account in level_2_by_parent[parent_code]:
                if account not in result.index:
                    continue
                row = result.loc[account]
                code = _account_code(account)
                final_cost = _cost(row, column)
                parent_cost += final_cost
                reference_cost = _baseline_cost(baseline, account, column)
                multiplier = final_cost / reference_cost if reference_cost else final_cost
                ref_name = f"c_{code}_{suffix}"
                mult_name = f"k_{code}_{suffix}"
                variables = f"{ref_name}, {mult_name}"
                cost_element_rows.append(
                    (
                        element_ind,
                        f"{code}_{suffix}",
                        final_cost,
                        f"{parent_code}_{suffix}",
                        "lpsr_scaled_cost",
                        "dollar",
                        variables,
                        code,
                        "LPSR1",
                        0,
                    )
                )
                variable_rows.append(
                    (
                        variable_ind,
                        ref_name,
                        f"LPSR reference for account {code} {column}",
                        reference_cost,
                        "dollar",
                        "",
                        "",
                        "",
                        0,
                    )
                )
                variable_ind += 1
                variable_rows.append(
                    (
                        variable_ind,
                        mult_name,
                        f"LPSR multiplier for account {code} {column}",
                        multiplier,
                        "1",
                        "lpsr_scaled_cost",
                        "",
                        "",
                        0,
                    )
                )
                variable_ind += 1
                element_ind += 1

            direct_cost += parent_cost
            cost_element_rows.append(
                (
                    element_ind,
                    f"{parent_code}_{suffix}",
                    parent_cost,
                    f"2_{suffix}",
                    "NO_ALG",
                    "dollar",
                    "N/A",
                    parent_code,
                    "N/A",
                    0,
                )
            )
            element_ind += 1

        cost_element_rows.append(
            (
                element_ind,
                f"2_{suffix}",
                direct_cost,
                "",
                "NO_ALG",
                "dollar",
                "N/A",
                "2",
                "N/A",
                0,
            )
        )
        element_ind += 1

    return account_rows, cost_element_rows, variable_rows


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS lpsr_account (
          ind INTEGER DEFAULT NULL,
          code_of_account TEXT NOT NULL,
          account_description text,
          total_cost REAL DEFAULT NULL,
          level INTEGER DEFAULT NULL,
          supaccount text,
          review_status text,
          prn REAL DEFAULT NULL,
          PRIMARY KEY (code_of_account)
        );
        CREATE TABLE IF NOT EXISTS lpsr_cost_element (
          ind INTEGER NOT NULL,
          cost_element text,
          cost_2017 REAL DEFAULT NULL,
          sup_cost_ele text,
          alg_name text,
          fun_unit text,
          variables text,
          account text,
          algno text,
          updated INTEGER DEFAULT NULL,
          PRIMARY KEY (ind)
        );
        CREATE TABLE IF NOT EXISTS lpsr_variable (
          ind INTEGER NOT NULL,
          var_name text,
          var_description text,
          var_value REAL DEFAULT NULL,
          var_unit text,
          var_alg text,
          var_need text,
          v_linked text,
          user_input INTEGER DEFAULT NULL,
          PRIMARY KEY (ind)
        );
        """
    )


def write_rows(db_path: Path, account_rows, cost_element_rows, variable_rows) -> None:
    conn = sqlite3.connect(db_path)
    try:
        ensure_tables(conn)
        conn.execute("DELETE FROM lpsr_account")
        conn.execute("DELETE FROM lpsr_cost_element")
        conn.execute("DELETE FROM lpsr_variable")
        conn.executemany(
            """
            INSERT INTO lpsr_account
            (ind, code_of_account, account_description, total_cost, level, supaccount, review_status, prn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            account_rows,
        )
        conn.executemany(
            """
            INSERT INTO lpsr_cost_element
            (ind, cost_element, cost_2017, sup_cost_ele, alg_name, fun_unit, variables, account, algno, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            cost_element_rows,
        )
        conn.executemany(
            """
            INSERT INTO lpsr_variable
            (ind, var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked, user_input)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            variable_rows,
        )
        conn.execute("DELETE FROM algorithm WHERE alg_name LIKE 'lpsr_%'")
        conn.executemany(
            """
            INSERT INTO algorithm
            (ind, alg_name, alg_for, alg_description, alg_python, alg_formulation, alg_units, variables, constants)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    9001,
                    "lpsr_scaled_cost",
                    "c",
                    "LPSR cost element from reference cost and multiplier",
                    "LPSRFunc",
                    "reference_cost * multiplier",
                    "dollar",
                    "reference_cost, multiplier",
                    "",
                ),
                (
                    9002,
                    "lpsr_fixed_cost",
                    "c",
                    "Fixed TIMCAT-derived LPSR cost",
                    "LPSRFunc",
                    "cost",
                    "dollar",
                    "cost",
                    "",
                ),
                (
                    9003,
                    "lpsr_total_cost",
                    "c",
                    "Sum LPSR factory, labor, and material cost elements",
                    "LPSRFunc",
                    "sum(cost_elements)",
                    "dollar",
                    "cost_element_1, cost_element_2, cost_element_n",
                    "",
                ),
                (
                    9004,
                    "lpsr_option_1_scale",
                    "v",
                    "LPSR option 1 scale using detailed unit value",
                    "LPSRFunc",
                    "(new_base_unit_value / eedb_base_unit_value) ** exponent",
                    "ratio",
                    "new_base_unit_value, eedb_base_unit_value, exponent",
                    "",
                ),
                (
                    9005,
                    "lpsr_option_2_scale",
                    "v",
                    "LPSR option 2 scale using power value",
                    "LPSRFunc",
                    "(new_base_unit_value / eedb_base_unit_value) ** exponent",
                    "ratio",
                    "new_base_unit_value, eedb_base_unit_value, exponent",
                    "",
                ),
                (
                    9006,
                    "lpsr_option_3_scale",
                    "v",
                    "LPSR direct-cost input scale",
                    "LPSRFunc",
                    "new_base_unit_value / eedb_base_unit_value",
                    "ratio",
                    "new_base_unit_value, eedb_base_unit_value",
                    "",
                ),
                (
                    9007,
                    "lpsr_option_4_scale",
                    "v",
                    "LPSR fixed-cost scale",
                    "LPSRFunc",
                    "1.0",
                    "ratio",
                    "",
                    "",
                ),
                (
                    9008,
                    "lpsr_option_0_power_scale",
                    "v",
                    "LPSR option 0 nonlinear scale",
                    "LPSRFunc",
                    "((a + b * new_base_unit_value ** exponent) * factor) / eedb_base_unit_value",
                    "ratio",
                    "a, b, new_base_unit_value, exponent, factor, eedb_base_unit_value",
                    "",
                ),
                (
                    9009,
                    "lpsr_option_0_linear_scale",
                    "v",
                    "LPSR option 0 linear scale",
                    "LPSRFunc",
                    "factor * new_base_unit_value / eedb_base_unit_value",
                    "ratio",
                    "factor, new_base_unit_value, eedb_base_unit_value",
                    "",
                ),
            ],
        )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timcat-dir", default=str(DEFAULT_TIMCAT))
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()

    result, baseline = _run_lpsr_base_case(Path(args.timcat_dir).resolve())
    account_rows, cost_element_rows, variable_rows = build_rows(result, baseline)
    write_rows(Path(args.db).resolve(), account_rows, cost_element_rows, variable_rows)
    print(
        f"Wrote {len(account_rows)} lpsr_account rows, "
        f"{len(cost_element_rows)} lpsr_cost_element rows, "
        f"and {len(variable_rows)} lpsr_variable rows."
    )


if __name__ == "__main__":
    main()
