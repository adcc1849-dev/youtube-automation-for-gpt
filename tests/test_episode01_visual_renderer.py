"""Safety and integrity tests for the Episode 01 SVG rasterizer."""
import importlib.util
import json
import sys
import types
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_episode01_visuals.py"


def load_renderer(monkeypatch, tmp_path):
    fake = types.SimpleNamespace(svg2png=lambda **kwargs: Path(kwargs["write_to"]).write_bytes(b"fake-png"))
    monkeypatch.setitem(sys.modules, "cairosvg", fake)
    spec = importlib.util.spec_from_file_location("episode01_renderer", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    asset_dir = tmp_path / "episodes" / "episode-01-humanoid-robots" / "assets"
    asset_dir.mkdir(parents=True)
    for i in range(1, 11):
        (asset_dir / f"vis-{i:03d}.svg").write_text("<svg/>", encoding="utf-8")
    (asset_dir / "thumbnail-draft.svg").write_text("<svg/>", encoding="utf-8")
    module.ROOT = tmp_path
    module.ASSET_DIR = asset_dir
    module.OUTPUTS = [
        *((asset_dir / f"vis-{i:03d}.svg", asset_dir / f"vis-{i:03d}.png", 1920, 1080) for i in range(1, 11)),
        (asset_dir / "thumbnail-draft.svg", asset_dir / "thumbnail-draft.png", 1280, 720),
    ]
    return module, asset_dir


def test_renderer_creates_all_drafts_and_hash_manifest(monkeypatch, tmp_path):
    module, asset_dir = load_renderer(monkeypatch, tmp_path)
    assert module.main() == 0
    report = json.loads((tmp_path / "episodes/episode-01-humanoid-robots/RASTER_OUTPUTS_DRAFT.json").read_text())
    assert len(report["outputs"]) == 11
    assert report["status"] == "RASTER_DRAFTS_CREATED_NOT_CLEARED"
    assert all(len(item["sha256"]) == 64 for item in report["outputs"])
    assert all(item["approved_for_render"] is False for item in report["outputs"])
    assert all(item["rights_status"] == "PENDING_OWNER_REVIEW" for item in report["outputs"])
    assert (asset_dir / "thumbnail-draft.png").is_file()


def test_renderer_preflights_every_output_before_writing(monkeypatch, tmp_path):
    module, asset_dir = load_renderer(monkeypatch, tmp_path)
    blocked = asset_dir / "vis-010.png"
    blocked.write_bytes(b"owner-file")
    try:
        module.main()
    except SystemExit as exc:
        assert "Refusing to overwrite" in str(exc)
    else:
        raise AssertionError("Expected overwrite refusal")
    assert not (asset_dir / "vis-001.png").exists()
    assert blocked.read_bytes() == b"owner-file"


def test_renderer_refuses_existing_report_before_conversion(monkeypatch, tmp_path):
    module, asset_dir = load_renderer(monkeypatch, tmp_path)
    report = tmp_path / "episodes/episode-01-humanoid-robots/RASTER_OUTPUTS_DRAFT.json"
    report.parent.mkdir(parents=True)
    report.write_text("owner report", encoding="utf-8")
    try:
        module.main()
    except SystemExit as exc:
        assert "Refusing to overwrite report" in str(exc)
    else:
        raise AssertionError("Expected report overwrite refusal")
    assert not (asset_dir / "vis-001.png").exists()
