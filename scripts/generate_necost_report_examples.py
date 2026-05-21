"""Generate NEcost EG03-EG40 SON examples from the LCAE report tables."""

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


def render_son(title, notes, tables, results):
    eg, code = option_code(title)
    weights = weights_for(eg, len(tables))
    lines = [
        "necost {",
        f"    % {title}",
        "    % Source: FCRD-FCO-2013-000196, Appendix A report input tables.",
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
            "    legacy_inputs {",
        ]
    )

    for idx, entries in enumerate(tables, start=1):
        case_id = eg if len(tables) == 1 else f"{eg}_ISLAND_{idx}"
        lines.append(f"        case({case_id}) {{")
        lines.append(f"            % Report LCAE weight for this input table.")
        lines.append(f"            energy_fraction = {fmt(weights[idx - 1])}")
        for entry in entries:
            lines.append(f"            input({entry['line']}) {{")
            lines.append(f"                low = {fmt(entry['low'])}")
            lines.append(f"                nominal = {fmt(entry['nominal'])}")
            lines.append(f"                high = {fmt(entry['high'])}")
            lines.append(f"                distribution = {entry['distribution']}")
            lines.append(f"                description = {son_string(entry['description'])}")
            lines.append("            }")
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
