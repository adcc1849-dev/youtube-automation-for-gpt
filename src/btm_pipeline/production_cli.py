"""CLI for the complete local production sequence."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from .production import ProductionError, run_production


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("Usage: btm-produce CONFIG.json REPORT.json", file=sys.stderr)
        return 2
    config_path, report_path = map(Path, args)
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ProductionError("config root must be a JSON object")
        config["report_path"] = str(report_path)
        report = run_production(config)
    except (OSError, json.JSONDecodeError, ProductionError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report.get("production_completed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
