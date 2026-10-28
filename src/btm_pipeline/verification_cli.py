"""CLI for post-upload verification."""
from __future__ import annotations
import argparse
import json
import sys
from .verification import VerificationError, verify_receipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify uploaded YouTube video metadata and processing")
    parser.add_argument("receipt")
    parser.add_argument("output")
    args = parser.parse_args(argv)
    try:
        result = verify_receipt(args.receipt, args.output)
    except (VerificationError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
