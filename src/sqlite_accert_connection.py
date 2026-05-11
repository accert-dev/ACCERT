"""SQLite compatibility layer for ACCERT.

Drop this file into ACCERT/src.  It provides two entry points:

1. connect_sqlite(db_path) -> (sqlite3 connection, ACCERT cursor adapter)
2. connect(...) -> MySQL-connector-compatible connection object

The second form is intentionally compatible with calls such as:

    mysql.connector.connect(host="localhost", user="root", password=..., database="accert_db")

used in the original ACCERT Main.py.  Instead of opening a MySQL server, it
opens ACCERT/src/accertdb.sqlite and returns a connection object whose cursor
supports the subset of MySQLCursor used by ACCERT, including:

    c.callproc(...)
    c.stored_results()
    c.execute(...)
    c.fetchall()
    c.fetchone()

Stored procedure names are implemented in accert_sqlite_procedures.py.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

from accert_sqlite_procedures import SQLiteCursorAdapter


def get_default_db_path(code_folder: str | os.PathLike[str] | None = None) -> str:
    """Return the default SQLite database path.

    If code_folder is omitted, this assumes this file lives in ACCERT/src and
    uses ACCERT/src/accertdb.sqlite.
    """
    if code_folder is None:
        code_folder = Path(__file__).resolve().parent
    return str(Path(code_folder) / "accertdb.sqlite")


class SQLiteConnectionAdapter:
    """Small wrapper that mimics the subset of mysql.connector connection used by ACCERT."""

    def __init__(self, db_path: str | os.PathLike[str] | None = None):
        self.db_path = str(db_path or get_default_db_path())
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA foreign_keys = ON")

    @property
    def raw_connection(self) -> sqlite3.Connection:
        return self._conn

    def cursor(self, *args: Any, **kwargs: Any) -> SQLiteCursorAdapter:
        return SQLiteCursorAdapter(self._conn)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()

    def is_connected(self) -> bool:
        try:
            self._conn.execute("SELECT 1")
        except sqlite3.Error:
            return False
        return True

    def execute(self, *args: Any, **kwargs: Any):
        # Convenience passthrough; most ACCERT code uses conn.cursor().execute().
        return self._conn.execute(*args, **kwargs)


class _MySQLConnectorShim:
    """Object used as mysql.connector in the Main.py wrapper."""

    @staticmethod
    def connect(*args: Any, **kwargs: Any) -> SQLiteConnectionAdapter:
        return connect(*args, **kwargs)


def connect_sqlite(db_path: str | os.PathLike[str] | None = None) -> tuple[SQLiteConnectionAdapter, SQLiteCursorAdapter]:
    """Open SQLite and return (connection_adapter, cursor_adapter)."""
    conn = SQLiteConnectionAdapter(db_path)
    return conn, conn.cursor()


def connect(*args: Any, **kwargs: Any) -> SQLiteConnectionAdapter:
    """MySQL-compatible connect function.

    Accepts mysql.connector.connect-style arguments and ignores MySQL-only
    fields such as host/user/password/auth_plugin.  The SQLite DB path is
    selected in this order:

    1. explicit db_path=... or sqlite_path=...
    2. environment variable ACCERT_SQLITE_DB
    3. ACCERT/src/accertdb.sqlite
    """
    db_path: Optional[str] = kwargs.pop("db_path", None) or kwargs.pop("sqlite_path", None)
    db_path = db_path or os.environ.get("ACCERT_SQLITE_DB")
    return SQLiteConnectionAdapter(db_path)


# Expose a connector-like object for direct monkeypatching.
connector = _MySQLConnectorShim()
