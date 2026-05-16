"""Verify the LPSR costs stored in ACCERT SQLite.

Run from the ACCERT repository root:

    PYTHONPATH=src python3 tutorial/accert/lpsr_verify_cost.py

The script sums the factory/labor/material cost elements by account and compares
those sums with the account totals stored in ``lpsr_account``.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "src" / "accertdb.sqlite"
TOLERANCE = 0.01


def load_cost_elements(conn: sqlite3.Connection) -> dict[str, list[tuple[str, float]]]:
    grouped: dict[str, list[tuple[str, float]]] = {}
    rows = conn.execute(
        """
        SELECT cost_element, cost_2017, account
        FROM lpsr_cost_element
        ORDER BY ind
        """
    ).fetchall()
    for cost_element, stored_cost, account in rows:
        grouped.setdefault(account, []).append((cost_element, float(stored_cost or 0.0)))
    return grouped


def verify_accounts(conn: sqlite3.Connection) -> int:
    grouped_elements = load_cost_elements(conn)
    failures = 0

    print("LPSR account verification")
    print("account | stored account total | summed cost elements | delta")
    print("-" * 72)

    account_rows = conn.execute(
        """
        SELECT code_of_account, account_description, total_cost
        FROM lpsr_account
        WHERE level >= 2
        ORDER BY ind
        """
    ).fetchall()

    for account, description, stored_total in account_rows:
        element_sum = sum(cost for _, cost in grouped_elements.get(account, []))
        delta = float(stored_total or 0.0) - element_sum
        if abs(delta) > TOLERANCE:
            failures += 1
        print(f"{account:>7} | {stored_total:20,.2f} | {element_sum:20,.2f} | {delta: .6f}")

        if account in {"212", "213"}:
            print(f"        {description}")
            for cost_element, stored_cost in grouped_elements[account]:
                print(f"        {cost_element:<12} stored={stored_cost:,.2f}")

    top_rows = conn.execute(
        """
        SELECT code_of_account, account_description, total_cost
        FROM lpsr_account
        WHERE code_of_account = '2'
        ORDER BY ind
        """
    ).fetchall()
    print("\nDirect cost total")
    for account, description, total_cost in top_rows:
        print(f"{account:>7} | {description:<24} | {total_cost:,.2f}")

    if failures:
        print(f"\nFAILED: {failures} account total(s) did not match within ${TOLERANCE}.")
        return 1

    print(f"\nPASSED: all level-2 and lower account totals match within ${TOLERANCE}.")
    return 0


def main() -> int:
    if not DB_PATH.exists():
        print(f"SQLite database not found: {DB_PATH}", file=sys.stderr)
        return 1

    with sqlite3.connect(DB_PATH) as conn:
        return verify_accounts(conn)


if __name__ == "__main__":
    raise SystemExit(main())
