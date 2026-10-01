"""Behavioral sensitivity checks for the CRT model against the supplied paper."""

import math

import pytest

from crt import run_one_scenario


def _config(reactor_type="AP1000"):
    durations = {"AP1000": 76, "SFR": 80, "HTGR": 125}
    startups = {"AP1000": 28, "SFR": 16, "HTGR": 16}
    return {
        "reactor_type": reactor_type,
        "f_22": 250_000_000,
        "f_2321": 150_000_000,
        "land_cost_per_acre_0": 22_000,
        "construction_duration_0": durations[reactor_type],
        "startup_0": startups[reactor_type],
        "staggering_ratio": 0.75,
    }


def _levers(**overrides):
    values = {
        "num_orders": 10,
        "num_NOAK": 8,
        "itc_percent": 0,
        "n_itc": 0,
        "interest_percent": 6,
        "design_completion_percent": 70,
        "design_maturity": 1,
        "proc_exp": 1,
        "N_proc": 9,
        "ce_exp": 1,
        "N_cons": 9,
        "ae_exp": 1,
        "N_AE": 9,
        "standardization_percent": 80,
        "modularity_code": 1,
        "bop_grade_code": 1,
        "rb_grade_code": 1,
    }
    values.update(overrides)
    return values


def _run(reactor_type="AP1000", *, config_overrides=None, **overrides):
    config = _config(reactor_type)
    config.update(config_overrides or {})
    return run_one_scenario(config, _levers(**overrides))


def _finite(result, *keys):
    return all(math.isfinite(float(result[key])) for key in keys)


@pytest.mark.parametrize("reactor_type", ["AP1000", "SFR", "HTGR"])
def test_representative_reactor_baselines_produce_finite_crt_results(reactor_type):
    result = _run(reactor_type)

    assert _finite(result, "OCC_1", "TCI_1", "duration_1", "avg_OCC", "avg_TCI")


@pytest.mark.parametrize(
    ("lever", "low", "high", "metric"),
    [
        ("design_completion_percent", 0, 100, "duration_1"),
        ("design_maturity", 0, 2, "duration_1"),
        ("proc_exp", 0, 2, "duration_1"),
        ("ce_exp", 0, 2, "OCC_1"),
        ("ae_exp", 0, 2, "OCC_1"),
        ("standardization_percent", 0, 100, "OCC_8"),
        ("N_proc", 1, 9, "duration_2"),
        ("N_cons", 1, 9, "OCC_2"),
        ("N_AE", 1, 9, "OCC_2"),
        ("num_orders", 2, 10, "avg_OCC"),
        ("num_NOAK", 2, 8, "occ_reduction_from_FOAK_to_NOAK_percent"),
    ],
)
def test_documented_crt_levers_change_the_expected_output(lever, low, high, metric):
    extra = {"num_NOAK": 2} if lever == "num_orders" else {}
    low_result = _run(**{**extra, lever: low})
    high_result = _run(**{**extra, lever: high})

    assert float(low_result[metric]) != pytest.approx(float(high_result[metric])), (
        f"{lever} did not change {metric}: "
        f"{low_result[metric]} vs {high_result[metric]}"
    )


@pytest.mark.parametrize(
    ("lever", "off", "on", "metric"),
    [
        ("modularity_code", 0, 1, "duration_1"),
        ("bop_grade_code", 0, 1, "OCC_1"),
        ("rb_grade_code", 0, 1, "OCC_1"),
    ],
)
def test_ap1000_characteristic_levers_have_directional_effects(lever, off, on, metric):
    off_result = _run(**{lever: off})
    on_result = _run(**{lever: on})

    assert float(on_result[metric]) < float(off_result[metric])


def test_itc_changes_net_metrics_without_changing_gross_metrics():
    gross = _run(itc_percent=0, n_itc=0)
    net = _run(itc_percent=30, n_itc=1)

    assert net["OCC_1"] == pytest.approx(gross["OCC_1"])
    assert net["TCI_1"] == pytest.approx(gross["TCI_1"])
    assert net["NETOCC_1"] < net["OCC_1"]
    assert net["NCI_1"] < net["TCI_1"]


def test_itc_unit_count_changes_deployment_average_only_for_credited_units():
    no_credit = _run(itc_percent=30, n_itc=0)
    one_credit = _run(itc_percent=30, n_itc=1)

    assert one_credit["OCC_1"] == pytest.approx(no_credit["OCC_1"])
    assert one_credit["avg_OCC"] < no_credit["avg_OCC"]


def test_financing_inputs_affect_tci_but_not_overnight_cost():
    low_interest = _run(interest_percent=0)
    high_interest = _run(interest_percent=12)

    assert high_interest["OCC_1"] == pytest.approx(low_interest["OCC_1"])
    assert high_interest["TCI_1"] > low_interest["TCI_1"]


@pytest.mark.parametrize("config_key", ["f_22", "f_2321"])
@pytest.mark.xfail(
    strict=True,
    reason="AP1000 add_factory_cost currently ignores f_22 and f_2321; investigate before changing model logic",
)
def test_factory_allocation_inputs_reach_gross_occ(config_key):
    low = _run(config_overrides={config_key: 0})
    high = _run(config_overrides={config_key: 500_000_000})

    assert high["OCC_1"] != pytest.approx(low["OCC_1"])


@pytest.mark.parametrize("reactor_type", ["SFR", "HTGR"])
@pytest.mark.parametrize("config_key", ["f_22", "f_2321"])
def test_factory_allocation_inputs_reach_non_ap1000_gross_occ(reactor_type, config_key):
    low = _run(reactor_type, config_overrides={config_key: 0})
    high = _run(reactor_type, config_overrides={config_key: 500_000_000})

    assert high["OCC_1"] != pytest.approx(low["OCC_1"])


def test_land_cost_is_visible_in_gross_occ_but_not_construction_duration():
    low = _run(config_overrides={"land_cost_per_acre_0": 0})
    high = _run(config_overrides={"land_cost_per_acre_0": 44_000})

    assert high["OCC_1"] != pytest.approx(low["OCC_1"])
    assert high["duration_1"] == pytest.approx(low["duration_1"])
