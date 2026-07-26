"""
Report Generator module.

Turns any analysis result (a plain dict) into a saved TXT, JSON, or PDF
report inside the app's reports/ directory (SalmTool/reports/ at runtime,
resolved via the app's user_data_dir on-device).
"""

import json
import os
import time

try:
    from fpdf import FPDF
except Exception:
    FPDF = None


def _timestamp():
    return time.strftime("%Y%m%d_%H%M%S")


def _flatten(data, prefix=""):
    """Turns a nested dict/list structure into flat, readable lines for
    the TXT and PDF exporters."""
    lines = []
    if isinstance(data, dict):
        for k, v in data.items():
            key = f"{prefix}{k}"
            if isinstance(v, (dict, list)):
                lines.append(f"{key}:")
                lines.extend(_flatten(v, prefix=key + "  "))
            else:
                lines.append(f"{key}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}[{i}]:")
                lines.extend(_flatten(item, prefix=prefix + "  "))
            else:
                lines.append(f"{prefix}[{i}]: {item}")
    else:
        lines.append(f"{prefix}{data}")
    return lines


def save_txt_report(data, reports_dir, name="report"):
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"{name}_{_timestamp()}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"SalmTool Ultimate Report - {name}\n")
        f.write("=" * 50 + "\n\n")
        f.write("\n".join(_flatten(data)))
    return path


def save_json_report(data, reports_dir, name="report"):
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"{name}_{_timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return path


def save_pdf_report(data, reports_dir, name="report"):
    if FPDF is None:
        return None
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"{name}_{_timestamp()}.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SalmTool Ultimate Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, name, ln=True)
    pdf.ln(4)
    pdf.set_font("Courier", "", 9)

    for line in _flatten(data):
        safe_line = line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 5, safe_line)

    pdf.output(path)
    return path


def save_all_formats(data, reports_dir, name="report"):
    return {
        "txt": save_txt_report(data, reports_dir, name),
        "json": save_json_report(data, reports_dir, name),
        "pdf": save_pdf_report(data, reports_dir, name),
    }


def list_reports(reports_dir):
    if not os.path.isdir(reports_dir):
        return []
    files = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir)]
    files.sort(key=os.path.getmtime, reverse=True)
    return files
