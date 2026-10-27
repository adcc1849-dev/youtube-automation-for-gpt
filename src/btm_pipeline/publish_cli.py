"""Command-line interface for staged YouTube uploads."""
from __future__ import annotations
import argparse
import json
import sys
from .publishing import PublishingError, upload_video


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Upload a reviewed video to YouTube")
    parser.add_argument("manifest")
    parser.add_argument("video")
    parser.add_argument("receipt")
    parser.add_argument("--visibility", choices=("private", "unlisted", "public"), default="private")
    parser.add_argument("--policy", default="config/publishing-policy.json")
    args = parser.parse_args(argv)
    try:
        result = upload_video(args.manifest, args.video, args.receipt,
                              visibility=args.visibility, policy_path=args.policy)
    except (PublishingError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
