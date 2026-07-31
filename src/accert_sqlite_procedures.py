"""
SQLite procedure implementations for ACCERT.

Design
------
Each procedure is a Python function that accepts a sqlite3.Connection and
normal Python arguments. The functions return rows for SELECT-style procedures
and return None for UPDATE/INSERT/DELETE procedures.

The companion SQLiteCursorAdapter class lets existing ACCERT code keep the
same c.callproc(...); c.stored_results() pattern with minimal changes.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Sequence, Tuple

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def qident(name: str) -> str:
    """Safely quote a SQLite table/column identifier."""
    if not isinstance(name, str) or not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Unsafe SQL identifier: {name!r}")
    return f'"{name}"'


def _fetchall(conn: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> list[tuple]:
    return conn.execute(sql, tuple(params)).fetchall()


def _fetchone(conn: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> Optional[tuple]:
    return conn.execute(sql, tuple(params)).fetchone()


def _execute(conn: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
    return conn.execute(sql, tuple(params))


def _split_csv(value: Any) -> list[str]:
    if value is None:
        return []
    return [x.strip() for x in str(value).replace(" ", "").split(",") if x.strip()]


def _decode_text(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("\\n", "\n").replace("\\t", "\t")
    return value


def _with_decoded_text(rows: Iterable[tuple]) -> list[tuple]:
    return [tuple(_decode_text(value) for value in row) for row in rows]


def _contains_csv_var(variables: Any, var_name: str) -> bool:
    return str(var_name).strip() in _split_csv(variables)


def _table_columns(conn: sqlite3.Connection, table_name: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({qident(table_name)})").fetchall()]


def _has_column(conn: sqlite3.Connection, table_name: str, column: str) -> bool:
    return column in _table_columns(conn, table_name)


def _cost_column(conn: sqlite3.Connection, table_name: str) -> str:
    if _has_column(conn, table_name, "cost_2018"):
        return "cost_2018"
    return "cost_2017"


@dataclass
class StoredResult:
    rows: list[tuple]
    description: Optional[list[tuple]] = None

    def fetchall(self) -> list[tuple]:
        return self.rows

    def fetchone(self) -> Optional[tuple]:
        return self.rows[0] if self.rows else None


class SQLiteCursorAdapter:
    """Small adapter that provides the cursor API used by ACCERT.

    Use this when you want to keep existing ACCERT methods that do:
        c.callproc('procedure_name', args)
        for row in c.stored_results(): ...
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._stored_results: list[StoredResult] = []
        self._last_cursor: Optional[sqlite3.Cursor] = None

    def callproc(self, procname: str, args: Sequence[Any] = ()) -> None:
        result = callproc(self.conn, procname, args)
        rows, description = ([], None)
        if isinstance(result, sqlite3.Cursor):
            rows = result.fetchall()
            description = result.description
        elif result is None:
            rows = []
        else:
            rows = list(result)
            description = _description_for(procname, rows)
        self._stored_results = [StoredResult(rows=rows, description=description)]

    def stored_results(self) -> list[StoredResult]:
        return self._stored_results

    def execute(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        self._last_cursor = self.conn.execute(sql, tuple(params))
        return self._last_cursor

    def fetchall(self) -> list[tuple]:
        return [] if self._last_cursor is None else self._last_cursor.fetchall()

    def fetchone(self) -> Optional[tuple]:
        return None if self._last_cursor is None else self._last_cursor.fetchone()

    @property
    def description(self):
        return None if self._last_cursor is None else self._last_cursor.description


# ---------------------------------------------------------------------------
# Procedure implementations registered by name for ACCERT call sites.
# ---------------------------------------------------------------------------

def cal_direct_cost_elements(conn: sqlite3.Connection, acc_table: str, cel_table: str) -> list[tuple]:
    acc = qident(acc_table); cel = qident(cel_table)
    cost_col = qident(_cost_column(conn, cel_table))
    row = _fetchone(conn, f"""
        SELECT COALESCE(SUM(t1.prn), 0)
        FROM {acc} AS t1
        LEFT JOIN {acc} AS t2 ON t1.code_of_account = t2.supaccount
        WHERE t2.code_of_account IS NULL
          AND t1.code_of_account NOT IN ('2','2C')
    """)
    tprn = row[0] if row else 0
    if not tprn:
        return [(None, None, None)]
    vals = {}
    for kind in ("fac", "lab", "mat"):
        r = _fetchone(conn, f"SELECT {cost_col} / ? FROM {cel} WHERE account='2' AND lower(cost_element)=?", (tprn, f"2c_{kind}"))
        vals[kind] = r[0] if r else None
    return [(vals["fac"], vals["lab"], vals["mat"])]


def extract_affected_accounts(conn: sqlite3.Connection, acc_table: str, var_table: str) -> list[tuple]:
    rows = []
    for var_name, in _fetchall(conn, f"SELECT var_name FROM {qident(var_table)} WHERE user_input = 1"):
        affected = [r[0] for r in _fetchall(conn, f"SELECT code_of_account, variables FROM {qident(acc_table)}") if _contains_csv_var(r[1], var_name)]
        if affected:
            rows.append((var_name, ", ".join(affected)))
    return rows


def extract_affected_cost_elements(conn: sqlite3.Connection, cel_table: str, var_table: str) -> list[tuple]:
    rows = []
    ce_rows = _fetchall(conn, f"SELECT cost_element, variables FROM {qident(cel_table)}")
    for var_name, in _fetchall(conn, f"SELECT var_name FROM {qident(var_table)} WHERE user_input = 1"):
        affected = [ce for ce, variables in ce_rows if _contains_csv_var(variables, var_name)]
        if affected:
            rows.append((var_name, ", ".join(affected)))
    return rows


def extract_affected_cost_elements_w_dis(conn: sqlite3.Connection, cel_table: str, var_table: str) -> list[tuple]:
    rows = []
    ce_rows = _fetchall(conn, f"SELECT cost_element, variables FROM {qident(cel_table)}")
    for var_name, desc in _fetchall(conn, f"SELECT var_name, var_description FROM {qident(var_table)} WHERE user_input = 1"):
        affected = [ce for ce, variables in ce_rows if _contains_csv_var(variables, var_name)]
        if affected:
            rows.append((var_name, desc, ", ".join(affected)))
    return rows


def extract_changed_cost_elements(conn: sqlite3.Connection, cel_table: str) -> list[tuple]:
    cost_col = qident(_cost_column(conn, cel_table))
    return _fetchall(conn, f"SELECT cost_element, {cost_col} FROM {qident(cel_table)} WHERE updated != 0 ORDER BY account, cost_element")


def extract_super_val(conn: sqlite3.Connection, table_name: str, var_name: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT v_linked FROM {qident(table_name)} WHERE var_name = ?", (var_name,))


def extract_total_cost_on_name(conn: sqlite3.Connection, table_name: str, tc_name: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT code_of_account, account_description, total_cost FROM {qident(table_name)} WHERE code_of_account = ?", (tc_name,))


def extract_user_changed_variables(conn: sqlite3.Connection, table_name: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT var_name, var_description, var_value, var_unit FROM {qident(table_name)} WHERE user_input = 1 ORDER BY ind")


def extract_variable_info_on_name(conn: sqlite3.Connection, table_name: str, var_name: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT var_value, var_unit FROM {qident(table_name)} WHERE var_name = ?", (var_name,))


def get_current_COAs(conn: sqlite3.Connection, table_name: str, inp_id: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT code_of_account, ind FROM {qident(table_name)} WHERE supaccount = ?", (inp_id,))


def get_var_value_by_name(conn: sqlite3.Connection, table_name: str, var_name: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT var_value FROM {qident(table_name)} WHERE var_name = ?", (var_name,))


def insert_new_COA(conn: sqlite3.Connection, table_name: str, ind: int, supaccount: str, level: int, code_of_account: str, account_description: str, total_cost: float, review_status: str, prn: Any) -> None:
    _execute(conn, f"""
        INSERT INTO {qident(table_name)}
        (ind, supaccount, level, code_of_account, account_description, total_cost, review_status, prn)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ind, supaccount, level, code_of_account, account_description, total_cost, review_status, prn))


def insert_new_COA_gncoa(conn: sqlite3.Connection, table_name: str, ind: int, supaccount: str, level: int, code_of_account: str, account_description: str, total_cost: float, review_status: str, prn: Any, gncoa: str, gn_level: int, gn_supaccount: str, gn_ind: int) -> None:
    _execute(conn, f"""
        INSERT INTO {qident(table_name)}
        (ind, supaccount, level, code_of_account, account_description, total_cost, review_status, prn, gncoa, gn_level, gn_supaccount, gn_ind)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ind, supaccount, level, code_of_account, account_description, total_cost, review_status, prn, gncoa, gn_level, gn_supaccount, gn_ind))


def print_account_all(conn: sqlite3.Connection, table_name: str, level: int) -> list[tuple]:
    return _fetchall(conn, f"SELECT * FROM {qident(table_name)} WHERE level <= ?", (level,))


def print_account_simple(conn: sqlite3.Connection, table_name: str, level: int) -> list[tuple]:
    return _fetchall(conn, f"""
        SELECT ind, code_of_account, account_description, total_cost, level, review_status
        FROM {qident(table_name)} WHERE level <= ?
    """, (level,))


def print_leveled_accounts_all(conn: sqlite3.Connection, acc_table: str, cel_table: str, level: int) -> list[tuple]:
    cost_expr = "cost_elements" if _has_column(conn, acc_table, "cost_elements") else "NULL AS cost_elements"
    cost_col = qident(_cost_column(conn, cel_table))
    rows = _fetchall(conn, f"""
        SELECT level, code_of_account, account_description, total_cost, review_status, {cost_expr}
        FROM {qident(acc_table)}
        WHERE level <= ?
        ORDER BY ind
    """, (level,))
    out = []
    for acc_level, coa, desc, total, status, cost_elements in rows:
        names = _split_csv(cost_elements) or [f"{coa}_fac", f"{coa}_lab", f"{coa}_mat"]
        values = []
        for name in names[:3]:
            row = _fetchone(conn, f"SELECT {cost_col} FROM {qident(cel_table)} WHERE cost_element = ?", (name,))
            if row is None:
                row = _fetchone(conn, f"SELECT {cost_col} FROM {qident(cel_table)} WHERE cost_element = ?", (name.lower(),))
            values.append(row[0] if row else None)
        values.extend([None] * (3 - len(values)))
        out.append((acc_level, f"{' ' * int(acc_level)}{coa}", desc, values[0], values[1], values[2], total, status))
    return out


def print_leveled_accounts_gn(conn: sqlite3.Connection, acc_table: str, map_table: str, level: int) -> list[tuple]:
    acc = qident(acc_table); mp = qident(map_table)
    return _fetchall(conn, f"""
        SELECT printf('%*s%s', acc.gn_level, '', acc.gncoa) AS gncoa,
               map.gncoa_description,
               acc.total_cost,
               acc.gn_level,
               acc.review_status
        FROM {acc} AS acc
        JOIN {mp} AS map ON acc.gncoa = map.gncoa
        WHERE acc.gn_level <= ?
        ORDER BY acc.gn_ind
    """, (level,))


def print_leveled_accounts_gn_all(conn: sqlite3.Connection, acc_table: str, cel_table: str, level: int) -> list[tuple]:
    cost_expr = "cost_elements" if _has_column(conn, acc_table, "cost_elements") else "NULL AS cost_elements"
    cost_col = qident(_cost_column(conn, cel_table))
    rows = _fetchall(conn, f"""
        SELECT gn_level, gncoa, account_description, total_cost, review_status, {cost_expr}
        FROM {qident(acc_table)}
        WHERE gn_level <= ?
        ORDER BY gn_ind
    """, (level,))
    out = []
    for gn_level, gncoa, desc, total, status, cost_elements in rows:
        names = _split_csv(cost_elements) or [f"{gncoa}_fac", f"{gncoa}_lab", f"{gncoa}_mat"]
        values = []
        for name in names[:3]:
            row = _fetchone(conn, f"SELECT {cost_col} FROM {qident(cel_table)} WHERE cost_element = ?", (name,))
            if row is None:
                row = _fetchone(conn, f"SELECT {cost_col} FROM {qident(cel_table)} WHERE cost_element = ?", (name.lower(),))
            values.append(row[0] if row else None)
        values.extend([None] * (3 - len(values)))
        out.append((gn_level, f"{' ' * int(gn_level)}{gncoa}", desc, values[0], values[1], values[2], total, status))
    return out


def print_leveled_accounts_simple(conn: sqlite3.Connection, acc_table: str, level: int) -> list[tuple]:
    return _fetchall(conn, f"""
        SELECT printf('%*s%s', level, '', code_of_account) AS code_of_account,
               account_description,
               total_cost,
               level,
               review_status
        FROM {qident(acc_table)}
        WHERE level <= ?
        ORDER BY ind
    """, (level,))


def print_table(conn: sqlite3.Connection, table_name: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT * FROM {qident(table_name)}")


def print_updated_cost_elements(conn: sqlite3.Connection, cel_table: str) -> list[tuple]:
    cost_name = _cost_column(conn, cel_table)
    cost_col = qident(cost_name)
    return conn.execute(f"""
        SELECT ind, cost_element, ROUND({cost_col}, 5) AS {qident(cost_name)}, sup_cost_ele, account, updated
        FROM {qident(cel_table)} WHERE updated = 1
    """)


def print_user_request_parameter(conn: sqlite3.Connection, all_col: bool, var_table: str, cel_table: str) -> list[tuple]:
    ce_rows = _fetchall(conn, f"SELECT cost_element, variables FROM {qident(cel_table)}")
    rows = []
    cols = "ind, var_name" if all_col else "var_name"
    for r in _fetchall(conn, f"SELECT {cols} FROM {qident(var_table)} WHERE var_value IS NULL ORDER BY ind"):
        if all_col:
            ind, var_name = r
        else:
            (var_name,) = r
        affected = [ce for ce, variables in ce_rows if _contains_csv_var(variables, var_name)]
        rows.append((ind, var_name, ", ".join(affected)) if all_col else (var_name, ", ".join(affected)))
    return rows


def remove_specific_row(conn: sqlite3.Connection, table_name: str, target_code: str) -> None:
    _execute(conn, f"DELETE FROM {qident(table_name)} WHERE code_of_account = ?", (target_code,))


def roll_up_account_table_by_gn_level(conn: sqlite3.Connection, table_name: str, from_level: int, to_level: int) -> None:
    table = qident(table_name)
    rows = _fetchall(conn, f"""
        SELECT parent.gncoa, COALESCE(SUM(child.total_cost), 0)
        FROM {table} AS child
        JOIN {table} AS parent ON child.gn_supaccount = parent.gncoa
        WHERE child.gn_level = ? AND parent.gn_level = ?
        GROUP BY parent.gncoa
    """, (from_level, to_level))
    for gncoa, total in rows:
        _execute(conn, f"UPDATE {table} SET total_cost = ?, review_status = 'Updated' WHERE gncoa = ?", (total, gncoa))


def roll_up_account_table_by_level(conn: sqlite3.Connection, table_name: str, from_level: int, to_level: int) -> None:
    table = qident(table_name)
    rows = _fetchall(conn, f"""
        SELECT parent.code_of_account, COALESCE(SUM(child.total_cost), 0)
        FROM {table} AS child
        JOIN {table} AS parent ON child.supaccount = parent.code_of_account
        WHERE child.level = ? AND parent.level = ?
        GROUP BY parent.code_of_account
    """, (from_level, to_level))
    for coa, total in rows:
        _execute(conn, f"UPDATE {table} SET total_cost = ?, review_status = 'Updated' WHERE code_of_account = ?", (total, coa))


def roll_up_cost_elements_by_level(conn: sqlite3.Connection, table_name: str, from_level: int, to_level: int) -> None:
    table = qident(table_name)
    cost_col = qident(_cost_column(conn, table_name))
    # The original procedure joins the global account table. For model-specific
    # tables, infer parent cost elements directly from sup_cost_ele.
    rows = _fetchall(conn, f"""
        SELECT parent.cost_element, COALESCE(SUM(child.{cost_col}), 0)
        FROM {table} AS child
        JOIN {table} AS parent ON child.sup_cost_ele = parent.cost_element
        GROUP BY parent.cost_element
    """)
    for ce, total in rows:
        _execute(conn, f"UPDATE {table} SET {cost_col} = ? WHERE cost_element = ?", (total, ce))


def roll_up_lmt_account_2C(conn: sqlite3.Connection, acc_tabl_name: str) -> None:
    table = qident(acc_tabl_name)
    row = _fetchone(conn, f"""
        SELECT COALESCE(SUM(t1.total_cost), 0), COALESCE(SUM(t1.prn), 0)
        FROM {table} AS t1
        LEFT JOIN {table} AS t2 ON t1.code_of_account = t2.supaccount
        WHERE t2.code_of_account IS NULL AND t1.code_of_account NOT IN ('2','2C')
    """)
    tc, tprn = row if row else (0, 0)
    _execute(conn, f"UPDATE {table} SET total_cost = ?, prn = ?, review_status = 'Ready for Review' WHERE code_of_account = '2C'", (tc, tprn))


def roll_up_lmt_direct_cost(conn: sqlite3.Connection, acc_tabl_name: str) -> None:
    table = qident(acc_tabl_name)
    row = _fetchone(conn, f"SELECT total_cost, prn FROM {table} WHERE code_of_account = '2C'")
    val = None if not row or not row[1] else row[0] / row[1]
    _execute(conn, f"UPDATE {table} SET total_cost = ?, review_status = 'Ready for Review' WHERE code_of_account = '2'", (val,))


def _sum_cost_elements_2c(conn: sqlite3.Connection, cel_tabl_name: str, acc_tabl_name: str, suffix: str) -> list[tuple]:
    acc = qident(acc_tabl_name); cel = qident(cel_tabl_name)
    cost_col = qident(_cost_column(conn, cel_tabl_name))
    return _fetchall(conn, f"""
        SELECT SUM(ce.{cost_col})
        FROM (
            SELECT t1.code_of_account, t1.code_of_account || ? AS ce_name
            FROM {acc} AS t1
            LEFT JOIN {acc} AS t2 ON t1.code_of_account = t2.supaccount
            WHERE t2.code_of_account IS NULL AND t1.code_of_account NOT IN ('2','2C')
        ) AS leaf
        JOIN {cel} AS ce ON ce.cost_element = leaf.ce_name
        WHERE leaf.code_of_account != '2C'
    """, (suffix,))


def sum_cost_elements_2C_fac(conn: sqlite3.Connection, cel_tabl_name: str, acc_tabl_name: str) -> list[tuple]:
    return _sum_cost_elements_2c(conn, cel_tabl_name, acc_tabl_name, "_fac")


def sum_cost_elements_2C_lab(conn: sqlite3.Connection, cel_tabl_name: str, acc_tabl_name: str) -> list[tuple]:
    return _sum_cost_elements_2c(conn, cel_tabl_name, acc_tabl_name, "_lab")


def sum_cost_elements_2C_mat(conn: sqlite3.Connection, cel_tabl_name: str, acc_tabl_name: str) -> list[tuple]:
    return _sum_cost_elements_2c(conn, cel_tabl_name, acc_tabl_name, "_mat")


def sum_up_lmt_account_2C(conn: sqlite3.Connection, acc_tabl_name: str) -> None:
    return roll_up_lmt_account_2C(conn, acc_tabl_name)


def sum_up_lmt_direct_cost(conn: sqlite3.Connection, acc_tabl_name: str) -> None:
    return roll_up_lmt_direct_cost(conn, acc_tabl_name)


def sup_coa_level(conn: sqlite3.Connection, table_name: str, supaccount: str) -> list[tuple]:
    return _fetchall(conn, f"SELECT level FROM {qident(table_name)} WHERE code_of_account = ?", (supaccount,))


def update_account_before_insert(conn: sqlite3.Connection, table_name: str, min_ind: int) -> None:
    _execute(conn, f"UPDATE {qident(table_name)} SET ind = ind + 1 WHERE ind > ?", (min_ind,))


def update_account_table_by_cost_elements(conn: sqlite3.Connection, acc_tabl_name: str, cel_tabl_name: str) -> None:
    acc = qident(acc_tabl_name); cel = qident(cel_tabl_name)
    cost_col = qident(_cost_column(conn, cel_tabl_name))
    rows = _fetchall(conn, f"SELECT account, SUM({cost_col}), SUM(updated) FROM {cel} GROUP BY account")
    for account, total_cost, updated in rows:
        if updated and updated > 0:
            _execute(conn, f"UPDATE {acc} SET total_cost = ?, review_status = 'Ready for Review' WHERE code_of_account = ?", (total_cost, account))


def update_cost_element_on_name(conn: sqlite3.Connection, table_name: str, ce_name: str, alg_value: float) -> None:
    cost_col = qident(_cost_column(conn, table_name))
    _execute(conn, f"UPDATE {qident(table_name)} SET {cost_col} = ?, updated = 1 WHERE cost_element = ?", (alg_value, ce_name))


def update_new_accounts(conn: sqlite3.Connection, acc_tabl_name: str, var_tabl_name: str, alg_tabl_name: str) -> list[tuple]:
    acc_rows = _fetchall(conn, f"""
        SELECT ac.ind, ac.code_of_account, ac.total_cost, ac.alg_name, ac.variables,
               alg.alg_python, alg.alg_formulation, alg.alg_units
        FROM {qident(acc_tabl_name)} AS ac
        JOIN {qident(alg_tabl_name)} AS alg ON ac.alg_name = alg.alg_name
    """)
    user_vars = [r[0] for r in _fetchall(conn, f"SELECT var_name FROM {qident(var_tabl_name)} WHERE user_input = 1")]
    return _with_decoded_text(r for r in acc_rows if any(_contains_csv_var(r[4], v) for v in user_vars))


def update_new_cost_elements(conn: sqlite3.Connection, cel_tabl_name: str, var_tabl_name: str, alg_tabl_name: str) -> list[tuple]:
    cost_col = qident(_cost_column(conn, cel_tabl_name))
    ce_rows = _fetchall(conn, f"""
        SELECT ce.ind, ce.cost_element, ce.{cost_col}, ce.alg_name, ce.variables, ce.algno,
               alg.alg_python, alg.alg_formulation, alg.alg_units
        FROM {qident(cel_tabl_name)} AS ce
        JOIN {qident(alg_tabl_name)} AS alg ON ce.alg_name = alg.alg_name
    """)
    user_vars = [r[0] for r in _fetchall(conn, f"SELECT var_name FROM {qident(var_tabl_name)} WHERE user_input = 1")]
    return _with_decoded_text(r for r in ce_rows if any(_contains_csv_var(r[4], v) for v in user_vars))


def update_super_variable(conn: sqlite3.Connection, var_table_name: str, alg_table_name: str, u_i_var_name: str) -> list[tuple]:
    return _with_decoded_text(_fetchall(conn, f"""
        SELECT var.ind, var.var_name, var.var_value, var.var_alg, var.var_need,
               alg.ind, alg.alg_python, alg.alg_formulation, alg.alg_units, var.var_unit
        FROM {qident(var_table_name)} AS var
        JOIN {qident(alg_table_name)} AS alg ON var.var_alg = alg.alg_name
        WHERE var.var_name = ?
    """, (u_i_var_name,)))


def update_total_cost_on_name(conn: sqlite3.Connection, table_name: str, tc_id: str, u_i_tc_value: float) -> None:
    _execute(conn, f"UPDATE {qident(table_name)} SET total_cost = ?, review_status = 'User Input' WHERE code_of_account = ?", (u_i_tc_value, tc_id))


def update_variable_info_on_name(conn: sqlite3.Connection, table_name: str, u_i_var_name: str, value: float, unit: str) -> None:
    _execute(conn, f"UPDATE {qident(table_name)} SET var_value = ?, var_unit = ?, user_input = 1 WHERE var_name = ?", (value, unit, u_i_var_name))


PROC_COLUMNS = {
    "cal_direct_cost_elements": ["fac", "lab", "mat"],
    "extract_affected_accounts": ["var_name", "ac_affected"],
    "extract_affected_cost_elements": ["var_name", "ce_affected"],
    "extract_affected_cost_elements_w_dis": ["var_name", "var_description", "ce_affected"],
    "extract_changed_cost_elements": ["cost_element", "cost_2017"],
    "extract_super_val": ["v_linked"],
    "extract_total_cost_on_name": ["code_of_account", "account_description", "total_cost"],
    "extract_user_changed_variables": ["var_name", "var_description", "var_value", "var_unit"],
    "extract_variable_info_on_name": ["var_value", "var_unit"],
    "get_current_COAs": ["code_of_account", "ind"],
    "get_var_value_by_name": ["var_value"],
    "print_account_simple": ["ind", "code_of_account", "account_description", "total_cost", "level", "review_status"],
    "print_leveled_accounts_all": ["level", "code_of_account", "account_description", "fac_cost", "lab_cost", "mat_cost", "total_cost", "review_status"],
    "print_leveled_accounts_gn": ["gncoa", "gncoa_description", "total_cost", "gn_level", "review_status"],
    "print_leveled_accounts_gn_all": ["gn_level", "gncoa", "account_description", "fac_cost", "lab_cost", "mat_cost", "total_cost", "review_status"],
    "print_leveled_accounts_simple": ["code_of_account", "account_description", "total_cost", "level", "review_status"],
    "print_updated_cost_elements": ["ind", "cost_element", "cost_2017", "sup_cost_ele", "account", "updated"],
    "print_user_request_parameter": None,
    "sum_cost_elements_2C_fac": ["sum"],
    "sum_cost_elements_2C_lab": ["sum"],
    "sum_cost_elements_2C_mat": ["sum"],
    "sup_coa_level": ["level"],
    "update_new_accounts": ["ind", "code_of_account", "total_cost", "alg_name", "variables", "alg_python", "alg_formulation", "alg_units"],
    "update_new_cost_elements": ["ind", "cost_element", "cost_2017", "alg_name", "variables", "algno", "alg_python", "alg_formulation", "alg_units"],
    "update_super_variable": ["var_ind", "var_name", "var_value", "var_alg", "var_need", "alg_ind", "alg_python", "alg_formulation", "alg_units", "var_unit"],
}

def _description_for(procname: str, rows: list[tuple]) -> list[tuple]:
    cols = PROC_COLUMNS.get(procname)
    if cols is None:
        if procname == "print_user_request_parameter":
            cols = ["ind", "var_name", "ce_affected"] if rows and len(rows[0]) == 3 else ["var_name", "ce_affected"]
        else:
            width = len(rows[0]) if rows else 0
            cols = [f"col_{i+1}" for i in range(width)]
    return [(c, None, None, None, None, None, None) for c in cols]


PROCEDURES = {
    "cal_direct_cost_elements": cal_direct_cost_elements,
    "extract_affected_accounts": extract_affected_accounts,
    "extract_affected_cost_elements": extract_affected_cost_elements,
    "extract_affected_cost_elements_w_dis": extract_affected_cost_elements_w_dis,
    "extract_changed_cost_elements": extract_changed_cost_elements,
    "extract_super_val": extract_super_val,
    "extract_total_cost_on_name": extract_total_cost_on_name,
    "extract_user_changed_variables": extract_user_changed_variables,
    "extract_variable_info_on_name": extract_variable_info_on_name,
    "get_current_COAs": get_current_COAs,
    "get_var_value_by_name": get_var_value_by_name,
    "insert_new_COA": insert_new_COA,
    "insert_new_COA_gncoa": insert_new_COA_gncoa,
    "print_account_all": print_account_all,
    "print_account_simple": print_account_simple,
    "print_leveled_accounts_all": print_leveled_accounts_all,
    "print_leveled_accounts_gn": print_leveled_accounts_gn,
    "print_leveled_accounts_gn_all": print_leveled_accounts_gn_all,
    "print_leveled_accounts_simple": print_leveled_accounts_simple,
    "print_table": print_table,
    "print_updated_cost_elements": print_updated_cost_elements,
    "print_user_request_parameter": print_user_request_parameter,
    "remove_specific_row": remove_specific_row,
    "roll_up_account_table_by_gn_level": roll_up_account_table_by_gn_level,
    "roll_up_account_table_by_level": roll_up_account_table_by_level,
    "roll_up_cost_elements_by_level": roll_up_cost_elements_by_level,
    "roll_up_lmt_account_2C": roll_up_lmt_account_2C,
    "roll_up_lmt_direct_cost": roll_up_lmt_direct_cost,
    "sum_cost_elements_2C_fac": sum_cost_elements_2C_fac,
    "sum_cost_elements_2C_lab": sum_cost_elements_2C_lab,
    "sum_cost_elements_2C_mat": sum_cost_elements_2C_mat,
    "sum_up_lmt_account_2C": sum_up_lmt_account_2C,
    "sum_up_lmt_direct_cost": sum_up_lmt_direct_cost,
    "sup_coa_level": sup_coa_level,
    "update_account_before_insert": update_account_before_insert,
    "update_account_table_by_cost_elements": update_account_table_by_cost_elements,
    "update_cost_element_on_name": update_cost_element_on_name,
    "update_new_accounts": update_new_accounts,
    "update_new_cost_elements": update_new_cost_elements,
    "update_super_variable": update_super_variable,
    "update_total_cost_on_name": update_total_cost_on_name,
    "update_variable_info_on_name": update_variable_info_on_name,
}


def callproc(conn: sqlite3.Connection, procname: str, args: Sequence[Any] = ()) -> Any:
    try:
        func = PROCEDURES[procname]
    except KeyError as exc:
        raise KeyError(f"No SQLite procedure registered for {procname!r}") from exc
    return func(conn, *tuple(args))
