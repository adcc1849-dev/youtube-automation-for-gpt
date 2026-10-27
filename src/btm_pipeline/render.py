"""Offline FFmpeg still-image documentary renderer; no network/provider calls."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .media import inspect_media
from .rights import validate_asset_rights_ledger


class RenderError(RuntimeError):
    """Raised when rendering is blocked or FFmpeg fails."""


def render_documentary(
    render_spec: Any,
    rights_ledger: Any,
    output_path: str | Path,
    *,
    ffmpeg_binary: str = "ffmpeg",
    timeout_seconds: int = 3600,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Render cleared still images with supplied narration and optional cleared music."""
    if not isinstance(render_spec, dict):
        raise RenderError("render spec must be an object")
    rights_report = validate_asset_rights_ledger(rights_ledger)
    if not rights_report["passed"]:
        raise RenderError("asset rights ledger failed; render blocked")
    assets = rights_ledger["assets"]
    asset_ids = {asset["asset_id"] for asset in assets if isinstance(asset, dict) and isinstance(asset.get("asset_id"), str)}

    segments = render_spec.get("segments")
    if not isinstance(segments, list) or not segments:
        raise RenderError("at least one image segment is required")
    narration = render_spec.get("narration_path")
    narration_id = render_spec.get("narration_asset_id")
    if not isinstance(narration, str) or not Path(narration).expanduser().is_file():
        raise RenderError("narration_path must point to an existing local audio file")
    if narration_id not in asset_ids:
        raise RenderError("narration_asset_id is not in the cleared rights ledger")

    normalized_segments: list[tuple[str, float]] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise RenderError(f"segment #{index + 1} must be an object")
        image_path = segment.get("image_path")
        asset_id = segment.get("asset_id")
        duration = segment.get("duration_seconds")
        if not isinstance(image_path, str) or not Path(image_path).expanduser().is_file():
            raise RenderError(f"segment #{index + 1} image_path must point to an existing local file")
        if asset_id not in asset_ids:
            raise RenderError(f"segment #{index + 1} asset_id is not in the cleared rights ledger")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or not 1 <= duration <= 300:
            raise RenderError(f"segment #{index + 1} duration_seconds must be between 1 and 300")
        normalized_segments.append((str(Path(image_path).expanduser()), float(duration)))

    music_path = render_spec.get("music_path")
    music_id = render_spec.get("music_asset_id")
    if music_path:
        if not isinstance(music_path, str) or not Path(music_path).expanduser().is_file():
            raise RenderError("music_path must point to an existing local file")
        if music_id not in asset_ids:
            raise RenderError("music_asset_id is not in the cleared rights ledger")

    output = Path(output_path).expanduser()
    if output.exists() and not overwrite:
        raise RenderError("output already exists; pass overwrite=True only when replacement is intentional")
    if output.suffix.lower() not in {".mp4", ".mkv", ".mov"}:
        raise RenderError("output extension must be .mp4, .mkv, or .mov")
    executable = shutil.which(ffmpeg_binary)
    if executable is None:
        raise RenderError(f"{ffmpeg_binary} executable was not found; install FFmpeg locally")
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [executable, "-hide_banner", "-loglevel", "error", "-y" if overwrite else "-n"]
    for image_path, duration in normalized_segments:
        command.extend(["-loop", "1", "-framerate", "30", "-t", f"{duration:.3f}", "-i", image_path])
    narration_index = len(normalized_segments)
    command.extend(["-i", str(Path(narration).expanduser())])
    music_index = None
    if music_path:
        music_index = narration_index + 1
        command.extend(["-stream_loop", "-1", "-i", str(Path(music_path).expanduser())])

    filters: list[str] = []
    for index, (_, duration) in enumerate(normalized_segments):
        filters.append(
            f"[{index}:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,fps=30,setsar=1,format=yuv420p,"
            f"trim=duration={duration:.3f},setpts=PTS-STARTPTS[v{index}]"
        )
    joined = "".join(f"[v{index}]" for index in range(len(normalized_segments)))
    filters.append(f"{joined}concat=n={len(normalized_segments)}:v=1:a=0[vout]")
    if music_index is not None:
        filters.append(f"[{narration_index}:a]aresample=48000[narr]")
        filters.append(f"[{music_index}:a]volume=0.12,aresample=48000[music]")
        filters.append("[narr][music]amix=inputs=2:duration=first:dropout_transition=2[aout]")
        audio_map = "[aout]"
    else:
        audio_map = f"{narration_index}:a:0"
    command.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", audio_map,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        "-shortest", str(output),
    ])

    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        raise RenderError("FFmpeg render timed out") from None
    except OSError:
        raise RenderError("FFmpeg could not be executed") from None
    if result.returncode != 0:
        raise RenderError("FFmpeg render failed; inspect the local FFmpeg installation and input files")
    report = inspect_media(output)
    if not report.get("passed"):
        raise RenderError("rendered file failed technical QC; output is not cleared for production")
    return {
        "rendered": True,
        "output_path": str(output),
        "technical_qc": report,
        "asset_ids": sorted({narration_id, *(segment.get("asset_id") for segment in segments), *([music_id] if music_path else [])}),
        "public_publish_allowed": False,
        "notice": "Local render only. Human editorial, factual, rights, and platform-policy review remain required.",
    }
