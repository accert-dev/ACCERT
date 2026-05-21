"""Generate structured NEcost EG03-EG40 SON examples from the LCAE report."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DOCX = Path(
    "/Users/jia.zhou/Library/CloudStorage/Box-Box/ne-cost/"
    "LCAE_calculations_FCRD-FCO-2013-000196_Feb_6_2014.docx"
)
OUTPUT_DIR = PROJECT_ROOT / "tutorial" / "necost"

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

WEIGHT_OVERRIDES = {
    "EG12": [0.774, 0.226],
    "EG13": [0.902, 0.098],
    "EG14": [0.706, 0.294],
    "EG15": [0.881, 0.119],
    "EG16": [0.9256, 0.0744],
    "EG17": [0.9049, 0.0951],
    "EG18": [0.687, 0.313],
    "EG23": [0.954, 0.046],
    "EG25": [0.48, 0.52],
    "EG27": [0.584, 0.02, 0.396],
    "EG28": [0.878, 0.122],
    "EG29": [0.611, 0.389],
    "EG30": [0.87, 0.13],
    "EG31": [0.682, 0.318],
    "EG32": [0.6202, 0.3798],
    "EG33": [0.772, 0.065, 0.163],
    "EG34": [0.757, 0.064, 0.179],
    "EG35": [0.847, 0.153],
    "EG36": [0.935, 0.065],
    "EG37": [0.119, 0.434, 0.067, 0.38],
    "EG38": [0.796, 0.059, 0.145],
    "EG39": [0.6964, 0.2434, 0.0602],
    "EG40": [0.205, 0.795],
}


def ascii_clean(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip()


def son_string(text: str) -> str:
    return '"' + ascii_clean(text).replace("\\", "\\\\").replace('"', '\\"') + '"'


def num(text: str) -> float:
    value = ascii_clean(text).replace(",", "")
    if value in {"", "-", "NA", "N/A"}:
        raise ValueError(f"Blank numeric value: {text!r}")
    try:
        return float(value)
    except ValueError:
        match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", value)
        if not match:
            raise
        return float(match.group(0))


def fmt(value: float) -> str:
    if abs(value) >= 100000 or (value and abs(value) < 0.001):
        return f"{value:.8g}"
    return f"{value:.10g}"


def doc_items():
    root = ET.fromstring(ZipFile(REPORT_DOCX).read("word/document.xml"))
    body = root.find("w:body", NS)
    items = []
    for child in body:
        if child.tag.endswith("}p"):
            text = "".join(t.text or "" for t in child.findall(".//w:t", NS)).strip()
            if text:
                items.append(("p", ascii_clean(text)))
        elif child.tag.endswith("}tbl"):
            rows = []
            for tr in child.findall("w:tr", NS):
                cells = []
                for tc in tr.findall("w:tc", NS):
                    parts = []
                    for para in tc.findall("w:p", NS):
                        parts.append("".join(t.text or "" for t in para.findall(".//w:t", NS)).strip())
                    cells.append(ascii_clean(" ".join(parts)))
                rows.append(cells)
            items.append(("tbl", rows))
    return items


def section_heads(items):
    heads = []
    for idx, (typ, data) in enumerate(items):
        if typ != "p":
            continue
        if re.match(r"^EG\d{2}/", data) and "System Data" not in data and "System Datasheet" not in data:
            heads.append((idx, data))
    return heads


def option_code(title: str) -> tuple[str, str]:
    match = re.match(r"^(EG\d{2})/([A-Z]+\d+)(?:/([A-Z]))?", title)
    if not match:
        raise ValueError(f"Could not parse title: {title}")
    eg = match.group(1)
    code = match.group(2) + (match.group(3) or "")
    return eg, code


def is_input_table(rows) -> bool:
    if not rows or len(rows[0]) < 6:
        return False
    header = " ".join(rows[0]).lower()
    return "low" in header and "nominal" in header and "high" in header and "line" in header


def is_result_table(rows) -> bool:
    return bool(rows and rows[0] and "lcae" in rows[0][0].lower() and "discount" in rows[0][0].lower())


def parse_input_table(rows):
    header = [cell.lower() for cell in rows[0]]
    line_idx = next(i for i, cell in enumerate(header) if "line" in cell)
    desc_idx = next((i for i, cell in enumerate(header) if "variable description" in cell), len(rows[0]) - 1)
    entries = []
    for row in rows[1:]:
        if line_idx >= len(row) or not row[line_idx].strip():
            continue
        line_match = re.search(r"\d+", row[line_idx])
        if not line_match:
            continue
        entries.append(
            {
                "line": int(line_match.group(0)),
                "low": num(row[0]),
                "nominal": num(row[1]),
                "high": num(row[2]),
                "distribution": int(num(row[3])),
                "description": row[desc_idx] if desc_idx < len(row) else "",
            }
        )
    return entries


def parse_result_table(rows):
    out = {}
    for row in rows[1:]:
        if len(row) < 3:
            continue
        rate_match = re.search(r"\d+", row[0])
        if rate_match:
            out[int(rate_match.group(0))] = {"mean": num(row[1]), "std": num(row[2])}
    return out


def section_notes(section):
    notes = []
    for typ, data in section:
        if typ != "p":
            continue
        if data.startswith("NE-COST input preparer:") or data.startswith("Technical Reviewer:"):
            notes.append(data)
        if data.startswith("In fuel cycle option") or data.startswith("Fuel cycle option"):
            notes.append(data)
        if "modeled using" in data and "NE-COST island" in data:
            notes.append(data)
        if "fractional energy generated" in data:
            notes.append(data)
    return notes[:8]


def weights_for(eg: str, n_cases: int):
    if n_cases == 1:
        return [1.0]
    weights = WEIGHT_OVERRIDES.get(eg)
    if weights and len(weights) == n_cases:
        return weights
    return [1.0 / n_cases] * n_cases


def entry_map(entries):
    return {item["line"]: item for item in entries}


def get_entry(entries, line, low=None, nominal=None, high=None, distribution=0, description=""):
    found = entry_map(entries).get(line)
    if found:
        return found
    value = 0 if nominal is None else nominal
    return {
        "line": line,
        "low": value if low is None else low,
        "nominal": value,
        "high": value if high is None else high,
        "distribution": distribution,
        "description": description,
    }


def dist_type(code: int) -> str:
    return "uniform" if int(code) == 2 else "triangular"


def distribution_values(entry):
    low = entry["low"]
    nominal = entry["nominal"]
    high = entry["high"]
    if int(entry["distribution"]) == 1 and not low <= nominal <= high:
        low, high = min(low, nominal, high), max(low, nominal, high)
    return low, nominal, high


def cost_item_block(
    indent,
    item_id,
    entry,
    cost_type=None,
    expenditure_time=None,
    lead_time=None,
    value_key="cost_value",
):
    pad = " " * indent
    lines = [f"{pad}item({item_id}) {{"]
    if cost_type:
        lines.append(f"{pad}    cost_type = {cost_type}")
    if expenditure_time is not None:
        lines.append(f"{pad}    expenditure_time = {fmt(expenditure_time)}")
    if value_key:
        lines.append(f"{pad}    {value_key} = {fmt(entry['nominal'])}")
    if lead_time is not None:
        lines.append(f"{pad}    lead_time = {fmt(lead_time)}")
    low, nominal, high = distribution_values(entry)
    lines.append(
        f"{pad}    distribution {{ type = {dist_type(entry['distribution'])} "
        f"low = {fmt(low)} high = {fmt(high)} "
        f"nominal = {fmt(nominal)} }}"
    )
    lines.append(f"{pad}}}")
    return lines


def named(entries, line, fallback):
    return get_entry(entries, line, nominal=fallback)


def reactor_id(eg, table_count, idx):
    return eg if table_count == 1 else f"{eg}_ISLAND_{idx}"


def fuel_id(eg, table_count, idx):
    return f"{reactor_id(eg, table_count, idx)}_FUEL"


def render_son(title, notes, tables, results):
    eg, code = option_code(title)
    weights = weights_for(eg, len(tables))
    lines = [
        "necost {",
        f"    % {title}",
        "    % Source: FCRD-FCO-2013-000196, Appendix A report input tables.",
        "    % Structured from the report into fuel_cycles, reactors, cost tables, and fuels.",
    ]
    for note in notes:
        lines.append(f"    % {note}")
    if results:
        for rate in sorted(results):
            row = results[rate]
            lines.append(
                f"    % Report LCAE at {rate}% discount rate: mean {row['mean']} mills/kWh, "
                f"std {row['std']} mills/kWh."
            )
    lines.extend(
        [
            "",
            "    construction_interest_rate = 0.05",
            "    operations_interest_rate = 0.05",
            "    sample_size = 2000",
            "",
            "    fuel_cycles {",
            f"        cycle({eg}) {{",
        ]
    )
    for idx, entries in enumerate(tables, start=1):
        rid = reactor_id(eg, len(tables), idx)
        lines.append(f"            reactor({rid}) {{")
        if len(tables) > 1:
            lines.append(f"                % Report LCAE energy weight for this island.")
        else:
            lines.append(f"                % Single NE-COST island, so the LCAE weight is 100%.")
        lines.append(f"                energy_fraction = {fmt(weights[idx - 1])}")
        lines.append("            }")
    lines.extend(["        }", "    }", "", "    reactors {"])

    for idx, entries in enumerate(tables, start=1):
        rid = reactor_id(eg, len(tables), idx)
        fid = fuel_id(eg, len(tables), idx)
        ref_power = named(entries, 1, 3.0e9)
        efficiency = named(entries, 3, 33)
        hm_mass = named(entries, 4, 88.23)
        capacity = named(entries, 21, 0.9)
        lines.extend(
            [
                f"        reactor({rid}) {{",
                f"            capacity_factor = {fmt(capacity['nominal'])}",
                "            cycle_length = 1.5",
                "            lifetime_years = 60",
                f"            power_level {{ reference_thermal = {fmt(ref_power['nominal'])} net_thermal_efficiency = {fmt(efficiency['nominal'])} }}",
                "            capital_costs { scaling_factor(capital_cost) = 1 }",
                "            om_costs {",
                "                scaling_factor(OM_per_year) = 1",
                "                scaling_factor(OM_per_MWh) = 1",
                "            }",
                "            fuel_reloads {",
                f"                quantity({fid}) {{ heavy_metal_mass = {fmt(hm_mass['nominal'])} fuel_fraction = 1 }}",
                "            }",
                "        }",
            ]
        )
    lines.extend(["    }", "", "    capital_costs {"])

    cap = get_entry(tables[0], 13, low=2300, nominal=4000, high=5800, distribution=1)
    construction = get_entry(tables[0], 19, nominal=5)
    lines.extend(cost_item_block(8, "capital_cost", cap, cost_type="s_curve", expenditure_time=construction["nominal"]))
    lines.extend(["    }", "", "    om_costs {"])

    om_year = get_entry(tables[0], 27, low=58, nominal=70, high=84, distribution=1)
    om_mwh = get_entry(tables[0], 28, low=0.84, nominal=1.9, high=2.6, distribution=1)
    lines.extend(cost_item_block(8, "OM_per_year", om_year, cost_type="fixed", value_key="nominal_value"))
    lines.extend(cost_item_block(8, "OM_per_MWh", om_mwh, cost_type="variable", value_key="nominal_value"))
    lines.extend(["    }", "", "    fuel_costs {"])

    fuel_cost_lines = [
        ("cost_U", 40, "lead_time_purchase", 36, 110),
        ("cost_SWU", 41, "lead_time_nrchmt", 38, 100),
        ("cost_fuel_fab", 42, "lead_time_fab", 39, 350),
        ("cost_conv", 45, "lead_time_conv", 37, 12),
        ("cost_deconv", 46, None, None, 6),
        ("cost_SNF_cond", 48, None, None, 100),
        ("cost_rprocsng", 60, "lead_time_rprocsng", 64, 1850),
        ("cost_MOX_fab", 61, "lead_time_refab", 65, 3200),
        ("cost_FP_cond", 62, "lead_time_FP_cond", 66, 5000),
        ("cost_FP_geologic", 63, "lead_time_FP_disposal", 67, 6500),
        ("cost_conv_rec", 71, "lead_time_conv_rec", 73, 11),
        ("cost_nrchmt_rec", 72, "lead_time_nrchmt_rec", 74, 110),
        ("cost_geologic_disposal", 81, "lead_time_FP_disposal", 67, 550),
        ("cost_ec_rprocsng", 82, "lead_time_rprocsng", 64, 6000),
        ("cost_Th", 89, None, None, 75),
        ("cost_RU_disposal", 94, "lead_time_FP_disposal", 67, 0),
        ("cost_DU_disposal", 96, None, None, 4),
    ]
    first = tables[0]
    for item_id, line_no, _lead_name, lead_line, fallback in fuel_cost_lines:
        cost = get_entry(first, line_no, nominal=fallback)
        lead = get_entry(first, lead_line, nominal=0)["nominal"] if lead_line else None
        lines.extend(cost_item_block(8, item_id, cost, lead_time=lead))

    lines.extend(["    }", "", "    fuels {"])
    for idx, entries in enumerate(tables, start=1):
        fid = fuel_id(eg, len(tables), idx)
        burnup = get_entry(entries, 11, nominal=50)
        batches = get_entry(entries, 12, nominal=3)
        product = get_entry(entries, 33, nominal=4.2)
        feed = get_entry(entries, 34, nominal=0.711)
        tails = get_entry(entries, 35, nominal=0.25)
        fab_loss = get_entry(entries, 49, nominal=0.2)
        conv_loss = get_entry(entries, 50, nominal=0)
        reproc_loss = get_entry(entries, 51, nominal=1)
        recovered_fraction = get_entry(entries, 53, nominal=0)["nominal"]
        primary_fissile = get_entry(entries, 54, nominal=1)
        pu_new = get_entry(entries, 55, nominal=0.098)
        ma_new = get_entry(entries, 56, nominal=0.04)
        pu_prev = get_entry(entries, 57, nominal=0.012)
        ma_prev = get_entry(entries, 58, nominal=0.002)
        fp_prev = get_entry(entries, 59, nominal=0.053)
        rec_product = get_entry(entries, 68, nominal=4.95)
        rec_tails = get_entry(entries, 69, nominal=0.3)
        rec_feed = get_entry(entries, 70, nominal=1.5)
        lines.extend(
            [
                f"        fuel({fid}) {{",
                f"            avg_discharge_burnup = {fmt(burnup['nominal'])}",
                f"            num_batches = {fmt(batches['nominal'])}",
                "            avg_specific_power = 1",
                "            fresh_fuel {",
                f"                fabrication {{ loss_fraction = {fmt(max(fab_loss['nominal'] / 100, 1e-12))} costs = [cost_fuel_fab] }}",
                "                EU { fuel_fraction = 1 costs = [cost_U] }",
                "            }",
                "            spent_fuel {",
                "                costs = [cost_SNF_cond cost_geologic_disposal]",
                "            }",
                "            EU {",
                f"                conversion {{ loss_fraction = {fmt(max(conv_loss['nominal'] / 100, 1e-12))} costs = [cost_conv] }}",
                "                enrichment {",
                "                    type = one_stage",
                "                    loss_fraction = 0.01",
                f"                    stage_1 {{ feed = {fmt(feed['nominal'])} product = {fmt(product['nominal'])} tails = {fmt(tails['nominal'])} }}",
                "                    SWU_costs = [cost_SWU]",
                "                    NU_costs = [cost_U]",
                "                    DU_costs = [cost_DU_disposal]",
                "                }",
                "            }",
            ]
        )
        if recovered_fraction > 0:
            lines.extend(
                [
                    "            RU {",
                    f"                reprocess {{ loss_fraction = {fmt(max(reproc_loss['nominal'] / 100, 1e-12))} costs = [cost_rprocsng] }}",
                    f"                conversion {{ loss_fraction = {fmt(max(conv_loss['nominal'] / 100, 1e-12))} costs = [cost_conv_rec] }}",
                    "                reenrichment {",
                    "                    loss_fraction = 0.01",
                    f"                    stage_1 {{ feed = {fmt(rec_feed['nominal'])} product = {fmt(rec_product['nominal'])} tails = {fmt(rec_tails['nominal'])} }}",
                    "                    SWU_costs = [cost_nrchmt_rec]",
                    "                    DU_costs = [cost_DU_disposal]",
                    "                }",
                    "            }",
                    f"            % Reprocessed stream details from report: primary_fissile={fmt(primary_fissile['nominal'])}, Pu_new={fmt(pu_new['nominal'])}, MA_new={fmt(ma_new['nominal'])}, Pu_prev={fmt(pu_prev['nominal'])}, MA_prev={fmt(ma_prev['nominal'])}, FP_prev={fmt(fp_prev['nominal'])}.",
                ]
            )
        lines.append("        }")

    lines.extend(["    }", "}"])
    filename = OUTPUT_DIR / f"{eg}.{code}.son"
    return filename, "\n".join(lines) + "\n"


def main():
    for stale in OUTPUT_DIR.glob("EG??.[A-Z][A-Z].son"):
        stale.unlink()
    items = doc_items()
    heads = section_heads(items)
    generated = []
    for pos, (start, title) in enumerate(heads):
        eg, _ = option_code(title)
        if not (3 <= int(eg[2:]) <= 40) or eg in {"EG13", "EG23"}:
            continue
        end = heads[pos + 1][0] if pos + 1 < len(heads) else len(items)
        section = items[start:end]
        input_tables = [parse_input_table(data) for typ, data in section if typ == "tbl" and is_input_table(data)]
        if not input_tables:
            raise RuntimeError(f"No input table found for {title}")
        result_tables = [parse_result_table(data) for typ, data in section if typ == "tbl" and is_result_table(data)]
        results = result_tables[-1] if result_tables else {}
        filename, text = render_son(title, section_notes(section), input_tables, results)
        filename.write_text(text)
        generated.append(filename.name)
    print("\n".join(generated))


if __name__ == "__main__":
    main()
