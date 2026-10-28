"""Post-upload verification of YouTube metadata, visibility, and processing state."""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any


class VerificationError(RuntimeError):
    """Raised when post-upload verification fails or cannot be completed."""


def verify_video(video_id: str, *, youtube: Any, expected_title: str | None = None,
                 expected_visibility: str | None = None) -> dict[str, Any]:
    if not video_id or not video_id.strip():
        raise VerificationError("video_id must be non-empty")
    response = youtube.videos().list(
        part="snippet,status,processingDetails,contentDetails",
        id=video_id.strip(),
    ).execute()
    items = response.get("items", [])
    if len(items) != 1:
        raise VerificationError("YouTube API did not return exactly one matching video")
    item = items[0]
    snippet = item.get("snippet", {})
    status = item.get("status", {})
    processing = item.get("processingDetails", {})
    mismatches = []
    if expected_title is not None and snippet.get("title") != expected_title:
        mismatches.append("title_mismatch")
    if expected_visibility is not None and status.get("privacyStatus") != expected_visibility:
        mismatches.append("visibility_mismatch")
    processing_status = processing.get("processingStatus", "unknown")
    if processing_status in {"failed", "terminated"}:
        mismatches.append("processing_failed")
    if mismatches:
        raise VerificationError("post-upload verification failed: " + ", ".join(mismatches))
    return {
        "video_id": item.get("id"),
        "url": f"https://www.youtube.com/watch?v={item.get('id')}",
        "title": snippet.get("title"),
        "privacy_status": status.get("privacyStatus"),
        "upload_status": status.get("uploadStatus"),
        "processing_status": processing_status,
        "duration": item.get("contentDetails", {}).get("duration"),
        "verified": True,
        "verification_scope": [
            "video_exists", "title", "privacy_status", "processing_status", "duration"
        ],
        "not_verified": [
            "thumbnail_image", "caption_track_content_and_timing", "human_playback_quality"
        ],
    }


def verify_from_environment(video_id: str, expected_title: str | None = None,
                            expected_visibility: str | None = None) -> dict[str, Any]:
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    missing = [name for name, value in (
        ("YOUTUBE_CLIENT_ID", client_id),
        ("YOUTUBE_CLIENT_SECRET", client_secret),
        ("YOUTUBE_REFRESH_TOKEN", refresh_token),
    ) if not value]
    if missing:
        raise VerificationError("missing OAuth environment variables: " + ", ".join(missing))
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise VerificationError("Install optional dependencies with: pip install -e '.[publishing]'") from None
    credentials = Credentials(
        token=None, refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id, client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    )
    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    return verify_video(video_id, youtube=youtube, expected_title=expected_title,
                        expected_visibility=expected_visibility)


def verify_receipt(receipt_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    result = verify_from_environment(
        receipt.get("video_id", ""),
        expected_title=receipt.get("title"),
        expected_visibility=receipt.get("visibility_requested"),
    )
    output = Path(output_path)
    if output.exists():
        raise VerificationError("verification output already exists; choose a new path")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\\n", encoding="utf-8")
    return result
