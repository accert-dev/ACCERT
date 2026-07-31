from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
from prettytable import PrettyTable

from cost_escalation import TARGET_DOLLAR_YEAR


@dataclass(frozen=True)
class AccertOCCResults:
    total_calculated_direct_cost: float
    electric_power_mw: Optional[float] = None
    escalation_factor: float = 1.0
    target_dollar_year: int = TARGET_DOLLAR_YEAR
    direct_cost_fraction: float = 1.0
    indirect_cost_factor: float = 0.609
    owner_cost_fraction: float = 0.2

    @property
    def total_direct_cost(self) -> float:
        return self.total_calculated_direct_cost / self.direct_cost_fraction

    @property
    def total_indirect_costs(self) -> float:
        return self.total_calculated_direct_cost * self.indirect_cost_factor / self.direct_cost_fraction

    @property
    def total_cost_without_owner(self) -> float:
        return self.total_calculated_direct_cost * (1 + self.indirect_cost_factor) / self.direct_cost_fraction

    @property
    def owner_cost(self) -> float:
        return self.total_cost_without_owner * self.owner_cost_fraction

    @property
    def total_OCC(self) -> float:
        return self.total_cost_without_owner * (1 + self.owner_cost_fraction)

    def _per_kw(self, value: float) -> float:
        if self.electric_power_mw is None or self.electric_power_mw <= 0:
            return None
        return value / (self.electric_power_mw * 1000)

    def _target_year_value(self, value: float) -> float:
        return value * self.escalation_factor

    def as_dict(self) -> Dict[str, float]:
        return {
            "total_calculated_direct_cost": self.total_calculated_direct_cost,
            "total_direct_cost": self.total_direct_cost,
            "total_indirect_costs": self.total_indirect_costs,
            "total_cost_without_owner": self.total_cost_without_owner,
            "owner_cost": self.owner_cost,
            "total_OCC": self.total_OCC,
        }

    def as_rows(self) -> List[Dict[str, float]]:
        return [
            {
                "metric": metric,
                "value_dollar": value,
                "value_million_dollar": value / 1_000_000,
                "value_escalated_dollar": self._target_year_value(value),
                "value_escalated_million_dollar": self._target_year_value(value) / 1_000_000,
                "value_escalated_dollar_per_kw": self._per_kw(self._target_year_value(value)),
                "escalated_dollar_year": self.target_dollar_year,
            }
            for metric, value in self.as_dict().items()
        ]


class AccertPostProcessor:
    DIRECT_COST_FRACTIONS = {
        "abr1000": 0.834,
        "ap1000": 1.0,
        "heatpipe": 0.834,
        "lfr": 0.834,
        "fusion": 1.0,
        "lpsr": 1.0,
        "pwr12-be": 1.0,
        "stellarator": 1.0,
    }

    def calculate_occ(
        self,
        c,
        account_table: str,
        electric_power_mw: float = None,
        ref_model: str = "",
        escalation_factor: float = 1.0,
        target_dollar_year: int = TARGET_DOLLAR_YEAR,
    ) -> AccertOCCResults:
        account_table = self._validate_table_name(account_table)
        c.execute("""SELECT total_cost
                    FROM {}
                    WHERE code_of_account = ?
                    ORDER BY ind
                    LIMIT 1;""".format(account_table), ("2",))
        row = c.fetchone()
        if row is None:
            c.execute("""SELECT total_cost
                        FROM {}
                        ORDER BY ind
                        LIMIT 1;""".format(account_table))
            row = c.fetchone()
        if row is None:
            raise ValueError("Cannot calculate ACCERT OCC because the account table is empty")
        return AccertOCCResults(
            total_calculated_direct_cost=float(row[0]),
            electric_power_mw=float(electric_power_mw) if electric_power_mw is not None else None,
            escalation_factor=escalation_factor,
            target_dollar_year=target_dollar_year,
            direct_cost_fraction=self.DIRECT_COST_FRACTIONS.get(str(ref_model).lower(), 1.0),
        )

    def print_occ_summary(self, results: AccertOCCResults) -> None:
        print(' ACCERT post processing '.center(100, '='))
        print('\n')
        table = PrettyTable()
        table.field_names = ["Metric", "Reference year ($)", f"{results.target_dollar_year} ($)", f"{results.target_dollar_year} ($/kW)"]
        for label, key in (
            ("Total calculated direct cost", "total_calculated_direct_cost"),
            ("Total direct cost", "total_direct_cost"),
            ("Total indirect costs", "total_indirect_costs"),
            ("Total cost without owner", "total_cost_without_owner"),
            ("Owner cost", "owner_cost"),
            ("Total OCC", "total_OCC"),
        ):
            value = results.as_dict()[key]
            target_value = results._target_year_value(value)
            per_kw = results._per_kw(target_value)
            table.add_row([
                label,
                f"{value:,.2f}",
                f"{target_value:,.2f}",
                f"{per_kw:,.2f}" if per_kw is not None else "N/A",
            ])
        print(table)
        print('\n')

    def write_occ_csv(self, results: AccertOCCResults, ref_model: str, timestamp: str) -> str:
        filename = "{}_post_{}.csv".format(ref_model, timestamp)
        pd.DataFrame(results.as_rows()).to_csv(filename, index=False)
        print(f"Successfully created CSV file {filename}")
        return filename

    def _validate_table_name(self, table_name: str) -> str:
        if not table_name or not str(table_name).replace("_", "").isalnum():
            raise ValueError(f"Invalid account table name: {table_name}")
        return str(table_name)
