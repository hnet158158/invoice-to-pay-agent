"""CSV export for ERP posting payload — deterministic, field-value format.

Exports the ``posting_payload`` section of an ERP sync plan to a CSV file
so users can inspect vendor bill fields without a live ERP connector.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _flatten(
    d: dict[str, Any],
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, str]:
    """Flatten a nested dict into dot-separated keys with string values.

    Lists are serialised as JSON arrays to preserve structure.
    """
    items: dict[str, str] = {}
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(_flatten(value, new_key, sep=sep))
        elif isinstance(value, list):
            items[new_key] = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
        elif value is None:
            items[new_key] = ""
        else:
            items[new_key] = str(value)
    return items


def export_erp_payload_to_csv(
    erp_sync_plan: dict[str, Any],
    output_path: str | Path = "erp_posting_payload.csv",
) -> Path:
    """Write the ``posting_payload`` section of an ERP sync plan to a
    deterministic CSV file (field, value — sorted by field).

    Args:
        erp_sync_plan: The dict returned by
            ``app.services.erp_integration.build_erp_sync_plan``.
        output_path: Where to write the CSV (default ``erp_posting_payload.csv``).

    Returns:
        Absolute path of the written CSV file.
    """
    payload = erp_sync_plan.get("posting_payload", {})
    flat = _flatten(payload)

    out = Path(output_path)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["field", "value"])
        for key in sorted(flat):
            writer.writerow([key, flat[key]])

    return out.resolve()
