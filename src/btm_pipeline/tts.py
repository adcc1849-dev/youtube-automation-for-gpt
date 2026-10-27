"""Offline Piper text-to-speech adapter; does not download models or call cloud services."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .rights import validate_asset_rights_ledger


class TTSError(RuntimeError):
    """Raised when offline TTS is blocked or fails."""


def synthesize_with_piper(
    text: str,
    model_path: str | Path,
    voice_asset_id: str,
    rights_ledger: Any,
    output_path: str | Path,
    *,
    piper_binary: str = "piper",
    timeout_seconds: int = 600,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Synthesize text locally using a pre-installed Piper binary and licensed voice model."""
    if not isinstance(text, str) or not text.strip():
        raise TTSError("text must be non-empty")
    ledger_report = validate_asset_rights_ledger(rights_ledger)
    if not ledger_report["passed"]:
        raise TTSError("asset rights ledger failed; TTS blocked")
    assets = rights_ledger["assets"]
    voice_asset = next((asset for asset in assets if isinstance(asset, dict) and asset.get("asset_id") == voice_asset_id), None)
    if voice_asset is None:
        raise TTSError("voice_asset_id is not in the cleared rights ledger")
    if voice_asset.get("kind") not in {"original", "generated", "third_party"}:
        raise TTSError("voice asset kind is unresolved")

    model = Path(model_path).expanduser()
    if not model.is_file():
        raise TTSError("Piper model file does not exist locally; this adapter never downloads models")
    output = Path(output_path).expanduser()
    if output.exists() and not overwrite:
        raise TTSError("output already exists; pass overwrite=True only when replacement is intentional")
    if output.suffix.lower() not in {".wav", ".flac"}:
        raise TTSError("output extension must be .wav or .flac")
    executable = shutil.which(piper_binary)
    if executable is None:
        raise TTSError(f"{piper_binary} executable was not found; install Piper locally")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "--model", str(model), "--output_file", str(output)]
    try:
        result = subprocess.run(command, input=text, check=False, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        raise TTSError("Piper synthesis timed out") from None
    except OSError:
        raise TTSError("Piper could not be executed") from None
    if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        raise TTSError("Piper synthesis failed or produced an empty output file")
    return {
        "synthesized": True,
        "output_path": str(output),
        "voice_asset_id": voice_asset_id,
        "public_publish_allowed": False,
        "notice": "Offline TTS completed. Add a separate provenance/rights record for the generated narration and review the voice model terms before using it in a video.",
    }
