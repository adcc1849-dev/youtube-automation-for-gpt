from __future__ import annotations
import json
import pytest
from btm_pipeline.analytics import AnalyticsError, collect_snapshot, date_windows, diagnose_video, write_snapshot


def test_date_windows_are_explicit_and_comparable():
    windows = date_windows("2026-10-28")
    assert windows["1d"] == ("2026-10-27", "2026-10-28")
    assert windows["7d"] == ("2026-10-22", "2026-10-28")
    assert windows["28d"] == ("2026-10-01", "2026-10-28")


def test_bad_date_fails_closed():
    with pytest.raises(AnalyticsError, match="ISO date"):
        date_windows("not-a-date")


def test_diagnosis_marks_small_samples_and_does_not_predict_virality():
    result = diagnose_video({"views": 12, "impressions": 20, "impressionViewRate": 0.9})
    assert "small_view_sample: avoid strong conclusions" in result["observations"]
    assert result["is_virality_prediction"] is False


def test_collect_snapshot_preserves_rows_and_adds_diagnosis():
    class Query:
        def __init__(self, params): self.params = params
        def execute(self):
            return {"columnHeaders": [{"name": "video"}, {"name": "views"}, {"name": "averageViewPercentage"}],
                    "rows": [["abc123", 50, 35.0]]}
    class Reports:
        def query(self, **params): return Query(params)
    class Service:
        def reports(self): return Reports()
    result = collect_snapshot("2026-10-28", youtube_analytics=Service())
    assert set(result["windows"]) == {"1d", "7d", "28d"}
    assert result["windows"]["7d"]["rows"][0]["video"] == "abc123"
    assert result["windows"]["7d"]["rows"][0]["diagnosis"]["is_virality_prediction"] is False


def test_snapshot_does_not_overwrite_history(tmp_path):
    path = tmp_path / "snapshot.json"
    write_snapshot({"windows": {}}, path)
    assert json.loads(path.read_text()) == {"windows": {}}
    with pytest.raises(AnalyticsError, match="already exists"):
        write_snapshot({"windows": {"new": {}}}, path)
