"""CLI for local Piper synthesis."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

from .tts import TTSError, synthesize_with_piper


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 5:
        print("Usage: btm-synthesize TEXT_FILE MODEL.onnx VOICE_ASSET_ID RIGHTS_LEDGER.json OUTPUT.wav", file=sys.stderr)
        return 2
    text_path, model_path, voice_asset_id, ledger_path, output_path = args
    try:
        narration = Path(text_path).read_text(encoding="utf-8")
        ledger = json.loads(Path(ledger_path).read_text(encoding="utf-8"))
        report = synthesize_with_piper(narration, model_path, voice_asset_id, ledger, output_path)
    except (OSError, json.JSONDecodeError):
        print("Text or rights-ledger file could not be read.", file=sys.stderr)
        return 2
    except TTSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
