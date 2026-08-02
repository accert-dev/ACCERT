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


def test_mirror_default_inputs_are_exported_from_builder_defaults():
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


def test_mirror_func_does_not_keep_legacy_generate_inputs():
    assert not hasattr(MirrorFunc, "generate_inputs")


def test_mirror_variables_do_not_keep_blank_legacy_temporaries(cursor):
    cursor.execute("SELECT var_name FROM mirror_var WHERE COALESCE(var_value, '') = '' ORDER BY var_name")
    assert cursor.fetchall() == []

    temporary_locals = {
        "C_end_cap",
        "M_end_cap",
        "T_K",
        "V_cc_cylinder",
        "V_cc_triangle",
        "V_end_cap",
        "V_ep_cylinder",
        "V_ep_triangle",
        "V_radially_inner_cylinder",
        "V_total",
        "V_total_cc_facing",
        "V_total_ec_facing",
        "f_interp",
        "r_in",
        "r_in_cc",
        "r_in_ep",
        "r_out",
        "r_out_cc",
        "r_out_ep",
        "radial_build",
        "total",
    }
    placeholders = ", ".join("?" for _ in temporary_locals)
    cursor.execute(
        f"SELECT var_name FROM mirror_var WHERE var_name IN ({placeholders}) ORDER BY var_name",
        tuple(sorted(temporary_locals)),
    )
    assert cursor.fetchall() == []


def test_mirror_func_does_not_keep_legacy_dataframe_helpers():
    removed_helpers = {
        "PbLi_density",
        "Li_price",
        "PbLi_price",
        "V_cylindrical_shell",
        "V_inverse_triangular_washer",
        "create_radial_build",
        "add_new_layer",
        "add_fractional_layer",
        "build_central_cell",
        "central_cell_cost",
        "central_cell",
        "expander_cell_cost",
        "HF_magnet_shield_cost",
    }
    assert all(not hasattr(MirrorFunc, helper) for helper in removed_helpers)


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


def test_mirror_parent_accounts_are_rollups_without_algorithms(cursor):
    cursor.execute(
        """
        SELECT code_of_account, alg_name, variables
        FROM mirror_acco
        WHERE code_of_account IN (?, ?, ?, ?, ?)
        ORDER BY code_of_account;
        """,
        ("20", "21", "22", "221", "2213"),
    )
    assert cursor.fetchall() == [
        ("20", "", "rollup"),
        ("21", "", "rollup"),
        ("22", "", "rollup"),
        ("221", "", "rollup"),
        ("2213", "", "rollup"),
    ]

    cursor.execute(
        """
        SELECT code_of_account, supaccount
        FROM mirror_acco
        WHERE code_of_account IN (?, ?, ?)
        ORDER BY code_of_account;
        """,
        ("21", "22", "29"),
    )
    assert cursor.fetchall() == [("21", "20"), ("22", "20"), ("29", "20")]


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


def test_mirror_algorithm_table_only_keeps_referenced_variable_algorithms(cursor):
    cursor.execute("SELECT COUNT(*) FROM mirror_alg WHERE alg_name = '__init__';")
    assert cursor.fetchone()[0] == 0

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM mirror_alg
        WHERE alg_for = 'v'
          AND alg_name NOT IN (
              SELECT var_alg
              FROM mirror_var
              WHERE COALESCE(var_alg, '') != ''
          );
        """
    )
    assert cursor.fetchone()[0] == 0

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM mirror_var
        WHERE COALESCE(var_alg, '') != ''
          AND var_alg NOT IN (SELECT alg_name FROM mirror_alg);
        """
    )
    assert cursor.fetchone()[0] == 0


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

    alg = MirrorFunc(
        ind=1,
        alg_name="Account_C21_3",
        alg_for="c",
        alg_description="",
        alg_formulation="",
        alg_units="million",
        variables="application,P_egross",
        constants="",
    )
    assert alg.run({"application": "electricity", "P_egross": 158.12094932835822}) == pytest.approx(
        8.538531263731343
    )


def test_mirror_vacuum_pump_account_uses_deeper_variables(cursor):
    cursor.execute(
        """
        SELECT variables
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("22163",),
    )
    assert cursor.fetchone()[0] == "no_vpumps, cost_pump"

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
        variables="no_vpumps,cost_pump",
        constants="",
    )
    assert alg.run({"no_vpumps": 2.2619467105846507, "cost_pump": 40000}) == pytest.approx(
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
    assert rows["n_unit"] == (
        1.0,
        "1",
        "",
        "",
        "CF_magnet_cost, HF_magnet_cost, LF_magnet_cost, cost_factor",
    )

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


def test_mirror_magnet_accounts_use_explicit_cost_variables(cursor):
    cursor.execute(
        """
        SELECT code_of_account, variables
        FROM mirror_acco
        WHERE code_of_account IN (?, ?, ?)
        ORDER BY code_of_account;
        """,
        ("22131", "22132", "22133"),
    )
    assert cursor.fetchall() == [
        ("22131", "HF_magnet_number, HF_magnet_cost"),
        ("22132", "LF_magnet_number, LF_magnet_cost"),
        ("22133", "CF_magnet_number, CF_magnet_cost"),
    ]

    cursor.execute(
        """
        SELECT var_name, var_description, var_value, var_unit, var_alg, var_need, v_linked
        FROM mirror_var
        WHERE var_name IN (?, ?, ?, ?, ?, ?, ?)
        ORDER BY var_name;
        """,
        (
            "CF_magnet_cost",
            "CF_magnet_number",
            "HF_magnet_cost",
            "HF_magnet_number",
            "LF_magnet_cost",
            "LF_magnet_number",
            "n_unit",
        ),
    )
    rows = {row[0]: row[1:] for row in cursor.fetchall()}

    assert rows["HF_magnet_cost"] == (
        "HF cost per magnet, not for all four",
        29.1,
        "million",
        "cal_HF_magnet_cost",
        "n_unit, HF_magnet_number",
        "",
    )
    assert rows["LF_magnet_cost"] == (
        "LF cost per magnet",
        6.25262,
        "million",
        "cal_LF_magnet_cost",
        "n_unit, LF_magnet_number",
        "",
    )
    assert rows["CF_magnet_cost"] == (
        "CF cost per magnet",
        2.751,
        "million",
        "cal_CF_magnet_cost",
        "n_unit, CF_magnet_number",
        "",
    )
    assert rows["HF_magnet_number"][5] == "HF_magnet_cost"
    assert rows["LF_magnet_number"][5] == "LF_magnet_cost"
    assert rows["CF_magnet_number"][5] == "CF_magnet_cost"
    assert rows["n_unit"][5] == "CF_magnet_cost, HF_magnet_cost, LF_magnet_cost, cost_factor"

    alg = MirrorFunc(
        ind=1,
        alg_name="Account_C22_1_3_1",
        alg_for="c",
        alg_description="",
        alg_formulation="",
        alg_units="million",
        variables="HF_magnet_number,HF_magnet_cost",
        constants="",
    )
    assert alg.run({"HF_magnet_number": 4.0, "HF_magnet_cost": 29.1}) == pytest.approx(116.4)


def test_mirror_first_wall_and_blanket_use_legacy_scalar_super_variables(cursor):
    cursor.execute(
        """
        SELECT total_cost, alg_name, variables
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("2211",),
    )
    total_cost, alg_name, variables = cursor.fetchone()
    assert total_cost / 1e6 == pytest.approx(0.5110835873559177)
    assert alg_name == "Account_C22_1_1"
    assert variables == (
        "central_cell_cylindrical_part_cost, end_plug_cylindrical_part_cost, expander_cell_cost_result"
    )

    cursor.execute(
        """
        SELECT var_name, var_value, var_unit, var_alg, var_need
        FROM mirror_var
        WHERE var_name IN (?, ?, ?, ?, ?, ?)
        ORDER BY var_name;
        """,
        (
            "central_cell_cylindrical_part_cost",
            "end_plug_cylindrical_part_cost",
            "expander_cell_cost_result",
            "P_Li",
            "P_PbLi",
            "rho_PbLi",
        ),
    )
    rows = {row[0]: row[1:] for row in cursor.fetchall()}
    assert rows["central_cell_cylindrical_part_cost"][0] == pytest.approx(-0.5031620991790029)
    assert rows["central_cell_cylindrical_part_cost"][1:] == (
        "million",
        "cal_central_cell_cylindrical_part_cost",
        "L_CC, a_CC, vacuum_gap_CC, first_wall_thickness, vacuum_vessel_thickness, multiplier_thickness, blanket_thickness, blanket_coolant_fraction, blanket_structural_fraction, outer_vessel_thickness, W_rho, W_c_raw, W_m, SS316_rho, SS316_c_raw, SS316_m, Pb_rho, Pb_c_raw, Pb_m, rho_PbLi, P_PbLi",
    )
    assert rows["end_plug_cylindrical_part_cost"][0] == pytest.approx(0.5031620991790029)
    assert rows["end_plug_cylindrical_part_cost"][1:] == (
        "million",
        "cal_end_plug_cylindrical_part_cost",
        "L_EP, a_CC, vacuum_gap_CC, first_wall_thickness, vacuum_vessel_thickness, multiplier_thickness, blanket_thickness, blanket_coolant_fraction, blanket_structural_fraction, outer_vessel_thickness, W_rho, W_c_raw, W_m, SS316_rho, SS316_c_raw, SS316_m, Pb_rho, Pb_c_raw, Pb_m, rho_PbLi, P_PbLi",
    )
    assert rows["expander_cell_cost_result"][0] == pytest.approx(0.003960744088457411)
    assert rows["expander_cell_cost_result"][1:] == (
        "million",
        "cal_expander_cell_cost_result",
        "L_EC, a_EC, expander_cell_vessel_thickness, SS316_rho, SS316_c_raw, SS316_m",
    )
    assert rows["P_Li"][0] == pytest.approx(15.152)
    assert rows["P_Li"][1:] == ("dollar/kg", "cal_P_Li", "f_6Li")
    assert rows["P_PbLi"][0] == pytest.approx(4.56784)
    assert rows["P_PbLi"][1:] == ("dollar/kg", "cal_P_PbLi", "Pb_c_raw, P_Li")
    assert rows["rho_PbLi"][0] == pytest.approx(9838.0091935)
    assert rows["rho_PbLi"][1:] == ("kg/m3", "cal_rho_PbLi", "T, f_6Li")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM mirror_var
        WHERE var_name IN (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            "blanket1_vol",
            "blanket_cost",
            "central_cell_cylindrical_part",
            "end_plug_cylindrical_part",
            "first_wall_cost",
            "firstwall_vol",
            "L_cylinder",
            "L_magnet_to_magnet",
            "total_cost",
        ),
    )
    assert cursor.fetchone()[0] == 0

    alg = MirrorFunc(
        ind=1,
        alg_name="Account_C22_1_1",
        alg_for="c",
        alg_description="",
        alg_formulation="",
        alg_units="million",
        variables="central_cell_cylindrical_part_cost,end_plug_cylindrical_part_cost,expander_cell_cost_result",
        constants="",
    )
    assert alg.run(
        {
            "central_cell_cylindrical_part_cost": -0.5031620991790029,
            "end_plug_cylindrical_part_cost": 0.5031620991790029,
            "expander_cell_cost_result": 0.003960744088457411,
        }
    ) == pytest.approx(0.5110835873559177)


def test_mirror_magnet_shield_and_expander_costs_are_super_variables(cursor):
    cursor.execute(
        """
        SELECT total_cost, variables
        FROM mirror_acco
        WHERE code_of_account = ?;
        """,
        ("2212",),
    )
    total_cost, variables = cursor.fetchone()
    assert total_cost / 1e6 == pytest.approx(70.016988373184)
    assert variables == "HF_magnet_shield_cost"

    cursor.execute(
        """
        SELECT var_name, var_description, var_value, var_unit, var_alg, var_need
        FROM mirror_var
        WHERE var_name IN (?, ?)
        ORDER BY var_name;
        """,
        ("HF_magnet_shield_cost", "expander_cell_cost_result"),
    )
    rows = {row[0]: row[1:] for row in cursor.fetchall()}
    assert rows["HF_magnet_shield_cost"][0] == "HF magnet shield cost per end plug"
    assert rows["HF_magnet_shield_cost"][1] == pytest.approx(35.008494186592)
    assert rows["HF_magnet_shield_cost"][2:] == (
        "million",
        "cal_HF_magnet_shield_cost",
        "a_M, a_CC, a_0, length, r_gap, r_vv, r_magnet, r_cryostat, f_vol, length_cc_cylinder, length_ep_cylinder, W_rho, W_c_raw, W_m",
    )
    assert rows["expander_cell_cost_result"][0] == "Expander cell vacuum vessel cost from legacy Mirror geometry"
    assert rows["expander_cell_cost_result"][1] == pytest.approx(0.003960744088457411)
    assert rows["expander_cell_cost_result"][2:] == (
        "million",
        "cal_expander_cell_cost_result",
        "L_EC, a_EC, expander_cell_vessel_thickness, SS316_rho, SS316_c_raw, SS316_m",
    )

    alg = MirrorFunc(
        ind=1,
        alg_name="Account_C22_1_2",
        alg_for="c",
        alg_description="",
        alg_formulation="",
        alg_units="million",
        variables="HF_magnet_shield_cost",
        constants="",
    )
    assert alg.run({"HF_magnet_shield_cost": 35.008494186592}) == pytest.approx(70.016988373184)

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
        (2.0, "a_EC"),
    )
    assert accert.update_super_variable(cursor, "expander_cell_cost_result") is None
    cursor.execute("SELECT var_value FROM mirror_var WHERE var_name = ?;", ("expander_cell_cost_result",))
    assert cursor.fetchone()[0] == pytest.approx(0.011862477930766351)


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
