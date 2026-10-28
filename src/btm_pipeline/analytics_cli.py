"""CLI for versioned YouTube Analytics snapshots."""
from __future__ import annotations
import argparse
import json
import sys
from .analytics import AnalyticsError, collect_from_environment, write_snapshot


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Collect read-only YouTube Analytics snapshots")
    parser.add_argument("--end-date", required=True, help="ISO date; use a completed reporting day")
    parser.add_argument("--output", required=True, help="New JSON path; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        snapshot = collect_from_environment(args.end_date)
        path = write_snapshot(snapshot, args.output)
    except (AnalyticsError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({"snapshot_path": str(path), "windows": list(snapshot["windows"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
