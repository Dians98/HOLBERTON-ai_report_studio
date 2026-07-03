import csv
import json
import io
from collections import Counter


def parse_file(content: bytes, filename: str) -> list[dict]:
    if filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        return [row for row in reader]
    elif filename.endswith(".json"):
        data = json.loads(content.decode("utf-8"))
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
    return []


def is_numeric(value) -> bool:
    if isinstance(value, (int, float)):
        return True
    if not value or not str(value).strip():
        return False
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def compute_metrics(content: bytes, filename: str) -> dict:
    rows = parse_file(content, filename)
    if not rows:
        return {"row_count": 0, "error": "No data found"}

    columns = list(rows[0].keys())
    metrics = {"row_count": len(rows), "columns": columns}

    numeric_cols = []
    for col in columns:
        numeric_count = sum(1 for r in rows if is_numeric(r.get(col, "")))
        if numeric_count > len(rows) / 2:
            numeric_cols.append(col)

    for col in numeric_cols:
        values = []
        for r in rows:
            v = r.get(col, "")
            if is_numeric(v):
                values.append(float(v))

        if values:
            metrics[f"{col}_sum"] = round(sum(values), 2)
            metrics[f"{col}_avg"] = round(sum(values) / len(values), 2)
            metrics[f"{col}_min"] = min(values)
            metrics[f"{col}_max"] = max(values)

    text_cols = [c for c in columns if c not in numeric_cols]
    for col in text_cols:
        vals = [str(r.get(col, "")) for r in rows if r.get(col, "") is not None and r.get(col, "") != ""]
        if vals:
            counter = Counter(vals)
            metrics[f"{col}_top"] = counter.most_common(1)[0][0]
            metrics[f"{col}_top_count"] = counter.most_common(1)[0][1]
            metrics[f"{col}_unique"] = len(counter)

    return metrics
