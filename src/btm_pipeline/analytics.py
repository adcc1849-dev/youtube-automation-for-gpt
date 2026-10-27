"""Free-first YouTube Analytics snapshots and conservative performance diagnosis."""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ANALYTICS_SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"
CORE_METRICS = (
    "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,"
    "likes,comments,shares,subscribersGained,subscribersLost"
)
DISCOVERY_METRICS = "impressions,impressionClickThroughRate"


class AnalyticsError(RuntimeError):
    """Raised when analytics cannot be safely collected or interpreted."""


def diagnose_video(row: dict[str, Any]) -> dict[str, Any]:
    """Return evidence-aware observations, not a universal quality or virality score."""
    observations: list[str] = []
    views = row.get("views")
    ctr = row.get("impressionClickThroughRate")
    avg_pct = row.get("averageViewPercentage")
    impressions = row.get("impressions")
    if isinstance(impressions, (int, float)) and impressions < 100:
        observations.append("low_impression_sample: do not over-interpret CTR")
    if isinstance(ctr, (int, float)) and isinstance(impressions, (int, float)) and impressions >= 100:
        if ctr < 0.03:
            observations.append("packaging_review_candidate: CTR below 3% in this snapshot; compare with channel baseline")
        elif ctr >= 0.07:
            observations.append("packaging_signal_positive: CTR at least 7% in this snapshot; verify traffic mix and sample size")
    if isinstance(avg_pct, (int, float)):
        if avg_pct < 25:
            observations.append("retention_review_candidate: inspect promise-to-opening match and pacing")
        elif avg_pct >= 50:
            observations.append("retention_signal_positive: compare with similar-length videos and traffic sources")
    if isinstance(views, (int, float)) and views < 30:
        observations.append("small_view_sample: avoid strong conclusions")
    if not observations:
        observations.append("insufficient_signal_for_rule_based_diagnosis")
    return {"observations": observations, "is_virality_prediction": False}


def date_windows(end_date: str) -> dict[str, tuple[str, str]]:
    """Build comparable trailing 1/7/28-day date windows ending on the supplied date."""
    try:
        end = date.fromisoformat(end_date)
    except ValueError:
        raise AnalyticsError("end_date must be an ISO date (YYYY-MM-DD)") from None
    return {
        "1d": (end.isoformat(), end.isoformat()),
        "7d": ((end - timedelta(days=6)).isoformat(), end.isoformat()),
        "28d": ((end - timedelta(days=27)).isoformat(), end.isoformat()),
    }


def collect_snapshot(end_date: str, *, youtube_analytics: Any, youtube_data: Any | None = None) -> dict[str, Any]:
    """Collect video-level analytics for comparable windows, preserving returned rows."""
    windows = date_windows(end_date)
    snapshot: dict[str, Any] = {
        "end_date": end_date,
        "windows": {},
        "notes": [
            "Metrics are a snapshot, not a virality prediction.",
            "Compare only equivalent windows and account for video age, traffic mix, and sample size.",
            "Unavailable metrics are recorded as unavailable rather than inferred.",
        ],
    }
    for label, (start, end) in windows.items():
        params = {
            "ids": "channel==MINE",
            "startDate": start,
            "endDate": end,
            "metrics": CORE_METRICS,
            "dimensions": "video",
            "sort": "-views",
            "maxResults": 200,
        }
        result = youtube_analytics.reports().query(**params).execute()
        headers = [h.get("name") for h in result.get("columnHeaders", [])]
        rows = []
        for values in result.get("rows", []):
            row = dict(zip(headers, values))
            row["diagnosis"] = diagnose_video(row)
            rows.append(row)
        snapshot["windows"][label] = {
            "start_date": start,
            "end_date": end,
            "row_count": len(rows),
            "rows": rows,
            "discovery_metrics_status": "not_requested_in_core_query",
        }
    if youtube_data is not None:
        try:
            channel = youtube_data.channels().list(part="snippet", mine=True).execute()
            snapshot["channel_title"] = (
                channel.get("items", [{}])[0].get("snippet", {}).get("title")
                if channel.get("items") else None
            )
        except Exception:
            snapshot["channel_title"] = None
            snapshot["notes"].append("Channel title lookup failed; analytics rows are retained.")
    return snapshot


def collect_from_environment(end_date: str) -> dict[str, Any]:
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    missing = [name for name, value in (
        ("YOUTUBE_CLIENT_ID", client_id),
        ("YOUTUBE_CLIENT_SECRET", client_secret),
        ("YOUTUBE_REFRESH_TOKEN", refresh_token),
    ) if not value]
    if missing:
        raise AnalyticsError("missing OAuth environment variables: " + ", ".join(missing))
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise AnalyticsError("Install optional dependencies with: pip install -e '.[publishing]'") from None
    credentials = Credentials(
        token=None, refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id, client_secret=client_secret,
        scopes=[ANALYTICS_SCOPE],
    )
    service = build("youtubeAnalytics", "v2", credentials=credentials, cache_discovery=False)
    return collect_snapshot(end_date, youtube_analytics=service)


def write_snapshot(snapshot: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path).expanduser()
    if path.exists():
        raise AnalyticsError("snapshot output already exists; choose a new path to preserve history")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return path
