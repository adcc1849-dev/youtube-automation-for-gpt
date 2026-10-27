"""Fail-closed local production runner: Piper narration -> FFmpeg render -> ffprobe QC."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .media import inspect_media
from .render import RenderError, render_documentary
from .tts import TTSError, synthesize_with_piper


class ProductionError(RuntimeError):
    """Raised when production cannot safely continue."""


def run_production(
    config: Any,
    *,
    minimum_duration_seconds: float = 480,
    maximum_duration_seconds: float = 720,
) -> dict[str, Any]:
    """Run local production from explicitly supplied, rights-cleared inputs.

    This function does not download assets/models, call cloud APIs, or publish.
    """
    if not isinstance(config, dict):
        raise ProductionError("config root must be a JSON object")
    required = (
        "script_path", "piper_model_path", "voice_asset_id",
        "voice_rights_ledger_path", "production_rights_ledger_path",
        "narration_asset_id", "segments", "output_path", "report_path",
    )
    missing = [key for key in required if key not in config]
    if missing:
        raise ProductionError("missing required config fields: " + ", ".join(missing))

    def read_json(key: str) -> Any:
        try:
            return json.loads(Path(config[key]).expanduser().read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            raise ProductionError(f"{key} could not be read as valid JSON") from None

    try:
        script = Path(config["script_path"]).expanduser().read_text(encoding="utf-8")
    except (OSError, TypeError):
        raise ProductionError("script_path could not be read") from None
    if not script.strip():
        raise ProductionError("script file is empty")

    voice_ledger = read_json("voice_rights_ledger_path")
    production_ledger = read_json("production_rights_ledger_path")
    if not isinstance(production_ledger, dict) or not isinstance(production_ledger.get("assets"), list):
        raise ProductionError("production rights ledger must contain an assets list")
    narration_id = config["narration_asset_id"]
    narration_asset = next(
        (asset for asset in production_ledger["assets"]
         if isinstance(asset, dict) and asset.get("asset_id") == narration_id),
        None,
    )
    if narration_asset is None:
        raise ProductionError(
            "production rights ledger must explicitly document the generated narration asset "
            "and its provenance/terms before rendering"
        )
    if narration_asset.get("kind") not in {"generated", "original"}:
        raise ProductionError("narration asset kind must be generated or original")

    output_path = Path(config["output_path"]).expanduser()
    narration_path = output_path.with_name(output_path.stem + ".narration.wav")
    report_path = Path(config["report_path"]).expanduser()
    if report_path.exists():
        raise ProductionError("report_path already exists; choose a new report path")
    if output_path.exists() or narration_path.exists():
        raise ProductionError("output or narration file already exists; refusing to overwrite")

    report: dict[str, Any] = {
        "production_completed": False,
        "public_publish_allowed": False,
        "stages": {},
        "blockers": [],
        "notice": "Local production only. No upload or publishing was attempted.",
    }
    try:
        report["stages"]["narration"] = synthesize_with_piper(
            script, config["piper_model_path"], config["voice_asset_id"],
            voice_ledger, narration_path,
        )
        render_spec = {
            "segments": config["segments"],
            "narration_path": str(narration_path),
            "narration_asset_id": narration_id,
        }
        report["stages"]["render"] = render_documentary(
            render_spec, production_ledger, output_path,
        )
        qc = inspect_media(
            output_path,
            minimum_duration_seconds=minimum_duration_seconds,
            maximum_duration_seconds=maximum_duration_seconds,
        )
        report["stages"]["technical_qc"] = qc
        if qc.get("passed") is not True:
            report["blockers"].extend(qc.get("blockers", ["technical QC failed"]))
            report["output_path"] = str(output_path)
            report["production_completed"] = False
        else:
            report["production_completed"] = True
            report["output_path"] = str(output_path)
            report["human_review_required"] = True
            report["notice"] += " Technical QC passed; visual, audio intelligibility, factual, licensing, captions, and editorial review are still required."
    except (TTSError, RenderError, OSError, ValueError) as exc:
        report["blockers"].append(str(exc))
        report["production_completed"] = False

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path)
    return report
