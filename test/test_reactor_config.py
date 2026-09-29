import pytest

from crt.reactor_config import (
    REACTOR_CONFIGS,
    iat_api_reactor_type,
    reactor_power_mwe,
)


def test_reactor_config_uses_existing_crt_reference_powers():
    assert reactor_power_mwe("AP1000") == pytest.approx(2234.0)
    assert reactor_power_mwe("SFR") == pytest.approx(310.8)
    assert reactor_power_mwe("HTGR") == pytest.approx(1056.0)


def test_reactor_config_maps_one_shared_case_into_iat():
    assert iat_api_reactor_type("AP1000", csv_mode=True) == "ACCERT output-LR"
    assert iat_api_reactor_type("HTGR", csv_mode=True) == "ACCERT output-LR"
    assert iat_api_reactor_type("SFR", csv_mode=True) == "ACCERT output-SMR"
    assert REACTOR_CONFIGS["SFR"]["iat_family"] == "SMR"

