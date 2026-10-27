"""CLI for local ffprobe media inspection."""
from __future__ import annotations

import json
import sys
from typing import Sequence

from .media import inspect_media


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: btm-inspect-media PATH_TO_MEDIA_FILE", file=sys.stderr)
        return 2
    report = inspect_media(args[0])
    print(json.dumps(report, indent=2))
    return 0 if report.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
