"""SQLite connection layer for ACCERT.

This module provides two entry points:

1. connect_sqlite(db_path) -> (SQLite connection adapter, ACCERT cursor adapter)
2. connect(...) -> SQLite connection adapter

The second form accepts legacy keyword arguments so older ACCERT call sites can
open the bundled SQLite database without carrying server configuration around.
The returned cursor supports the procedure-style API used by ACCERT:

    c.callproc(...)
    c.stored_results()
    c.execute(...)
    c.fetchall()
    c.fetchone()

Procedure names are implemented in accert_sqlite_procedures.py.
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
    """Small wrapper around sqlite3 with the connection methods ACCERT uses."""

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


class _ConnectorShim:
    """Connector-like object for tests and legacy monkeypatching."""

    @staticmethod
    def connect(*args: Any, **kwargs: Any) -> SQLiteConnectionAdapter:
        return connect(*args, **kwargs)


def connect_sqlite(db_path: str | os.PathLike[str] | None = None) -> tuple[SQLiteConnectionAdapter, SQLiteCursorAdapter]:
    """Open SQLite and return (connection_adapter, cursor_adapter)."""
    conn = SQLiteConnectionAdapter(db_path)
    return conn, conn.cursor()


def connect(*args: Any, **kwargs: Any) -> SQLiteConnectionAdapter:
    """Open the ACCERT SQLite database.

    Accepts legacy connection keyword arguments and ignores fields that are not
    needed by SQLite. The database path is selected in this order:

    1. explicit db_path=... or sqlite_path=...
    2. environment variable ACCERT_SQLITE_DB
    3. ACCERT/src/accertdb.sqlite
    """
    db_path: Optional[str] = kwargs.pop("db_path", None) or kwargs.pop("sqlite_path", None)
    db_path = db_path or os.environ.get("ACCERT_SQLITE_DB")
    return SQLiteConnectionAdapter(db_path)


# Expose a connector-like object for direct monkeypatching.
connector = _ConnectorShim()
