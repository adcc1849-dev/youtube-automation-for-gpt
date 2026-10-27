# YouTube upload integration (staged, fail-closed)

This integration adds a separate upload capability; it does not enable public publishing by itself.

## Release manifest

Create a JSON manifest only after review. All five keys under `release_gates` must be the literal boolean `true`: `factual_evidence`, `asset_rights`, `technical`, `metadata`, and `security`. Also set `human_review_complete: true` and provide `metadata.title`, `metadata.description`, and optional `metadata.tags`. A checkbox or AI confidence is not evidence; the responsible reviewer must verify the evidence behind each gate.

Example structure:

```json
{
  "release_gates": {
    "factual_evidence": true,
    "asset_rights": true,
    "technical": true,
    "metadata": true,
    "security": true
  },
  "human_review_complete": true,
  "metadata": {
    "title": "Episode title",
    "description": "Episode description with source notes",
    "tags": ["AI", "robotics"]
  },
  "category_id": "28",
  "made_for_kids": false,
  "staged_private_end_to_end_tests_passed": false
}
```

## Credentials and run

Install the optional dependencies from `requirements-publishing.txt`. Supply `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN` through the environment or GitHub Actions secrets. The OAuth grant needs the YouTube upload scope. Never put credentials in a manifest, repository file, receipt, or logs.

Run:

```bash
python -m btm_pipeline.publish_cli manifest.json out/episode.mp4 out/upload-receipt.json --visibility private
```

Start with private uploads. Preserve the receipt across retries: the CLI refuses to upload if a receipt already exists, reducing accidental duplicate uploads. If the process is interrupted after YouTube accepts the upload but before a receipt is written, inspect YouTube Studio before retrying; do not assume the first request failed.

The receipt confirms only that the API returned a video ID. It is not yet proof that processing finished, captions and thumbnail are present, or all metadata/visibility match. Those checks remain a required next verification step.

Public visibility is deliberately blocked by `config/publishing-policy.json` unless both `public_publishing_enabled` and `owner_public_activation_authorized` are explicitly set to true and the manifest records successful staged private end-to-end tests. Do not activate public publishing until private test upload and post-upload verification are complete. This integration does not bypass factual, rights, technical, metadata, or security gates.

YouTube Data API quotas and OAuth access can limit uploads. The workflow must fail visibly if authorization or quota is unavailable; no paid service is assumed.
