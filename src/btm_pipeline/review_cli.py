"""CLI for local preflight review of a JSON production bundle."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from .review import review_bundle


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: btm-review-bundle PATH_TO_BUNDLE.json", file=sys.stderr)
        return 2
    try:
        bundle = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(json.dumps({"error": "bundle could not be read as valid JSON"}, indent=2), file=sys.stderr)
        return 2
    report = review_bundle(bundle)
    print(json.dumps(report, indent=2))
    return 0 if report.get("overall_ready_for_private_review") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
