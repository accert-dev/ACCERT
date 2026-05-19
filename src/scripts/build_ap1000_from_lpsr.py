"""Create AP1000 ACCERT reference tables from the LPSR table structure."""
from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "src" / "accertdb.sqlite"
DEFAULT_REF_DIR = ROOT / "tutorial" / "accert" / "ref_tables"

TARGET_DIRECT_COST = 6673722963.402768347
REFERENCE_ELECTRIC_POWER = 2234.0
REFERENCE_THERMAL_POWER = 6800.0
REFERENCE_REJECTED_POWER = REFERENCE_THERMAL_POWER - REFERENCE_ELECTRIC_POWER


TABLES = {
    "account": ("lpsr_account", "ap1000_account", "ap1000_direct_account.csv"),
    "cost_element": ("lpsr_cost_element", "ap1000_cost_element", "ap1000_direct_cost_elements.csv"),
    "variable": ("lpsr_variable", "ap1000_variable", "ap1000_direct_variables.csv"),
    "algorithm": ("lpsr_algorithm", "ap1000_algorithm", "ap1000_direct_algorithms.csv"),
}


def _columns(conn: sqlite3.Connection, table_name: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")]


def _scale_factor(conn: sqlite3.Connection) -> float:
    row = conn.execute(
        "SELECT total_cost FROM lpsr_account WHERE code_of_account = '2'"
    ).fetchone()
    if row is None or row[0] in (None, 0):
        raise ValueError("Could not find a nonzero LPSR account 2 total_cost")
    return TARGET_DIRECT_COST / float(row[0])


def _copy_schema(conn: sqlite3.Connection, source_table: str, target_table: str) -> None:
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (source_table,),
    ).fetchone()[0]
    conn.execute(f"DROP TABLE IF EXISTS {target_table}")
    conn.execute(sql.replace(source_table, target_table, 1))


def _clone_table(conn: sqlite3.Connection, source_table: str, target_table: str) -> None:
    columns = _columns(conn, source_table)
    column_list = ", ".join(columns)
    conn.execute(f"INSERT INTO {target_table} ({column_list}) SELECT {column_list} FROM {source_table}")


def _scale_ap1000_tables(conn: sqlite3.Connection, scale: float) -> None:
    conn.execute("UPDATE ap1000_account SET total_cost = total_cost * ? WHERE total_cost IS NOT NULL", (scale,))
    conn.execute("UPDATE ap1000_cost_element SET cost_2018 = cost_2018 * ? WHERE cost_2018 IS NOT NULL", (scale,))
    conn.execute("UPDATE ap1000_account SET review_status = 'Unchanged'")
    conn.execute("UPDATE ap1000_cost_element SET updated = 0")
    conn.execute("UPDATE ap1000_variable SET user_input = 0")
    conn.execute(
        "UPDATE ap1000_variable SET var_value = ? WHERE var_name = 'elec_P'",
        (REFERENCE_ELECTRIC_POWER,),
    )
    conn.execute(
        "UPDATE ap1000_variable SET var_value = ? WHERE var_name = 'rx_P'",
        (REFERENCE_THERMAL_POWER,),
    )
    conn.execute(
        "UPDATE ap1000_variable SET var_value = ? WHERE var_name = 'rej_th_P'",
        (REFERENCE_REJECTED_POWER,),
    )


def _write_csv(conn: sqlite3.Connection, table_name: str, path: Path) -> int:
    rows = conn.execute(f"SELECT * FROM {table_name} ORDER BY 1").fetchall()
    columns = _columns(conn, table_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)
    return len(rows)


def build_ap1000_tables(db_path: Path, ref_dir: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        scale = _scale_factor(conn)
        for _, (source_table, target_table, _) in TABLES.items():
            _copy_schema(conn, source_table, target_table)
            _clone_table(conn, source_table, target_table)
        _scale_ap1000_tables(conn, scale)
        conn.commit()

        for _, (_, target_table, file_name) in TABLES.items():
            count = _write_csv(conn, target_table, ref_dir / file_name)
            print(f"Wrote {count} {target_table} rows.")
        print(f"AP1000 account 2 direct cost target: {TARGET_DIRECT_COST:.12f}")
        print(f"LPSR-to-AP1000 scale factor: {scale:.12f}")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--ref-dir", default=str(DEFAULT_REF_DIR))
    args = parser.parse_args()
    build_ap1000_tables(Path(args.db).resolve(), Path(args.ref_dir).resolve())


if __name__ == "__main__":
    main()
