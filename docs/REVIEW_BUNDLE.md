# Bundle preflight orchestration

`btm-review-bundle PATH_TO_BUNDLE.json` runs the current local validators and returns one JSON report. A bundle contains `research_packet`, `script_package`, `claim_review_packet`, `rights_ledger`, `media_path`, and `release_manifest`.

- `research_packet` is the collector's evidence map; claims must remain `unverified` in this source packet.
- `claim_review_packet` is the separate human-reviewed copy used to validate claim IDs in the script. Claims used by narration must be marked `human_verified` only after a human has checked the cited source.
- `rights_ledger` tracks every asset; all assets must be reviewed and rights must be unambiguous.
- `media_path` points to an existing local render that `ffprobe` can inspect.
- `release_manifest` provides the metadata, claim-evidence ledger, asset ledger, technical report, security report, and policy inputs required by the release gate.

A bundle passes only if every preflight stage and release gate passes. The orchestrator always returns `public_publish_allowed: false`; it has no uploader and cannot activate public publishing.

## Important

This orchestrator does not create a video, verify facts autonomously, fetch sources, grant rights, or run cloud AI. It combines available reports into a conservative review. See the individual workflow documents for each validator's limits.
