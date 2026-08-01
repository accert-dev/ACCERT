"""Load Mirror ACCERT reference tables from a PR #50 MySQL dump.

The closed upstream Mirror PR predated the SQLite database used by ACCERT.
This script converts the Mirror-specific MySQL tables into SQLite tables and
writes reference CSVs under tutorial/accert/ref_tables.
"""
from __future__ import annotations

import argparse
import ast
import csv
import math
import re
import shutil
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "src" / "accertdb.sqlite"
DEFAULT_REF_DIR = ROOT / "tutorial" / "accert" / "ref_tables"
DEFAULT_SQL = DEFAULT_REF_DIR / "mirror_accertdb.sql"
DEFAULT_ALG_SRC = DEFAULT_REF_DIR / "MirrorFunc.py"
DEFAULT_SPLIT_ALG_SRC = DEFAULT_REF_DIR / "MirrorFunc_splitInputs.py"
DEFAULT_ALG_DST = ROOT / "src" / "Algorithm" / "MirrorFunc.py"
DEFAULT_SPLIT_ALG_DST = ROOT / "src" / "Algorithm" / "MirrorFunc_splitInputs.py"

TABLES = {
    "mirror_acco": "mirror_account.csv",
    "mirror_alg": "mirror_algorithm.csv",
    "mirror_var": "mirror_variable.csv",
}
DEFAULT_INPUT_FILE = "mirror_default_inputs.csv"

MIRROR_ACCOUNT_COLUMNS = [
    ("ind", "INTEGER"),
    ("code_of_account", "TEXT NOT NULL"),
    ("account_description", "TEXT"),
    ("total_cost", "REAL"),
    ("level", "INTEGER"),
    ("supaccount", "TEXT"),
    ("review_status", "TEXT"),
    ("prn", "REAL"),
    ("alg_name", "TEXT"),
    ("fun_unit", "TEXT"),
    ("variables", "TEXT"),
]

HUMAN_INPUT_TO_VAR = {
    "Application": "application",
    "Central Cell Length": "L_CC",
    "Construction Time": "construction_time",
    "Contingency": "include_contingency",
    "DEC Electrical Power": "P_DECe",
    "ECH Power": "P_ECH",
    "End Plug Length": "L_EP",
    "Gross Electric Power": "P_egross",
    "HF Magnet Number": "HF_magnet_number",
    "ICRH Power": "P_ICRH",
    "LF Magnet Number": "LF_magnet_number",
    "NBI Power": "P_NBI",
    "NOAK": "NOAK",
    "Net Electric Power": "P_enet",
    "Number of Modules": "N_module",
    "Overall Length": "L",
    "Thermal Power": "P_th",
    "Unit Number": "n_unit",
    "Vacuum Volume": "V_vac",
}

MIRROR_REFERENCE_VAR_OVERRIDES = {
    "n_unit": (1, "1"),
    "P_NBI": (15, "MW"),
    "P_ICRH": (10, "MW"),
    "P_ECH": (10, "MW"),
    "HF_magnet_cost": (29.1, "million"),
    "LF_magnet_cost": (6.25262, "million"),
    "CF_magnet_cost": (2.751, "million"),
    "HF_magnet_shield_cost": (47.36847787, "million"),
    "CF_magnet_number": (52.0300751726645, "1"),
    "P_egross": (158.12094932835822, "MW"),
    "P_DECe": (63.01790788032513, "MW"),
    "P_DEC": (70.0198976448057, "MW"),
    "P_th": (158.50506908190818, "MW"),
    "P_enet": (94.91500463226332, "MW"),
}

MIRROR_INPUT_UNITS = {
    "P_f": "MW",
    "P_f_L": "MW/m",
    "P_f_EP": "MW",
    "P_NBI": "MW",
    "P_ECH": "MW",
    "P_ICRH": "MW",
    "P_pump": "MW",
    "P_sub_cont": "MW",
    "P_cryo": "MW",
    "P_pfcool": "MW",
    "P_thcool": "MW",
    "P_coils": "MW",
    "P_aux": "MW",
    "construction_time": "years",
    "lifetime": "years",
    "replacement": "years",
    "hf_magnet_length": "m",
    "hf_magnet_shielding_thickness": "m",
    "a_EC": "m",
    "expander_cell_vessel_thickness": "m",
    "vacuum_gap_CC": "m",
    "first_wall_thickness": "m",
    "vacuum_vessel_thickness": "m",
    "multiplier_thickness": "m",
    "blanket_thickness": "m",
    "outer_vessel_thickness": "m",
    "L_EP": "m",
    "L_EC": "m",
    "a_CC": "m",
    "a_EP": "m",
    "application": "1",
    "cost_file": "1",
    "method": "1",
    "expander_cell_vessel_material": "1",
    "first_wall_material": "1",
    "vacuum_vessel_material": "1",
    "multiplier_material": "1",
    "blanket_coolant_material": "1",
    "blanket_structural_material": "1",
    "filename": "1",
    "run_name": "1",
}

MIRROR_GENERATED_VAR_NEEDS = {
    "P_f_CC": "P_f, P_f_EP",
    "L_CC": "P_f_CC, P_f_L",
    "L_CF": "",
    "L": "L_CC, L_EP, L_EC",
    "V_vac": "L, a_EC",
    "no_vpumps": "V_vac, vpump_cap",
    "cost_factor": "n_unit",
    "HF_magnet_cost": "n_unit, HF_magnet_number",
    "LF_magnet_cost": "n_unit, LF_magnet_number",
    "CF_magnet_cost": "n_unit, CF_magnet_number",
    "P_alpha": "E_DT, E_alpha, P_f",
    "P_n": "P_f, P_alpha",
    "P_ine": "P_NBI, eta_NBI, P_ICRH, eta_ICRH, P_ECH, eta_ECH",
    "P_pump": "f_pump, M_n, P_n",
    "P_sub_cont": "f_sub, P_f",
    "P_cryo": "f_cryo, P_f",
    "P_other": "P_pump, P_sub_cont, P_cryo",
    "P_in": "P_NBI, P_ICRH, P_ECH",
    "P_th": "M_n, P_n, P_pump, eta_pump",
    "P_the": "eta_th, P_th",
    "P_DEC": "P_in, P_alpha",
    "P_DECe": "eta_DEC, P_DEC",
    "P_egross": "application, P_DECe, P_the",
    "P_enet": "P_egross, P_ine, P_other",
    "f_aux": "P_aux, P_egross",
    "Q_sci": "P_f, P_in",
    "Q_eng": "P_egross, P_ine, P_other",
    "f_refrac": "Q_eng",
    "CF_magnet_number": "L_CC, L_CF",
}

MIRROR_GENERATED_VAR_FORMULAS = {
    "P_f_CC": ("P_f_CC = P_f - 2 * P_f_EP", "MW"),
    "L_CC": ("L_CC = P_f_CC / P_f_L", "m"),
    "L_CF": ("L_CF = 1.0", "m"),
    "L": ("L = L_CC + 2 * L_EP + 2 * L_EC", "m"),
    "V_vac": ("V_vac = L * pi * a_EC**2", "m3"),
    "no_vpumps": ("no_vpumps = V_vac / vpump_cap", "1"),
    "cost_factor": ("cost_factor = 0.80 ** (log(n_unit) / log(2))", "1"),
    "HF_magnet_cost": (
        "HF_magnet_cost = HTS_storedEnergy(25.0, 50) * 0.70 ** (log((n_unit - 1) * HF_magnet_number + 1) / log(2))",
        "million",
    ),
    "LF_magnet_cost": (
        "LF_magnet_cost = HTS_storedEnergy(10.0, 50) * 0.70 ** (log((n_unit - 1) * LF_magnet_number + 1) / log(2))",
        "million",
    ),
    "CF_magnet_cost": (
        "CF_magnet_cost = 0.7 * 3.0 * 1.31 * 0.70 ** (log((n_unit - 1) * CF_magnet_number + 1) / log(2))",
        "million",
    ),
    "P_alpha": ("P_alpha = P_f * E_alpha / E_DT", "MW"),
    "P_n": ("P_n = P_f - P_alpha", "MW"),
    "P_ine": ("P_ine = P_NBI / eta_NBI + P_ICRH / eta_ICRH + P_ECH / eta_ECH", "MW"),
    "P_pump": ("P_pump = f_pump * M_n * P_n", "MW"),
    "P_sub_cont": ("P_sub_cont = f_sub * P_f", "MW"),
    "P_cryo": ("P_cryo = f_cryo * P_f", "MW"),
    "P_other": ("P_other = P_pump + P_sub_cont + P_cryo", "MW"),
    "P_in": ("P_in = P_NBI + P_ICRH + P_ECH", "MW"),
    "P_th": ("P_th = M_n * P_n + eta_pump * P_pump", "MW"),
    "P_the": ("P_the = eta_th * P_th", "MW"),
    "P_DEC": ("P_DEC = P_in + P_alpha", "MW"),
    "P_DECe": ("P_DECe = eta_DEC * P_DEC", "MW"),
    "P_egross": (
        "P_egross = P_DECe + P_the if application == 'electricity' else P_DECe",
        "MW",
    ),
    "P_enet": ("P_enet = P_egross - (P_ine + P_other)", "MW"),
    "f_aux": ("f_aux = P_aux / P_egross", "1"),
    "Q_sci": ("Q_sci = P_f / P_in", "1"),
    "Q_eng": ("Q_eng = P_egross / (P_ine + P_other)", "1"),
    "f_refrac": ("f_refrac = 1 / Q_eng", "1"),
    "CF_magnet_number": ("CF_magnet_number = L_CC / L_CF", "1"),
}

MIRROR_CONSTANT_DEFAULTS = {
    "E_DT": (17.59e6 * 1.60218e-19, "J"),
    "E_alpha": (3.52e6 * 1.60218e-19, "J"),
}

MIRROR_VARIABLE_OVERRIDES = {
    "cost_pump": (
        "Cost of one vacuum pump, scaled from 1985 dollars",
        40000,
        "dollar/pump",
    ),
    "vpump_cap": (
        "Vacuum volume pumped by one vacuum pump in one second",
        200 / 48,
        "m3/pump",
    ),
    "no_vpumps": (
        "Number of vacuum pumps required to pump the full vacuum in one second",
        None,
        "1",
    ),
    "cost_factor": (
        "Cost scaling factor calculated from the unit number using an 0.80 learning factor",
        None,
        "1",
    ),
    "HF_magnet_cost": (
        "HF cost per magnet, not for all four",
        None,
        "million",
    ),
    "LF_magnet_cost": (
        "LF cost per magnet",
        None,
        "million",
    ),
    "CF_magnet_cost": (
        "CF cost per magnet",
        None,
        "million",
    ),
    "CF_magnet_number": (
        "One CF coil every L_CF m of central cell",
        None,
        "1",
    ),
    "HF_magnet_shield_cost": (
        "HF magnet shield cost per end plug",
        None,
        "million",
    ),
}

TYPE_REPLACEMENTS = (
    (re.compile(r"varchar\(\d+\)", re.IGNORECASE), "TEXT"),
    (re.compile(r"\bint\b", re.IGNORECASE), "INTEGER"),
    (re.compile(r"\bdouble\b", re.IGNORECASE), "REAL"),
)


def _sqlite_table_script(mysql_sql: str, table_name: str) -> str:
    without_commented_create = re.sub(
        rf"/\*CREATE TABLE `{table_name}`.*?\*/",
        "",
        mysql_sql,
        flags=re.DOTALL,
    )
    create = re.search(
        rf"CREATE TABLE `{table_name}` \(.*?\) ENGINE=.*?;",
        without_commented_create,
        flags=re.DOTALL,
    )
    if create is None:
        raise ValueError(f"Could not find CREATE SQL for {table_name}")

    script = f"DROP TABLE IF EXISTS {table_name};\n{create.group(0)}"
    script = re.sub(r"/\*!.*?\*/;?", "", script, flags=re.DOTALL)
    script = re.sub(r"\) ENGINE=.*?;", ");", script, flags=re.DOTALL)
    script = script.replace("`", "")
    for pattern, replacement in TYPE_REPLACEMENTS:
        script = pattern.sub(replacement, script)
    return script


def _mysql_insert_rows(mysql_sql: str, table_name: str) -> list[tuple]:
    insert = re.search(
        rf"INSERT INTO `{table_name}` VALUES (.*?);",
        mysql_sql,
        flags=re.DOTALL,
    )
    if insert is None:
        raise ValueError(f"Could not find INSERT SQL for {table_name}")
    return list(ast.literal_eval(f"[{insert.group(1)}]"))


def _columns(conn: sqlite3.Connection, table_name: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")]


def _write_csv(conn: sqlite3.Connection, table_name: str, path: Path) -> int:
    rows = conn.execute(f"SELECT * FROM {table_name} ORDER BY 1").fetchall()
    columns = _columns(conn, table_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)
    return len(rows)


def _mirror_method_name(code_of_account: str) -> str:
    if code_of_account in {"OCC", "TCC"}:
        return f"Account_{code_of_account}"
    if re.fullmatch(r"[0-9.]+", code_of_account):
        return "Account_C" + code_of_account.replace(".", "_")
    return ""


def _mirror_code(code_of_account: str) -> str:
    return code_of_account.replace(".", "") if re.fullmatch(r"[0-9.]+", code_of_account) else code_of_account


def _mirror_parent_code(code_of_account: str, level: int) -> str:
    if level <= 0:
        return ""
    if "." in code_of_account:
        return _mirror_code(code_of_account.rsplit(".", 1)[0])
    if re.fullmatch(r"\d+", code_of_account):
        return code_of_account[:-1]
    return ""


def _mirror_parent_code_for_table(code_of_account: str, level: int, codes: set[str]) -> str:
    parent = _mirror_parent_code(code_of_account, level)
    if parent == "2" and "20" in codes:
        return "20"
    return parent


def _dollar_value(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    return float(str(value).replace("$", ""))


def _account_method_dependencies(algorithm_source: Path) -> dict[str, tuple[list[str], list[str]]]:
    module = ast.parse(algorithm_source.read_text(encoding="utf-8"))
    klass = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "MirrorFunc")
    dependencies = {}
    for node in klass.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("Account_"):
            continue
        input_keys = set()
        account_calls = set()
        explicit_args = [
            arg.arg
            for arg in node.args.args
            if arg.arg not in {"self", "inputs"}
        ]
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Subscript)
                and isinstance(child.value, ast.Name)
                and child.value.id == "inputs"
                and isinstance(child.slice, ast.Constant)
                and isinstance(child.slice.value, str)
            ):
                input_keys.add(child.slice.value)
            if (
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and isinstance(child.func.value, ast.Name)
                and child.func.value.id == "MirrorFunc"
                and child.func.attr.startswith("Account_")
            ):
                account_calls.add(child.func.attr)
        dependencies[node.name] = (explicit_args or sorted(input_keys), sorted(account_calls))
    return dependencies


def _account_variables(input_keys: list[str], account_calls: list[str]) -> str:
    if account_calls:
        return "rollup"
    return ", ".join(HUMAN_INPUT_TO_VAR.get(key, key) for key in input_keys)


def _literal_default(node: ast.AST):
    value = ast.literal_eval(node)
    if isinstance(value, bool):
        return int(value)
    if value is None:
        return ""
    return value


def _generate_inputs_defaults(algorithm_source: Path) -> dict[str, tuple[object, str]]:
    module = ast.parse(algorithm_source.read_text(encoding="utf-8"))
    klass = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "MirrorFunc")
    method = next(node for node in klass.body if isinstance(node, ast.FunctionDef) and node.name == "generate_inputs")
    args = method.args.args
    defaults = method.args.defaults
    default_start = len(args) - len(defaults)
    values = {}
    for arg, default in zip(args[default_start:], defaults):
        if arg.arg in {"verbose", "exact", "save", "load"}:
            continue
        values[arg.arg] = (_literal_default(default), MIRROR_INPUT_UNITS.get(arg.arg, "1"))
    values["HF_magnet_number"] = (4, "1")
    values["LF_magnet_number"] = (2, "1")
    return values


def _mirror_generated_var_values(input_defaults: dict[str, tuple[object, str]]) -> dict[str, float]:
    values = {name: value for name, (value, _unit) in input_defaults.items()}
    values.update({name: value for name, (value, _unit) in MIRROR_CONSTANT_DEFAULTS.items()})
    values.update({name: value for name, (value, _unit) in MIRROR_REFERENCE_VAR_OVERRIDES.items()})
    generated = {}

    generated["P_f_CC"] = values["P_f"] - 2 * values["P_f_EP"]
    generated["L_CC"] = generated["P_f_CC"] / values["P_f_L"]
    generated["L_CF"] = 1.0
    generated["L"] = generated["L_CC"] + 2 * values["L_EP"] + 2 * values["L_EC"]
    generated["V_vac"] = generated["L"] * 3.141592653589793 * values["a_EC"] ** 2
    values["vpump_cap"] = MIRROR_VARIABLE_OVERRIDES["vpump_cap"][1]
    generated["no_vpumps"] = generated["V_vac"] / values["vpump_cap"]
    generated["cost_factor"] = 0.80 ** (math.log(values["n_unit"]) / math.log(2))
    generated["HF_magnet_cost"] = 29.1 * 0.70 ** (
        math.log((values["n_unit"] - 1) * values["HF_magnet_number"] + 1) / math.log(2)
    )
    generated["LF_magnet_cost"] = 6.25262 * 0.70 ** (
        math.log((values["n_unit"] - 1) * values["LF_magnet_number"] + 1) / math.log(2)
    )
    generated["CF_magnet_cost"] = 2.751 * 0.70 ** (
        math.log((values["n_unit"] - 1) * values["CF_magnet_number"] + 1) / math.log(2)
    )
    generated["P_alpha"] = values["P_f"] * values["E_alpha"] / values["E_DT"]
    generated["P_n"] = values["P_f"] - generated["P_alpha"]
    generated["P_ine"] = (
        values["P_NBI"] / values["eta_NBI"]
        + values["P_ICRH"] / values["eta_ICRH"]
        + values["P_ECH"] / values["eta_ECH"]
    )
    generated["P_pump"] = values["f_pump"] * values["M_n"] * generated["P_n"]
    generated["P_sub_cont"] = values["f_sub"] * values["P_f"]
    generated["P_cryo"] = values["f_cryo"] * values["P_f"]
    generated["P_other"] = generated["P_pump"] + generated["P_sub_cont"] + generated["P_cryo"]
    generated["P_in"] = values["P_NBI"] + values["P_ICRH"] + values["P_ECH"]
    generated["P_th"] = values["M_n"] * generated["P_n"] + values["eta_pump"] * generated["P_pump"]
    generated["P_the"] = values["eta_th"] * generated["P_th"]
    generated["P_DEC"] = generated["P_in"] + generated["P_alpha"]
    generated["P_DECe"] = values["eta_DEC"] * generated["P_DEC"]
    if str(values["application"]).lower() == "electricity":
        generated["P_egross"] = generated["P_DECe"] + generated["P_the"]
    else:
        generated["P_egross"] = generated["P_DECe"]
    generated["P_enet"] = generated["P_egross"] - (generated["P_ine"] + generated["P_other"])
    generated["f_aux"] = values["P_aux"] / generated["P_egross"]
    generated["Q_sci"] = values["P_f"] / generated["P_in"]
    generated["Q_eng"] = generated["P_egross"] / (generated["P_ine"] + generated["P_other"])
    generated["f_refrac"] = 1 / generated["Q_eng"]
    generated["CF_magnet_number"] = generated["L_CC"] / generated["L_CF"]
    generated.update({name: value for name, (value, _unit) in MIRROR_REFERENCE_VAR_OVERRIDES.items()})
    return generated


def _normalize_mirror_account_table(conn: sqlite3.Connection, algorithm_source: Path) -> None:
    dependencies = _account_method_dependencies(algorithm_source)
    methods = set(dependencies)
    conn.execute("ALTER TABLE mirror_acco RENAME TO mirror_acco_raw")
    conn.execute(
        "CREATE TABLE mirror_acco ("
        + ", ".join(f"{name} {kind}" for name, kind in MIRROR_ACCOUNT_COLUMNS)
        + ", PRIMARY KEY (code_of_account))"
    )
    rows = conn.execute(
        """
        SELECT ind, code_of_account, account_description, total_cost_dollars, level,
               prn, fun_unit
        FROM mirror_acco_raw
        ORDER BY ind
        """
    ).fetchall()
    codes = {
        _mirror_code(raw_code)
        for _ind, raw_code, _description, _total_cost, _level, _prn, _fun_unit in rows
    }
    rollup_codes = {
        _mirror_parent_code_for_table(raw_code, int(level or 0), codes)
        for _ind, raw_code, _description, _total_cost, level, _prn, _fun_unit in rows
        if _mirror_parent_code_for_table(raw_code, int(level or 0), codes)
    }
    for ind, raw_code, description, total_cost, level, prn, fun_unit in rows:
        code = _mirror_code(raw_code)
        alg_name = _mirror_method_name(raw_code)
        input_keys, account_calls = dependencies.get(alg_name, ([], []))
        is_rollup = code in rollup_codes
        variables = "rollup" if is_rollup else _account_variables(input_keys, account_calls)
        if is_rollup or account_calls or alg_name not in methods:
            alg_name = ""
        conn.execute(
            """
            INSERT INTO mirror_acco
            (ind, code_of_account, account_description, total_cost, level,
             supaccount, review_status, prn, alg_name, fun_unit, variables)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ind,
                code,
                description,
                _dollar_value(total_cost),
                level,
                _mirror_parent_code_for_table(raw_code, int(level or 0), codes),
                "Unchanged",
                prn,
                alg_name,
                fun_unit or "million",
                variables,
            ),
        )
    conn.execute("DROP TABLE mirror_acco_raw")


def _split_vars(value: str | None) -> list[str]:
    if value is None:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip() and part.strip() != "TODO"]


def _normalize_mirror_variable_table(conn: sqlite3.Connection, algorithm_source: Path) -> None:
    input_defaults = _generate_inputs_defaults(algorithm_source)
    generated_values = _mirror_generated_var_values(input_defaults)
    conn.execute("UPDATE mirror_var SET var_alg = '' WHERE var_alg = 'TODO'")
    conn.execute("UPDATE mirror_var SET var_need = '' WHERE var_need = 'TODO'")
    conn.execute("UPDATE mirror_var SET v_linked = '' WHERE v_linked = 'TODO'")
    conn.execute("UPDATE mirror_var SET var_unit = '1' WHERE var_unit = 'TODO'")
    conn.execute("UPDATE mirror_var SET var_unit = 'm' WHERE var_name = 'r_magnet'")
    for var_name, (value, unit) in input_defaults.items():
        if conn.execute("SELECT 1 FROM mirror_var WHERE var_name = ?", (var_name,)).fetchone():
            continue
        next_ind = conn.execute("SELECT COALESCE(MAX(ind), 0) + 1 FROM mirror_var").fetchone()[0]
        conn.execute(
            """
            INSERT INTO mirror_var
            (ind, var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked, user_input)
            VALUES (?, ?, ?, ?, ?, '', '', '', 0)
            """,
            (next_ind, var_name, "Mirror input parameter", value, unit),
        )
    for var_name, (value, unit) in MIRROR_REFERENCE_VAR_OVERRIDES.items():
        if not conn.execute("SELECT 1 FROM mirror_var WHERE var_name = ?", (var_name,)).fetchone():
            next_ind = conn.execute("SELECT COALESCE(MAX(ind), 0) + 1 FROM mirror_var").fetchone()[0]
            conn.execute(
                """
                INSERT INTO mirror_var
                (ind, var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked, user_input)
                VALUES (?, ?, ?, ?, ?, '', '', '', 0)
                """,
                (next_ind, var_name, "Mirror reference parameter", value, unit),
            )
            continue
        conn.execute(
            """
            UPDATE mirror_var
            SET var_value = ?, var_unit = ?, user_input = 0
            WHERE var_name = ?
            """,
            (value, unit, var_name),
        )
    for var_name, var_need in MIRROR_GENERATED_VAR_NEEDS.items():
        if not conn.execute("SELECT 1 FROM mirror_var WHERE var_name = ?", (var_name,)).fetchone():
            next_ind = conn.execute("SELECT COALESCE(MAX(ind), 0) + 1 FROM mirror_var").fetchone()[0]
            conn.execute(
                """
                INSERT INTO mirror_var
                (ind, var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked, user_input)
                VALUES (?, ?, ?, '', '1', '', ?, '', 0)
                """,
                (next_ind, var_name, "Mirror generated parameter", var_need),
            )
        conn.execute("UPDATE mirror_var SET var_need = ? WHERE var_name = ?", (var_need, var_name))
        _formulation, unit = MIRROR_GENERATED_VAR_FORMULAS.get(var_name, ("", "1"))
        conn.execute(
            """
            UPDATE mirror_var
            SET var_value = ?, var_alg = ?, var_unit = ?, user_input = 0
            WHERE var_name = ?
            """,
            (generated_values.get(var_name), f"cal_{var_name}", unit, var_name),
        )

    for var_name, (value, unit) in MIRROR_CONSTANT_DEFAULTS.items():
        if not conn.execute("SELECT 1 FROM mirror_var WHERE var_name = ?", (var_name,)).fetchone():
            next_ind = conn.execute("SELECT COALESCE(MAX(ind), 0) + 1 FROM mirror_var").fetchone()[0]
            conn.execute(
                """
                INSERT INTO mirror_var
                (ind, var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked, user_input)
                VALUES (?, ?, ?, ?, ?, '', '', '', 0)
                """,
                (next_ind, var_name, "Mirror physical constant", value, unit),
            )
        else:
            conn.execute(
                "UPDATE mirror_var SET var_value = ?, var_unit = ?, user_input = 0 WHERE var_name = ?",
                (value, unit, var_name),
            )

    for var_name, (description, value, unit) in MIRROR_VARIABLE_OVERRIDES.items():
        if not conn.execute("SELECT 1 FROM mirror_var WHERE var_name = ?", (var_name,)).fetchone():
            next_ind = conn.execute("SELECT COALESCE(MAX(ind), 0) + 1 FROM mirror_var").fetchone()[0]
            conn.execute(
                """
                INSERT INTO mirror_var
                (ind, var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked, user_input)
                VALUES (?, ?, ?, ?, ?, '', '', '', 0)
                """,
                (next_ind, var_name, description, value, unit),
            )
            continue
        if value is None:
            conn.execute(
                """
                UPDATE mirror_var
                SET var_description = ?, var_unit = ?, user_input = 0
                WHERE var_name = ?
                """,
                (description, unit, var_name),
            )
        else:
            conn.execute(
                """
                UPDATE mirror_var
                SET var_description = ?, var_value = ?, var_unit = ?, user_input = 0
                WHERE var_name = ?
                """,
                (description, value, unit, var_name),
            )

    valid_variable_algorithms = {f"cal_{var_name}" for var_name in MIRROR_GENERATED_VAR_FORMULAS}
    placeholders = ", ".join("?" for _ in valid_variable_algorithms)
    conn.execute(
        f"""
        UPDATE mirror_var
        SET var_alg = ''
        WHERE COALESCE(var_alg, '') != ''
          AND var_alg NOT IN ({placeholders})
        """,
        tuple(sorted(valid_variable_algorithms)),
    )

    reverse_links: dict[str, list[str]] = {}
    for var_name, var_need in conn.execute("SELECT var_name, var_need FROM mirror_var"):
        for needed in _split_vars(var_need):
            reverse_links.setdefault(needed, []).append(var_name)
    conn.execute("UPDATE mirror_var SET v_linked = ''")
    for var_name, links in reverse_links.items():
        conn.execute(
            "UPDATE mirror_var SET v_linked = ? WHERE var_name = ?",
            (", ".join(sorted(set(links))), var_name),
        )


def _write_default_inputs_csv(algorithm_source: Path, path: Path) -> int:
    rows = [
        (name, value, unit)
        for name, (value, unit) in sorted(_generate_inputs_defaults(algorithm_source).items())
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["var_name", "default_value", "var_unit"])
        writer.writerows(rows)
    return len(rows)


def _normalize_mirror_algorithm_table(conn: sqlite3.Connection, algorithm_source: Path) -> None:
    dependencies = _account_method_dependencies(algorithm_source)
    used_account_algorithms = {
        row[0]
        for row in conn.execute("SELECT DISTINCT alg_name FROM mirror_acco WHERE COALESCE(alg_name, '') != ''")
    }
    for (alg_name,) in conn.execute("SELECT alg_name FROM mirror_alg WHERE alg_for = 'c'").fetchall():
        if alg_name not in used_account_algorithms:
            conn.execute("DELETE FROM mirror_alg WHERE alg_name = ?", (alg_name,))
    for alg_name, (input_keys, account_calls) in dependencies.items():
        if alg_name not in used_account_algorithms:
            continue
        variables = _account_variables(input_keys, account_calls)
        conn.execute(
            "UPDATE mirror_alg SET alg_formulation = ?, alg_units = 'million' WHERE alg_name = ?",
            (variables or "reference value", alg_name),
        )
    next_ind = conn.execute("SELECT COALESCE(MAX(ind), 0) + 1 FROM mirror_alg").fetchone()[0]
    for var_name, (formulation, unit) in MIRROR_GENERATED_VAR_FORMULAS.items():
        alg_name = f"cal_{var_name}"
        existing = conn.execute("SELECT ind FROM mirror_alg WHERE alg_name = ?", (alg_name,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE mirror_alg
                SET alg_for = 'v',
                    alg_description = ?,
                    alg_python = 'MirrorFunc',
                    alg_formulation = ?,
                    alg_units = ?
                WHERE alg_name = ?
                """,
                (f"Mirror generated variable calculation for {var_name}", formulation, unit, alg_name),
            )
            continue
        conn.execute(
            """
            INSERT INTO mirror_alg
            (ind, alg_name, alg_for, alg_description, alg_python, alg_formulation, alg_units)
            VALUES (?, ?, 'v', ?, 'MirrorFunc', ?, ?)
            """,
            (
                next_ind,
                alg_name,
                f"Mirror generated variable calculation for {var_name}",
                formulation,
                unit,
            ),
        )
        next_ind += 1

    used_variable_algorithms = {
        row[0]
        for row in conn.execute("SELECT DISTINCT var_alg FROM mirror_var WHERE COALESCE(var_alg, '') != ''")
    }
    for (alg_name,) in conn.execute("SELECT alg_name FROM mirror_alg WHERE alg_for = 'v'").fetchall():
        if alg_name not in used_variable_algorithms:
            conn.execute("DELETE FROM mirror_alg WHERE alg_name = ?", (alg_name,))


def load_mirror_tables(
    db_path: Path,
    ref_dir: Path,
    sql_path: Path,
    algorithm_source: Path,
    algorithm_dest: Path,
    split_algorithm_source: Path,
    split_algorithm_dest: Path,
) -> None:
    mysql_sql = sql_path.read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    try:
        for table_name in TABLES:
            conn.executescript(_sqlite_table_script(mysql_sql, table_name))
            columns = _columns(conn, table_name)
            placeholders = ", ".join("?" for _ in columns)
            conn.executemany(
                f"INSERT INTO {table_name} VALUES ({placeholders})",
                _mysql_insert_rows(mysql_sql, table_name),
            )
        _normalize_mirror_account_table(conn, algorithm_source)
        _normalize_mirror_variable_table(conn, algorithm_source)
        _normalize_mirror_algorithm_table(conn, algorithm_source)
        conn.commit()
        for table_name, file_name in TABLES.items():
            count = _write_csv(conn, table_name, ref_dir / file_name)
            print(f"Wrote {count} {table_name} rows.")
        count = _write_default_inputs_csv(algorithm_source, ref_dir / DEFAULT_INPUT_FILE)
        print(f"Wrote {count} Mirror default input rows.")
    finally:
        conn.close()

    algorithm_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(algorithm_source, algorithm_dest)
    shutil.copy2(split_algorithm_source, split_algorithm_dest)
    print(f"Copied {algorithm_source} to {algorithm_dest}.")
    print(f"Copied {split_algorithm_source} to {split_algorithm_dest}.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--ref-dir", default=str(DEFAULT_REF_DIR))
    parser.add_argument("--sql", default=str(DEFAULT_SQL))
    parser.add_argument("--algorithm-source", default=str(DEFAULT_ALG_SRC))
    parser.add_argument("--algorithm-dest", default=str(DEFAULT_ALG_DST))
    parser.add_argument("--split-algorithm-source", default=str(DEFAULT_SPLIT_ALG_SRC))
    parser.add_argument("--split-algorithm-dest", default=str(DEFAULT_SPLIT_ALG_DST))
    args = parser.parse_args()
    load_mirror_tables(
        Path(args.db).resolve(),
        Path(args.ref_dir).resolve(),
        Path(args.sql).resolve(),
        Path(args.algorithm_source).resolve(),
        Path(args.algorithm_dest).resolve(),
        Path(args.split_algorithm_source).resolve(),
        Path(args.split_algorithm_dest).resolve(),
    )


if __name__ == "__main__":
    main()
