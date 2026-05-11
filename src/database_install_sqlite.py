"""Install or refresh the ACCERT SQLite database.

Usage:
    python src/database_install_sqlite.py
    python src/database_install_sqlite.py --db src/accertdb.sqlite --sql src/accertdb_sqlite_schema_data.sql
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def install_sqlite_database(sql_file: str | Path, db_file: str | Path, overwrite: bool = True) -> Path:
    sql_path = Path(sql_file)
    db_path = Path(db_file)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQLite SQL file not found: {sql_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists() and overwrite:
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql_path.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    return db_path


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql", default=str(here / "accertdb_sqlite_schema_data.sql"))
    parser.add_argument("--db", default=str(here / "accertdb.sqlite"))
    parser.add_argument("--keep-existing", action="store_true")
    args = parser.parse_args()
    db = install_sqlite_database(args.sql, args.db, overwrite=not args.keep_existing)
    print(f"Installed SQLite database at {db}")


if __name__ == "__main__":
    main()
