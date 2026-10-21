from __future__ import annotations

import json
from pathlib import Path

def write_report(
    report: dict[str, object],
    destination: Path,
) -> None:
    """Write a readable JSON report to the requested destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )