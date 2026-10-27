"""Command-line manifest validator."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from .gates import evaluate_release


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: btm-validate PATH_TO_MANIFEST.json", file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    if not isinstance(manifest, dict):
        print(json.dumps({"error": "manifest root must be a JSON object"}, indent=2), file=sys.stderr)
        return 2
    report = evaluate_release(manifest)
    print(json.dumps(report, indent=2))
    return 0 if report["release_ready_for_private_review"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
