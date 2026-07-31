import csv
from pathlib import Path
from types import SimpleNamespace

from Main import Accert


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REF_DIR = PROJECT_ROOT / "tutorial" / "accert" / "ref_tables"


def _csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def test_mirror_reference_tables_loaded(cursor):
    expected = {
        "mirror_acco": REF_DIR / "mirror_account.csv",
        "mirror_alg": REF_DIR / "mirror_algorithm.csv",
        "mirror_var": REF_DIR / "mirror_variable.csv",
    }
    for table_name, csv_path in expected.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        assert cursor.fetchone()[0] == _csv_row_count(csv_path)


def test_mirror_setup_table_names():
    accert = Accert.__new__(Accert)
    accert.use_gncoa = False
    accert.target_dollar_year = 2017
    input_obj = SimpleNamespace(
        ref_model=SimpleNamespace(value="mirror"),
        use_gncoa=None,
        target_dollar_year=None,
    )

    accert.setup_table_names(input_obj)

    assert accert.ref_model == "mirror"
    assert accert.acc_tabl == "mirror_acco"
    assert accert.cel_tabl is None
    assert accert.var_tabl == "mirror_var"
    assert accert.alg_tabl == "mirror_alg"


def test_mirror_variable_update_uses_reference_table(cursor):
    accert = Accert.__new__(Accert)
    accert.var_tabl = "mirror_var"

    assert accert.update_input_variable(cursor, "r_magnet", 2.0, "m") is None
    cursor.execute(
        """
        SELECT var_value, var_unit, user_input
        FROM mirror_var
        WHERE var_name = ?;
        """,
        ("r_magnet",),
    )
    assert cursor.fetchone() == (2.0, "m", 1)
