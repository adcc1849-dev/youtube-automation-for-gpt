# Local FFmpeg rendering

The optional local renderer assembles still-image segments, one narration audio track, and optionally a background music track into an MP4/MKV/MOV file. It uses a local FFmpeg binary and makes no network calls.

## Render spec

```json
{
  "segments": [
    {"image_path": "assets/shot-01.png", "asset_id": "shot-01", "duration_seconds": 45},
    {"image_path": "assets/shot-02.png", "asset_id": "shot-02", "duration_seconds": 60}
  ],
  "narration_path": "audio/narration.wav",
  "narration_asset_id": "narration-01",
  "music_path": "audio/music.wav",
  "music_asset_id": "music-01"
}
```

Every referenced asset ID must exist in a structurally valid rights ledger. The owner is responsible for ensuring the ledger's human review and permissions are genuine. Output is not overwritten unless the caller explicitly passes `overwrite=True`. The renderer performs a post-render ffprobe check and blocks on failure.

## Limitations

- This is a still-image renderer, not a full nonlinear editor. It does not generate narration, create subtitles, animate graphics, or verify source facts.
- Narration and image/music segment timing must be prepared by the editor. FFmpeg's `-shortest` behavior may trim output to the narration duration.
- A valid rights ledger does not prove a license. Do not render uncleared assets.
- Render success does not authorize public publishing. The public-publish flag is always false.
