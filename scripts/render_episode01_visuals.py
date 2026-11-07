#!/usr/bin/env python3
"""Convert Episode 01 original SVG draft visuals to PNG and record output hashes.

Install the optional dependency with: pip install -e ".[visuals]"
This utility does not grant rights clearance or approve assets for publication.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    import cairosvg
except ImportError as exc:  # pragma: no cover - exercised by CLI users
    raise SystemExit('Missing optional dependency. Install with: pip install -e ".[visuals]"') from exc

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "episodes/episode-01-humanoid-robots/assets"
OUTPUTS = [
    *((ASSET_DIR / f"vis-{i:03d}.svg", ASSET_DIR / f"vis-{i:03d}.png", 1920, 1080) for i in range(1, 11)),
    (ASSET_DIR / "thumbnail-draft.svg", ASSET_DIR / "thumbnail-draft.png", 1280, 720),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    records = []
    for source, target, width, height in OUTPUTS:
        if not source.is_file():
            raise SystemExit(f"Missing SVG source: {source}")
        if target.exists():
            raise SystemExit(f"Refusing to overwrite existing output: {target}")
        cairosvg.svg2png(url=str(source), write_to=str(target), output_width=width, output_height=height)
        records.append({
            "source": str(source.relative_to(ROOT)),
            "output": str(target.relative_to(ROOT)),
            "width": width,
            "height": height,
            "sha256": sha256(target),
            "rights_status": "PENDING_OWNER_REVIEW",
            "approved_for_render": False,
        })
    report = {
        "episode_id": "episode-01-humanoid-robots",
        "status": "RASTER_DRAFTS_CREATED_NOT_CLEARED",
        "outputs": records,
        "notice": "Hashes identify these generated PNG files only. They do not establish ownership, license applicability, factual approval, or publication clearance.",
    }
    report_path = ASSET_DIR.parent / "RASTER_OUTPUTS_DRAFT.json"
    if report_path.exists():
        raise SystemExit(f"Refusing to overwrite existing report: {report_path}")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(records)} PNG drafts and {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
