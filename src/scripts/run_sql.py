"""Execute a SQL script against the ACCERT SQLite database."""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path


def execute_sql_file(db_file: str | os.PathLike[str], sql_file_path: str | os.PathLike[str]) -> None:
    sql_path = Path(sql_file_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    conn = sqlite3.connect(db_file)
    try:
        conn.executescript(sql_path.read_text(encoding="utf-8"))
        conn.commit()
        print(f"Executed {sql_path} against {db_file}")
    finally:
        conn.close()


def main() -> None:
    code_src_folder = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("sql_file", nargs="?", default="user_defined.sql")
    parser.add_argument("--db", default=os.environ.get("ACCERT_SQLITE_DB", str(code_src_folder / "accertdb.sqlite")))
    args = parser.parse_args()
    execute_sql_file(args.db, Path.cwd() / args.sql_file)


if __name__ == "__main__":
    main()
