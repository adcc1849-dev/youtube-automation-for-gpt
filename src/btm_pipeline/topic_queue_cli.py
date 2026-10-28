"""Rank candidate topics for editorial review."""
from __future__ import annotations
import argparse
import json
import sys
from .topic_queue import TopicQueueError, rank_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Rank next-video candidates without predicting virality")
    parser.add_argument("input", help="JSON list of candidate topics and scored evidence")
    parser.add_argument("output", help="New versioned output JSON path")
    parser.add_argument("--completed-topics", help="Optional JSON list of previously completed topic titles")
    args = parser.parse_args(argv)
    try:
        result = rank_file(args.input, args.output, completed_topics_path=args.completed_topics)
    except (TopicQueueError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "ranked_count": result["candidate_count"],
        "next_topic": result["next_topic"],
        "output": args.output,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
