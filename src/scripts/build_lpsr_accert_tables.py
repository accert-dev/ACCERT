"""Load LPSR ACCERT reference tables from tutorial/accert/ref_tables."""
from __future__ import annotations

import argparse
import csv
import shutil
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "src" / "accertdb.sqlite"
DEFAULT_REF_DIR = ROOT / "tutorial" / "accert" / "ref_tables"
DEFAULT_ALG_SRC = DEFAULT_REF_DIR / "LPSRDirectCostFunc.py"
DEFAULT_ALG_DST = ROOT / "src" / "Algorithm" / "LPSRDirectCostFunc.py"


TABLE_SPECS = {
    "lpsr_account": {
        "file": "lpsr_direct_account.csv",
        "columns": [
            ("ind", "INTEGER"),
            ("code_of_account", "TEXT NOT NULL"),
            ("account_description", "TEXT"),
            ("total_cost", "REAL"),
            ("level", "INTEGER"),
            ("supaccount", "TEXT"),
            ("review_status", "TEXT"),
            ("prn", "REAL"),
            ("gncoa", "TEXT"),
            ("gn_level", "INTEGER"),
            ("gn_supaccount", "TEXT"),
            ("gn_ind", "INTEGER"),
        ],
        "primary_key": "code_of_account",
    },
    "lpsr_cost_element": {
        "file": "lpsr_direct_cost_elements.csv",
        "columns": [
            ("ind", "INTEGER NOT NULL"),
            ("cost_element", "TEXT"),
            ("cost_2017", "REAL"),
            ("sup_cost_ele", "TEXT"),
            ("alg_name", "TEXT"),
            ("fun_unit", "TEXT"),
            ("variables", "TEXT"),
            ("account", "TEXT"),
            ("algno", "TEXT"),
            ("updated", "INTEGER"),
            ("source_row_type", "TEXT"),
        ],
        "primary_key": "ind",
    },
    "lpsr_variable": {
        "file": "lpsr_direct_variables.csv",
        "columns": [
            ("ind", "INTEGER NOT NULL"),
            ("var_name", "TEXT"),
            ("var_description", "TEXT"),
            ("var_value", "REAL"),
            ("var_unit", "TEXT"),
            ("var_alg", "TEXT"),
            ("var_need", "TEXT"),
            ("v_linked", "TEXT"),
            ("user_input", "INTEGER"),
        ],
        "primary_key": "ind",
    },
}

ALGORITHM_FILE = "lpsr_direct_algorithms.csv"
ALGORITHM_TABLE = "lpsr_algorithm"
ALGORITHM_COLUMNS = [
    ("ind", "INTEGER"),
    ("alg_name", "TEXT"),
    ("alg_for", "TEXT"),
    ("alg_description", "TEXT"),
    ("alg_python", "TEXT"),
    ("alg_formulation", "TEXT"),
    ("alg_units", "TEXT"),
    ("variables", "TEXT"),
    ("constants", "TEXT"),
]

INTEGER_COLUMNS = {"ind", "level", "gn_level", "gn_ind", "updated", "user_input"}
REAL_COLUMNS = {"total_cost", "prn", "cost_2017", "var_value"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _coerce(column: str, value: str):
    if value is None or value == "":
        return None
    if column in INTEGER_COLUMNS:
        return int(float(value))
    if column in REAL_COLUMNS:
        return float(value)
    return value


def _normalize_row(table_name: str, row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    if table_name == "lpsr_variable":
        # In ACCERT, user_input is a run-time dirty flag. The reference database
        # should always start clean; SON inputs set this flag during a run.
        normalized["user_input"] = "0"
    return normalized


def _create_table_sql(table_name: str, columns: list[tuple[str, str]], primary_key: str) -> str:
    column_defs = [f"{name} {kind}" for name, kind in columns]
    column_defs.append(f"PRIMARY KEY ({primary_key})")
    return f"CREATE TABLE {table_name} ({', '.join(column_defs)})"


def _replace_table(
    conn: sqlite3.Connection,
    table_name: str,
    csv_path: Path,
    columns: list[tuple[str, str]],
    primary_key: str,
) -> int:
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.execute(_create_table_sql(table_name, columns, primary_key))

    rows = [_normalize_row(table_name, row) for row in _read_csv(csv_path)]
    column_names = [name for name, _ in columns]
    placeholders = ", ".join("?" for _ in column_names)
    conn.executemany(
        f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})",
        [
            tuple(_coerce(column, row.get(column, "")) for column in column_names)
            for row in rows
        ],
    )
    return len(rows)


def _replace_algorithms(conn: sqlite3.Connection, ref_dir: Path) -> int:
    rows = _read_csv(ref_dir / ALGORITHM_FILE)
    conn.execute("DELETE FROM algorithm WHERE alg_python IN ('LPSRFunc', 'LPSRDirectCostFunc')")
    conn.execute(f"DROP TABLE IF EXISTS {ALGORITHM_TABLE}")
    conn.execute(
        f"""
        CREATE TABLE {ALGORITHM_TABLE} (
          ind INTEGER,
          alg_name TEXT,
          alg_for TEXT,
          alg_description TEXT,
          alg_python TEXT,
          alg_formulation TEXT,
          alg_units TEXT,
          variables TEXT,
          constants TEXT,
          PRIMARY KEY (ind)
        )
        """
    )
    conn.executemany(
        f"""
        INSERT INTO {ALGORITHM_TABLE}
        (ind, alg_name, alg_for, alg_description, alg_python, alg_formulation, alg_units, variables, constants)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            tuple(_coerce(column, row.get(column, "")) for column, _ in ALGORITHM_COLUMNS)
            for row in rows
        ],
    )
    return len(rows)


def load_lpsr_tables(db_path: Path, ref_dir: Path, algorithm_source: Path, algorithm_dest: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        counts = {}
        for table_name, spec in TABLE_SPECS.items():
            counts[table_name] = _replace_table(
                conn,
                table_name,
                ref_dir / spec["file"],
                spec["columns"],
                spec["primary_key"],
            )
        counts[ALGORITHM_TABLE] = _replace_algorithms(conn, ref_dir)
        conn.commit()
    finally:
        conn.close()

    algorithm_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(algorithm_source, algorithm_dest)
    for table_name, count in counts.items():
        print(f"Wrote {count} {table_name} rows.")
    print(f"Copied {algorithm_source} to {algorithm_dest}.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--ref-dir", default=str(DEFAULT_REF_DIR))
    parser.add_argument("--algorithm-source", default=str(DEFAULT_ALG_SRC))
    parser.add_argument("--algorithm-dest", default=str(DEFAULT_ALG_DST))
    args = parser.parse_args()

    load_lpsr_tables(
        Path(args.db).resolve(),
        Path(args.ref_dir).resolve(),
        Path(args.algorithm_source).resolve(),
        Path(args.algorithm_dest).resolve(),
    )


if __name__ == "__main__":
    main()
