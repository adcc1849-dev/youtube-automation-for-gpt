# Complete local production run

This workflow is **local-only** and does not call Gemini, download assets/models, upload to YouTube, or enable public publishing.

## Prerequisites

- Python 3.11+
- FFmpeg (provides `ffmpeg` and `ffprobe`)
- Piper executable and a locally downloaded voice model whose license/terms you have reviewed
- A script approved for production, local still images, and completed rights records for every asset

## Run

Install the package and tests:

```bash
python -m pip install -e ".[test]"
pytest -q
```

Prepare a JSON config (paths can be absolute or relative to the current working directory). Example shape:

```json
{
  "script_path": "work/script.txt",
  "piper_model_path": "models/en_US-voice-medium.onnx",
  "voice_asset_id": "piper-voice-01",
  "voice_rights_ledger_path": "work/voice-rights.json",
  "production_rights_ledger_path": "work/production-rights.json",
  "narration_asset_id": "generated-narration-01",
  "segments": [
    {"image_path": "assets/scene-01.png", "asset_id": "scene-01", "duration_seconds": 240},
    {"image_path": "assets/scene-02.png", "asset_id": "scene-02", "duration_seconds": 240}
  ],
  "output_path": "out/documentary.mp4",
  "report_path": "out/production-report.json"
}
```

Both rights-ledger files must follow the schema in [ASSET_RIGHTS.md](ASSET_RIGHTS.md). The voice ledger must clear the Piper voice/model. The production ledger must explicitly include every image and a generated narration record with its provenance and applicable model/voice terms. Do not mark rights as cleared unless you have actually checked the source license. The runner intentionally refuses to synthesize until the generated narration has a rights/provenance record in the production ledger; create that record before running based on the intended voice model and generation details.

Then run:

```bash
btm-produce work/production-config.json out/production-report.json
```

The command synthesizes narration, renders a 1080p MP4 from the cleared stills, then checks duration and audio/video streams with ffprobe. The default target is 8–12 minutes. Use segments whose durations add up to that window; narration may be shorter than the visual timeline, so review synchronization and silence manually.

A successful exit means **technical production/QC only**. It does not mean factual claims are verified, copyright is guaranteed, captions are complete, visual quality is acceptable, or the video is ready to upload. Human editorial, factual, rights, accessibility/captions, and playback checks remain mandatory. No upload implementation is included; public publishing is always disabled.
