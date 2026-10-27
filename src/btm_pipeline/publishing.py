"""Fail-closed YouTube Data API uploader. Public uploads require separate policy activation."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

REQUIRED_GATES = (
    "factual_evidence",
    "asset_rights",
    "technical",
    "metadata",
    "security",
)


class PublishingError(RuntimeError):
    """Raised when an upload cannot safely proceed."""


def validate_release(
    manifest: Any,
    video_path: str | Path,
    *,
    visibility: str = "private",
    policy: Any | None = None,
    receipt_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate all release prerequisites without making a network request."""
    if not isinstance(manifest, dict):
        raise PublishingError("release manifest must be a JSON object")
    gates = manifest.get("release_gates")
    if not isinstance(gates, dict):
        raise PublishingError("release_gates must be an object")
    failed = [name for name in REQUIRED_GATES if gates.get(name) is not True]
    if failed:
        raise PublishingError("mandatory release gates not passed: " + ", ".join(failed))
    if manifest.get("human_review_complete") is not True:
        raise PublishingError("human review must be explicitly marked complete")
    metadata = manifest.get("metadata")
    if not isinstance(metadata, dict):
        raise PublishingError("metadata must be an object")
    title = metadata.get("title")
    description = metadata.get("description")
    if not isinstance(title, str) or not title.strip() or len(title) > 100:
        raise PublishingError("metadata.title must contain 1–100 characters")
    if not isinstance(description, str) or not description.strip():
        raise PublishingError("metadata.description must be non-empty")
    tags = metadata.get("tags", [])
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise PublishingError("metadata.tags must be a list of strings")
    if visibility not in {"private", "unlisted", "public"}:
        raise PublishingError("visibility must be private, unlisted, or public")
    if visibility == "public":
        if not isinstance(policy, dict):
            raise PublishingError("public publishing requires an explicit policy object")
        if policy.get("public_publishing_enabled") is not True:
            raise PublishingError("public publishing is disabled by policy")
        if policy.get("owner_public_activation_authorized") is not True:
            raise PublishingError("explicit owner public activation is required")
        if policy.get("staged_private_end_to_end_tests_required") is not True:
            raise PublishingError("policy must require staged private end-to-end tests")
        if manifest.get("staged_private_end_to_end_tests_passed") is not True:
            raise PublishingError("staged private end-to-end tests must be recorded as passed")
    path = Path(video_path).expanduser()
    if not path.is_file() or path.stat().st_size <= 0:
        raise PublishingError("video_path must point to a non-empty video file")
    if receipt_path is not None and Path(receipt_path).expanduser().exists():
        raise PublishingError("upload receipt already exists; refusing a possible duplicate upload")
    return {
        "title": title.strip(),
        "description": description.strip(),
        "tags": tags,
        "visibility": visibility,
        "video_path": str(path),
    }


def upload_video(
    manifest_path: str | Path,
    video_path: str | Path,
    receipt_path: str | Path,
    *,
    visibility: str = "private",
    policy_path: str | Path = "config/publishing-policy.json",
) -> dict[str, Any]:
    """Upload through OAuth refresh-token credentials and save an audit receipt.

    Credentials are read only from environment variables. No credentials are written
    to the receipt or logs. The receipt must be preserved between retries to avoid
    creating a duplicate video.
    """
    try:
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublishingError(f"manifest/policy could not be read: {exc}") from None
    receipt = Path(receipt_path).expanduser()
    details = validate_release(
        manifest, video_path, visibility=visibility, policy=policy, receipt_path=receipt
    )

    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    missing = [key for key, value in (
        ("YOUTUBE_CLIENT_ID", client_id),
        ("YOUTUBE_CLIENT_SECRET", client_secret),
        ("YOUTUBE_REFRESH_TOKEN", refresh_token),
    ) if not value]
    if missing:
        raise PublishingError("missing OAuth environment variables: " + ", ".join(missing))

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        raise PublishingError(
            "YouTube upload dependencies missing; install the optional publishing requirements"
        ) from None

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    body = {
        "snippet": {
            "title": details["title"],
            "description": details["description"],
            "tags": details["tags"],
            "categoryId": str(manifest.get("category_id", "28")),
        },
        "status": {
            "privacyStatus": details["visibility"],
            "selfDeclaredMadeForKids": bool(manifest.get("made_for_kids", False)),
        },
    }
    media = MediaFileUpload(details["video_path"], chunksize=8 * 1024 * 1024,
                            resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response.get("id")
    if not video_id:
        raise PublishingError("YouTube returned no video ID; upload cannot be verified")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "visibility_requested": details["visibility"],
        "title": details["title"],
        "upload_complete": True,
        "verification_status": "upload_acknowledged_metadata_verification_pending",
    }, indent=2) + "\n", encoding="utf-8")
    return json.loads(receipt.read_text(encoding="utf-8"))
