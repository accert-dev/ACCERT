from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
from prettytable import PrettyTable


@dataclass(frozen=True)
class AccertOCCResults:
    total_calculated_direct_cost: float
    direct_cost_fraction: float = 0.834
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
            }
            for metric, value in self.as_dict().items()
        ]


class AccertPostProcessor:
    def calculate_occ(self, c, account_table: str) -> AccertOCCResults:
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
        return AccertOCCResults(total_calculated_direct_cost=float(row[0]))

    def print_occ_summary(self, results: AccertOCCResults) -> None:
        print(' ACCERT post processing '.center(100, '='))
        print('\n')
        table = PrettyTable()
        table.field_names = ["Metric", "Value ($)", "Value (million $)"]
        for label, key in (
            ("Total calculated direct cost", "total_calculated_direct_cost"),
            ("Total direct cost", "total_direct_cost"),
            ("Total indirect costs", "total_indirect_costs"),
            ("Total cost without owner", "total_cost_without_owner"),
            ("Owner cost", "owner_cost"),
            ("Total OCC", "total_OCC"),
        ):
            value = results.as_dict()[key]
            table.add_row([label, f"{value:,.2f}", f"{value / 1_000_000:,.2f}"])
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
