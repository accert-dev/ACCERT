import math

from .Algorithm import Algorithm


class LPSRFunc(Algorithm):
    """ACCERT algorithms used by the TIMCAT-derived LPSR level-2 tables."""

    def __init__(
        self,
        ind,
        alg_name,
        alg_for,
        alg_description,
        alg_formulation,
        alg_units,
        variables,
        constants,
    ):
        super().__init__(
            ind,
            alg_name,
            alg_for,
            alg_description,
            alg_formulation,
            alg_units,
            variables,
            constants,
        )

    def run(self, inputs: dict) -> float:
        values = [inputs[var.strip()] for var in self.variables.split(",") if var.strip()]
        return self._run_algorithm(self.name, values)

    def _run_algorithm(self, alg_name: str, values: list) -> float:
        method = alg_name.strip()
        try:
            algorithm = getattr(self, method)
        except AttributeError as exc:
            raise ValueError(f"Algorithm {alg_name} not found") from exc
        return algorithm(*values)

    @staticmethod
    def lpsr_scaled_cost(*values):
        reference_cost, multiplier = values
        return reference_cost * multiplier

    @staticmethod
    def lpsr_fixed_cost(*values):
        cost, = values
        return cost

    @staticmethod
    def lpsr_total_cost(*values):
        return sum(values)

    @staticmethod
    def lpsr_option_1_scale(*values):
        new_base_unit_value, eedb_base_unit_value, exponent = values
        return math.pow(new_base_unit_value / eedb_base_unit_value, exponent)

    @staticmethod
    def lpsr_option_2_scale(*values):
        new_base_unit_value, eedb_base_unit_value, exponent = values
        return math.pow(new_base_unit_value / eedb_base_unit_value, exponent)

    @staticmethod
    def lpsr_option_3_scale(*values):
        new_base_unit_value, eedb_base_unit_value = values
        return new_base_unit_value / eedb_base_unit_value

    @staticmethod
    def lpsr_option_4_scale(*values):
        return 1.0

    @staticmethod
    def lpsr_option_0_power_scale(*values):
        a, b, new_base_unit_value, exponent, factor, eedb_base_unit_value = values
        return ((a + b * math.pow(new_base_unit_value, exponent)) * factor) / eedb_base_unit_value

    @staticmethod
    def lpsr_option_0_linear_scale(*values):
        factor, new_base_unit_value, eedb_base_unit_value = values
        return factor * new_base_unit_value / eedb_base_unit_value
