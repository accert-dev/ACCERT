import pytest

from crt.reactor_config import (
    REACTOR_CONFIGS,
    compatible_crt_types,
    iat_api_reactor_type,
    iat_api_type_from_label,
    reactor_power_mwe,
)


def test_reactor_config_uses_existing_crt_reference_powers():
    assert reactor_power_mwe("AP1000") == pytest.approx(2234.0)
    assert reactor_power_mwe("SFR") == pytest.approx(310.8)
    assert reactor_power_mwe("HTGR") == pytest.approx(1056.0)


def test_reactor_config_maps_one_shared_case_into_iat():
    assert iat_api_reactor_type("AP1000", csv_mode=True) == "ACCERT output-LR"
    assert iat_api_reactor_type("SFR", csv_mode=True) == "ACCERT output-SMR"
    assert compatible_crt_types("Large Reactor") == ("AP1000",)
    assert compatible_crt_types("SMR") == ("SFR", "HTGR")
    assert iat_api_type_from_label("Large Reactor", csv_mode=True) == "ACCERT output-LR"
    assert iat_api_type_from_label("SMR", csv_mode=True) == "ACCERT output-SMR"
    with pytest.raises(ValueError, match="No compatible IAT reactor family"):
        iat_api_reactor_type("HTGR", csv_mode=True)
