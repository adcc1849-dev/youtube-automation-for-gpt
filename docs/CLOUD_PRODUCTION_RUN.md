# Cloud production runner (GitHub Actions)

This is a **manual, non-publishing** cloud render workflow. It uses a GitHub-hosted Ubuntu runner, FFmpeg, Piper TTS, and the repository's fail-closed production/QC pipeline. It does not publish to YouTube or call paid services.

## Before dispatching

1. Commit an episode-specific JSON config, script, still images, and complete rights ledgers to the branch you intend to run. Do not use the example rights ledger or placeholder URLs as clearance evidence.
2. Make sure the config points to repository-relative script, image assets, voice rights ledger, and production rights ledger. The workflow overrides only the model path, output path, and report path for the runner. All referenced script/images/ledgers must exist in the checkout.
3. Choose a Piper `.onnx` model and its matching `.onnx.json` sidecar. Review the exact model/voice terms for the intended YouTube use and ensure the voice rights ledger records the same model and license evidence.
4. Obtain the SHA-256 digest of both exact files from a trusted source or calculate it yourself. The workflow refuses a file if either digest differs. Do not rely on a URL alone as proof of licensing.
5. In the rights-ledger record matching `voice_asset_id`, record `model_sha256` and `sidecar_sha256` for those exact files. The workflow checks that the entered digests match both downloaded files and the reviewed voice record. These digest fields bind the selected files to the record; they do not independently prove that the license is valid.

## Run it

1. Open **Actions → Cloud video production (manual, no publishing)**.
2. Choose **Run workflow** and select the branch containing your config/assets.
3. Enter the repository-relative config path, HTTPS URLs for the voice model and matching sidecar, and both SHA-256 digests.
4. Set **voice_license_reviewed** to **yes** only after you have personally checked the applicable terms. This is an explicit attestation, not an automatic legal verification.
5. Start the run. If rendering/QC succeeds, download the artifact named `beyond-the-machine-production-<run-id>` from the completed workflow. Artifacts are retained for 7 days.

## Safety and limitations

- A successful run means technical rendering/QC passed; it does not certify factual accuracy, caption completeness, visual quality, synchronization, or rights. Complete the human review before any publishing decision.
- Failed checks stop the production job and the report is uploaded when available.
- The model and sidecar are downloaded only during the manual run, over HTTPS, and verified against user-supplied SHA-256 digests. Use only trusted model URLs and independently verified hashes.
- Keep the script, assets, and rights ledgers in a private branch/repository if they contain unpublished material. GitHub Actions artifacts are accessible according to repository permissions.
- This workflow has read-only repository permissions and no YouTube credentials. It does not publish, schedule, or enable public publishing.
- GitHub-hosted runner quotas and execution time limits apply. No paid service is configured by this workflow; check your GitHub plan's Actions limits before repeated large runs.
