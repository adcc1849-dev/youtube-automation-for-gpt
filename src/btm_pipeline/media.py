"""Local, offline technical inspection of rendered media using ffprobe."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def inspect_media(
    path: str | Path,
    *,
    minimum_duration_seconds: float = 480,
    maximum_duration_seconds: float = 720,
    ffprobe_binary: str = "ffprobe",
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Inspect an existing local file. Does not render, upload, or access network."""
    media_path = Path(path).expanduser()
    blockers: list[str] = []
    if not media_path.exists() or not media_path.is_file():
        return {"passed": False, "path": str(media_path), "blockers": ["media file does not exist or is not a regular file"]}
    if minimum_duration_seconds <= 0 or maximum_duration_seconds < minimum_duration_seconds:
        return {"passed": False, "path": str(media_path), "blockers": ["invalid duration bounds"]}
    executable = shutil.which(ffprobe_binary)
    if executable is None:
        return {"passed": False, "path": str(media_path), "blockers": [f"{ffprobe_binary} executable was not found; install FFmpeg locally to inspect media"]}
    command = [
        executable, "-v", "error", "-show_entries",
        "format=duration:stream=codec_type", "-of", "json", str(media_path),
    ]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        return {"passed": False, "path": str(media_path), "blockers": ["ffprobe timed out"]}
    except OSError:
        return {"passed": False, "path": str(media_path), "blockers": ["ffprobe could not be executed"]}
    if result.returncode != 0:
        # Avoid echoing arbitrary media/parser output into release reports.
        return {"passed": False, "path": str(media_path), "blockers": ["ffprobe could not parse the media file"]}
    try:
        payload = json.loads(result.stdout)
        duration = float(payload["format"]["duration"])
        streams = payload.get("streams", [])
        stream_types = {stream.get("codec_type") for stream in streams if isinstance(stream, dict)}
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {"passed": False, "path": str(media_path), "blockers": ["ffprobe output is missing required duration/stream data"]}

    if not minimum_duration_seconds <= duration <= maximum_duration_seconds:
        blockers.append(f"duration {duration:.2f}s is outside allowed range {minimum_duration_seconds:.0f}–{maximum_duration_seconds:.0f}s")
    if "video" not in stream_types:
        blockers.append("video stream is missing")
    if "audio" not in stream_types:
        blockers.append("audio stream is missing")
    return {
        "passed": not blockers,
        "path": str(media_path),
        "duration_seconds": round(duration, 3),
        "stream_types": sorted(stream_type for stream_type in stream_types if isinstance(stream_type, str)),
        "checks": {
            "file_exists": True,
            "duration_valid": minimum_duration_seconds <= duration <= maximum_duration_seconds,
            "audio_valid": "audio" in stream_types,
            "video_stream_valid": "video" in stream_types,
        },
        "blockers": blockers,
        "important_limit": "This is a technical stream/duration check only. It does not assess visual quality, intelligibility, synchronization, factual accuracy, rights, or platform policy.",
    }
