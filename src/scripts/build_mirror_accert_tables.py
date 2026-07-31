"""Load Mirror ACCERT reference tables from a PR #50 MySQL dump.

The closed upstream Mirror PR predated the SQLite database used by ACCERT.
This script converts the Mirror-specific MySQL tables into SQLite tables and
writes reference CSVs under tutorial/accert/ref_tables.
"""
from __future__ import annotations

import argparse
import ast
import csv
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

MIRROR_INPUT_DEFAULTS = {
    "application": ("heat", "1"),
    "P_f": (1, "MW"),
    "P_f_L": (1, "MW/m"),
    "P_f_EP": (1, "MW"),
    "P_NBI": (1, "MW"),
    "P_ECH": (1, "MW"),
    "P_ICRH": (1, "MW"),
    "M_n": (1.1, "1"),
    "N_module": (1, "1"),
    "f_pump": (0.03, "1"),
    "f_sub": (0.04, "1"),
    "f_cryo": (0.01, "1"),
    "P_aux": (1, "MW"),
    "eta_th": (0.50, "1"),
    "eta_DEC": (0.90, "1"),
    "eta_pump": (0.98, "1"),
    "eta_NBI": (0.50, "1"),
    "eta_ECH": (0.50, "1"),
    "eta_ICRH": (0.50, "1"),
    "NOAK": (0, "1"),
    "n_unit": (1, "1"),
    "construction_time": (6, "years"),
    "lifetime": (30, "years"),
    "replacement": (10, "years"),
    "availability": (0.90, "1"),
    "discount": (0.0245, "1"),
    "LSA": (2, "1"),
    "include_decommissioning": (0, "1"),
    "include_tax": (0, "1"),
    "include_licensing": (0, "1"),
    "include_contingency": (0, "1"),
    "hf_magnet_length": (1, "m"),
    "hf_magnet_shielding_thickness": (1, "m"),
    "a_EC": (1, "m"),
    "expander_cell_vessel_thickness": (0.01, "m"),
    "vacuum_gap_CC": (0.01, "m"),
    "first_wall_thickness": (0.01, "m"),
    "vacuum_vessel_thickness": (0.01, "m"),
    "multiplier_thickness": (0.01, "m"),
    "blanket_thickness": (1.00, "m"),
    "blanket_coolant_fraction": (0.90, "1"),
    "blanket_structural_fraction": (0.10, "1"),
    "outer_vessel_thickness": (0.01, "m"),
    "L_EP": (1, "m"),
    "L_EC": (1, "m"),
    "a_CC": (1, "m"),
    "a_EP": (1, "m"),
    "HF_magnet_number": (4, "1"),
    "LF_magnet_number": (2, "1"),
}

MIRROR_GENERATED_VAR_NEEDS = {
    "P_f_CC": "P_f, P_f_EP",
    "L_CC": "P_f_CC, P_f_L",
    "L_CF": "",
    "L": "L_CC, L_EP, L_EC",
    "V_vac": "L, a_EC",
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
        dependencies[node.name] = (sorted(input_keys), sorted(account_calls))
    return dependencies


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
    for ind, raw_code, description, total_cost, level, prn, fun_unit in rows:
        code = _mirror_code(raw_code)
        alg_name = _mirror_method_name(raw_code)
        input_keys, account_calls = dependencies.get(alg_name, ([], []))
        variables = "rollup" if account_calls else ", ".join(
            HUMAN_INPUT_TO_VAR[key] for key in input_keys if key in HUMAN_INPUT_TO_VAR
        )
        if alg_name not in methods:
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
                _mirror_parent_code(raw_code, int(level or 0)),
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


def _normalize_mirror_variable_table(conn: sqlite3.Connection) -> None:
    conn.execute("UPDATE mirror_var SET var_alg = '' WHERE var_alg = 'TODO'")
    conn.execute("UPDATE mirror_var SET var_need = '' WHERE var_need = 'TODO'")
    conn.execute("UPDATE mirror_var SET v_linked = '' WHERE v_linked = 'TODO'")
    conn.execute("UPDATE mirror_var SET var_unit = '1' WHERE var_unit = 'TODO'")
    conn.execute("UPDATE mirror_var SET var_unit = 'm' WHERE var_name = 'r_magnet'")
    for var_name, (value, unit) in MIRROR_INPUT_DEFAULTS.items():
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


def _normalize_mirror_algorithm_table(conn: sqlite3.Connection, algorithm_source: Path) -> None:
    dependencies = _account_method_dependencies(algorithm_source)
    for alg_name, (input_keys, account_calls) in dependencies.items():
        variables = "rollup" if account_calls else ", ".join(
            HUMAN_INPUT_TO_VAR[key] for key in input_keys if key in HUMAN_INPUT_TO_VAR
        )
        conn.execute(
            "UPDATE mirror_alg SET alg_formulation = ?, alg_units = 'million' WHERE alg_name = ?",
            (variables or "reference value", alg_name),
        )


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
        _normalize_mirror_variable_table(conn)
        _normalize_mirror_algorithm_table(conn, algorithm_source)
        conn.commit()
        for table_name, file_name in TABLES.items():
            count = _write_csv(conn, table_name, ref_dir / file_name)
            print(f"Wrote {count} {table_name} rows.")
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
