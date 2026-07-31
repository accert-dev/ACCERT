import csv
from pathlib import Path
from types import SimpleNamespace

import pytest

from Main import Accert
from Algorithm.MirrorFunc import MirrorFunc


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


def test_mirror_default_inputs_are_exported_from_generate_inputs():
    defaults_path = REF_DIR / "mirror_default_inputs.csv"
    with defaults_path.open(newline="", encoding="utf-8") as handle:
        defaults = {
            row["var_name"]: (row["default_value"], row["var_unit"])
            for row in csv.DictReader(handle)
        }

    assert defaults["application"] == ("heat", "1")
    assert defaults["P_f"] == ("1", "MW")
    assert defaults["n_unit"] == ("0", "1")
    assert defaults["HF_magnet_number"] == ("4", "1")
    assert defaults["LF_magnet_number"] == ("2", "1")


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


def test_mirror_unlinked_variable_does_not_change_accounts(cursor):
    accert = Accert.__new__(Accert)
    accert.acc_tabl = "mirror_acco"
    accert.var_tabl = "mirror_var"
    accert.alg_tabl = "mirror_alg"

    cursor.execute("SELECT total_cost FROM mirror_acco WHERE code_of_account = ?", ("OCC",))
    original_occ = cursor.fetchone()[0]

    assert accert.update_input_variable(cursor, "r_magnet", 2.0, "m") is None
    assert accert.update_new_accounts(cursor) is None
    assert not accert._has_account_changes_to_roll_up(cursor)

    cursor.execute(
        """
        SELECT total_cost, review_status
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("OCC",),
    )
    assert cursor.fetchone() == (original_occ, "Unchanged")


def test_mirror_accounts_use_fusion_style_structure(cursor):
    cursor.execute(
        """
        SELECT code_of_account, supaccount, alg_name, variables
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("211",),
    )
    assert cursor.fetchone() == ("211", "21", "Account_C21_1", "P_egross")

    cursor.execute(
        """
        SELECT total_cost
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("OCC",),
    )
    assert cursor.fetchone()[0] == 1587572359.0


def test_mirror_variable_links_are_reversed_from_var_need(cursor):
    cursor.execute(
        """
        SELECT var_need, v_linked
        FROM mirror_var
        WHERE var_name = ?;
        """,
        ("P_egross",),
    )
    assert cursor.fetchone() == (
        "application, P_DECe, P_the",
        "P_enet, Q_eng, f_aux",
    )


def test_mirror_reference_power_defaults_are_back_calculated(cursor):
    cursor.execute(
        """
        SELECT var_name, var_value, var_unit
        FROM mirror_var
        WHERE var_name IN (?, ?, ?, ?, ?)
        ORDER BY var_name;
        """,
        ("P_DEC", "P_DECe", "P_egross", "P_enet", "P_th"),
    )
    rows = {name: (value, unit) for name, value, unit in cursor.fetchall()}

    assert rows["P_DEC"][0] == pytest.approx(70.0198976448057)
    assert rows["P_DECe"][0] == pytest.approx(63.01790788032513)
    assert rows["P_egross"][0] == pytest.approx(158.12094932835822)
    assert rows["P_enet"][0] == pytest.approx(94.91500463226332)
    assert rows["P_th"][0] == pytest.approx(158.50506908190818)
    assert {unit for _value, unit in rows.values()} == {"MW"}


def test_mirror_generated_variable_algorithms_are_loaded(cursor):
    cursor.execute(
        """
        SELECT var_alg, var_need, var_unit
        FROM mirror_var
        WHERE var_name = ?;
        """,
        ("P_DECe",),
    )
    assert cursor.fetchone() == ("cal_P_DECe", "eta_DEC, P_DEC", "MW")

    cursor.execute(
        """
        SELECT alg_for, alg_python, alg_formulation, alg_units
        FROM mirror_alg
        WHERE alg_name = ?;
        """,
        ("cal_P_DECe",),
    )
    assert cursor.fetchone() == (
        "v",
        "MirrorFunc",
        "P_DECe = eta_DEC * P_DEC",
        "MW",
    )

    cursor.execute(
        """
        SELECT var_name, var_value, var_unit, v_linked
        FROM mirror_var
        WHERE var_name IN (?, ?)
        ORDER BY var_name;
        """,
        ("P_DEC", "eta_DEC"),
    )
    rows = cursor.fetchall()
    assert rows[0][0] == "P_DEC"
    assert rows[0][1] == pytest.approx(70.0198976448057)
    assert rows[0][2:] == ("MW", "P_DECe")
    assert rows[1] == ("eta_DEC", 0.9, "1", "P_DECe")


def test_mirror_account_algorithms_use_accert_variable_names():
    alg = MirrorFunc(
        ind=1,
        alg_name="Account_C21_1",
        alg_for="c",
        alg_description="",
        alg_formulation="",
        alg_units="million",
        variables="P_egross",
        constants="",
    )

    assert alg.run({"P_egross": 158.12094932835822}) == pytest.approx(42.37641442)


def test_mirror_vacuum_pump_account_uses_deeper_variables(cursor):
    cursor.execute(
        """
        SELECT variables
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("22163",),
    )
    assert cursor.fetchone()[0] == "cost_pump, no_vpumps"

    cursor.execute(
        """
        SELECT var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked
        FROM mirror_var
        WHERE var_name IN (?, ?, ?, ?)
        ORDER BY var_name;
        """,
        ("V_vac", "cost_pump", "no_vpumps", "vpump_cap"),
    )
    rows = {row[0]: row[1:] for row in cursor.fetchall()}

    assert rows["cost_pump"] == (
        "Cost of one vacuum pump, scaled from 1985 dollars",
        40000.0,
        "dollar/pump",
        "",
        "",
        "",
    )
    assert rows["vpump_cap"] == (
        "Vacuum volume pumped by one vacuum pump in one second",
        pytest.approx(200 / 48),
        "m3/pump",
        "",
        "",
        "no_vpumps",
    )
    assert rows["no_vpumps"] == (
        "Number of vacuum pumps required to pump the full vacuum in one second",
        pytest.approx(9.42477796076938 / (200 / 48)),
        "1",
        "cal_no_vpumps",
        "V_vac, vpump_cap",
        "",
    )
    assert rows["V_vac"][5] == "no_vpumps"

    cursor.execute(
        """
        SELECT alg_for, alg_python, alg_formulation, alg_units
        FROM mirror_alg
        WHERE alg_name = ?;
        """,
        ("cal_no_vpumps",),
    )
    assert cursor.fetchone() == (
        "v",
        "MirrorFunc",
        "no_vpumps = V_vac / vpump_cap",
        "1",
    )

    alg = MirrorFunc(
        ind=1,
        alg_name="Account_C22_1_6_3",
        alg_for="c",
        alg_description="",
        alg_formulation="",
        alg_units="million",
        variables="cost_pump,no_vpumps",
        constants="",
    )
    assert alg.run({"cost_pump": 40000, "no_vpumps": 2.2619467105846507}) == pytest.approx(
        0.09047786842338603
    )


def test_mirror_nbi_account_uses_cost_factor_variable(cursor):
    cursor.execute(
        """
        SELECT variables
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("22141",),
    )
    assert cursor.fetchone()[0] == "P_NBI, cost_factor"

    cursor.execute(
        """
        SELECT var_name, var_value, var_unit, var_alg, var_need, v_linked
        FROM mirror_var
        WHERE var_name IN (?, ?, ?)
        ORDER BY var_name;
        """,
        ("P_NBI", "cost_factor", "n_unit"),
    )
    rows = {row[0]: row[1:] for row in cursor.fetchall()}

    assert rows["P_NBI"] == (15.0, "MW", "", "", "P_in, P_ine")
    assert rows["cost_factor"] == (1.0, "1", "cal_cost_factor", "n_unit", "")
    assert rows["n_unit"] == (1.0, "1", "", "", "cost_factor")

    cursor.execute(
        """
        SELECT alg_for, alg_python, alg_formulation, alg_units
        FROM mirror_alg
        WHERE alg_name = ?;
        """,
        ("cal_cost_factor",),
    )
    assert cursor.fetchone() == (
        "v",
        "MirrorFunc",
        "cost_factor = 0.80 ** (log(n_unit) / log(2))",
        "1",
    )

    alg = MirrorFunc(
        ind=1,
        alg_name="Account_C22_1_4_1",
        alg_for="c",
        alg_description="",
        alg_formulation="",
        alg_units="million",
        variables="P_NBI,cost_factor",
        constants="",
    )
    assert alg.run({"P_NBI": 15.0, "cost_factor": 1.0}) == pytest.approx(105.963)


def test_mirror_generated_variable_algorithm_can_recalculate(cursor):
    accert = Accert.__new__(Accert)
    accert.var_tabl = "mirror_var"
    accert.alg_tabl = "mirror_alg"
    accert.cel_tabl = None

    cursor.execute(
        """
        UPDATE mirror_var
        SET var_value = ?
        WHERE var_name = ?;
        """,
        (10.0, "P_DEC"),
    )

    assert accert.update_super_variable(cursor, "P_DECe") is None
    cursor.execute(
        """
        SELECT var_value, var_unit, user_input
        FROM mirror_var
        WHERE var_name = ?;
        """,
        ("P_DECe",),
    )
    assert cursor.fetchone() == (9.0, "MW", 1)


def test_mirror_account_recalculation_uses_accert_variables(cursor):
    accert = Accert.__new__(Accert)
    accert.acc_tabl = "mirror_acco"
    accert.var_tabl = "mirror_var"
    accert.alg_tabl = "mirror_alg"

    cursor.execute(
        """
        UPDATE mirror_var
        SET var_value = ?, user_input = 1
        WHERE var_name = ?;
        """,
        (1000.0, "P_egross"),
    )

    assert accert.update_new_accounts(cursor) is None
    cursor.execute(
        """
        SELECT total_cost, review_status
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("211",),
    )
    assert cursor.fetchone() == (268000000.0, "User Input")
