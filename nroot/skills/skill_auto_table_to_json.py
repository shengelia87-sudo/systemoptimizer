import re

SKILL_META = {"description": "Converts simple CSV/pipe tables into JSON rows"}


def _split_line(line):
    if "|" in line and line.count("|") >= 2:
        parts = [p.strip() for p in line.split("|") if p.strip() != ""]
    elif "," in line:
        parts = [p.strip() for p in line.split(",")]
    elif "\t" in line:
        parts = [p.strip() for p in line.split("\t")]
    else:
        parts = [line.strip()]
    return parts


def table_to_json(text=None, header_hint=None, **kw):
    text = (text or "").strip()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return {"ok": True, "rows": []}
    header = _split_line(lines[0]) if header_hint is None else header_hint
    rows = []
    for ln in lines[1:]:
        parts = _split_line(ln)
        if len(parts) != len(header):
            if len(parts) > len(header):
                parts = parts[: len(header)]
            else:
                parts = parts + [""] * (len(header) - len(parts))
        rows.append({header[i]: parts[i] for i in range(len(header))})
    return {"ok": True, "header": header, "rows": rows}


SKILLS = {"table_to_json": table_to_json}
