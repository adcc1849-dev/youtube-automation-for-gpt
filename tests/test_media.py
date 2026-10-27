import json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from btm_pipeline.media import inspect_media


def test_missing_file_fails(tmp_path):
    report = inspect_media(tmp_path / "missing.mp4")
    assert report["passed"] is False
    assert any("does not exist" in item for item in report["blockers"])


def test_valid_media_streams_pass(tmp_path):
    media = tmp_path / "video.mp4"
    media.write_bytes(b"not real media; ffprobe mocked")
    stdout = json.dumps({
        "format": {"duration": "600.0"},
        "streams": [{"codec_type": "video"}, {"codec_type": "audio"}],
    })
    with patch("btm_pipeline.media.shutil.which", return_value="/usr/bin/ffprobe"), patch(
        "btm_pipeline.media.subprocess.run",
        return_value=CompletedProcess([], 0, stdout, ""),
    ):
        report = inspect_media(media)
    assert report["passed"] is True
    assert report["duration_seconds"] == 600.0


def test_short_media_fails(tmp_path):
    media = tmp_path / "short.mp4"
    media.write_bytes(b"x")
    stdout = json.dumps({"format": {"duration": "30"}, "streams": [{"codec_type": "video"}, {"codec_type": "audio"}]})
    with patch("btm_pipeline.media.shutil.which", return_value="/usr/bin/ffprobe"), patch(
        "btm_pipeline.media.subprocess.run", return_value=CompletedProcess([], 0, stdout, "")
    ):
        report = inspect_media(media)
    assert report["passed"] is False
    assert any("outside allowed range" in item for item in report["blockers"])


def test_missing_audio_fails(tmp_path):
    media = tmp_path / "silent.mp4"
    media.write_bytes(b"x")
    stdout = json.dumps({"format": {"duration": "600"}, "streams": [{"codec_type": "video"}]})
    with patch("btm_pipeline.media.shutil.which", return_value="/usr/bin/ffprobe"), patch(
        "btm_pipeline.media.subprocess.run", return_value=CompletedProcess([], 0, stdout, "")
    ):
        report = inspect_media(media)
    assert report["passed"] is False
    assert any("audio stream is missing" in item for item in report["blockers"])


def test_missing_ffprobe_fails_closed(tmp_path):
    media = tmp_path / "video.mp4"
    media.write_bytes(b"x")
    with patch("btm_pipeline.media.shutil.which", return_value=None):
        report = inspect_media(media)
    assert report["passed"] is False
    assert any("not found" in item for item in report["blockers"])
