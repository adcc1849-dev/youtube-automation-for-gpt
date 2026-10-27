"""Explicit CLI for running one skill with provided JSON inputs."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from .providers.gemini import GeminiConfigurationError, GeminiRequestError, run_skill


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) not in (2, 3):
        print("Usage: btm-run-skill SKILL_NAME INPUTS.json [OUTPUT.json]", file=sys.stderr)
        return 2
    skill_name, input_path = args[0], Path(args[1])
    output_path = Path(args[2]) if len(args) == 3 else Path(f"{skill_name}-result.json")
    try:
        inputs = json.loads(input_path.read_text(encoding="utf-8"))
        result = run_skill(skill_name, inputs)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        print("Inputs file could not be read as valid JSON.", file=sys.stderr)
        return 2
    except (GeminiConfigurationError, GeminiRequestError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"output_path": str(output_path), "skill": skill_name,
                      "human_review_required": True, "public_publish_allowed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
