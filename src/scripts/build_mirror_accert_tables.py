"""Load Mirror ACCERT reference tables from a PR #50 MySQL dump.

The closed upstream Mirror PR predated the SQLite database used by ACCERT.
This script converts the Mirror-specific MySQL tables into SQLite tables and
writes reference CSVs under tutorial/accert/ref_tables.
"""
from __future__ import annotations

import argparse
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
    insert = re.search(
        rf"INSERT INTO `{table_name}` VALUES .*?;",
        without_commented_create,
        flags=re.DOTALL,
    )
    if create is None or insert is None:
        raise ValueError(f"Could not find CREATE/INSERT SQL for {table_name}")

    script = f"DROP TABLE IF EXISTS {table_name};\n{create.group(0)}\n{insert.group(0)}"
    script = re.sub(r"/\*!.*?\*/;?", "", script, flags=re.DOTALL)
    script = re.sub(r"\) ENGINE=.*?;", ");", script, flags=re.DOTALL)
    script = script.replace("`", "")
    for pattern, replacement in TYPE_REPLACEMENTS:
        script = pattern.sub(replacement, script)
    return script


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
        conn.execute("ALTER TABLE mirror_acco ADD COLUMN review_status TEXT")
        conn.execute("UPDATE mirror_acco SET review_status = 'Unchanged'")
        conn.execute(
            "UPDATE mirror_var SET var_unit = ? WHERE var_name = ?",
            ("m", "r_magnet"),
        )
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
