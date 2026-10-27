"""Explicit CLI for drafting a script through the opt-in Gemini adapter."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from .providers.gemini import GeminiConfigurationError, GeminiRequestError, draft_script


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) not in (2, 3):
        print("Usage: btm-draft-script TOPIC RESEARCH_PACKET.json [OUTPUT.json]", file=sys.stderr)
        return 2
    topic, packet_path = args[0], Path(args[1])
    output_path = Path(args[2]) if len(args) == 3 else Path("script-draft.json")
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        result = draft_script(topic, packet)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        print("Research packet could not be read as valid JSON.", file=sys.stderr)
        return 2
    except (GeminiConfigurationError, GeminiRequestError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({
        "output_path": str(output_path),
        "draft_generated": True,
        "structurally_valid": result["validation_report"]["structurally_valid"],
        "editorially_approved": result["validation_report"]["editorially_approved"],
        "public_publish_allowed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
