# Beyond the Machine — v3.0

A free-first, hybrid open-source + cloud-AI production system for faceless AI and future-technology documentaries.

## Current status

**Local production runner implemented; real end-to-end production remains unverified.** The repository includes release gates, research and rights ledgers, script validation, opt-in Gemini drafting, all 11 skill prompts with a guarded runner, offline Piper TTS, a local FFmpeg still-image renderer, technical QC, bundle preflight, and a `btm-produce` command that sequences narration → render → media QC. A real sample run still requires locally installed FFmpeg/Piper, a licensed voice model, approved script, cleared assets, and completed rights ledgers.

- Public publishing is **disabled by default**.
- No paid APIs, subscriptions, or spend are enabled.
- Telegram is optional notification plumbing, never a publishing approval gate.
- Mandatory unresolved factual, licensing, technical, metadata, or security checks must block release.
- Public publishing requires successful staged private end-to-end tests and a separate, explicit owner activation.
- A model's confidence is never evidence.

## Quick start

Python 3.11+ is required. Runtime code uses only the Python standard library.

```bash
python -m venv .venv
python -m pip install -e ".[test]"
pytest -q
python -m btm_pipeline.cli examples/demo_manifest.json
```

Validate a research packet with the helper described in [Research workflow](docs/RESEARCH.md).

On Android/Termux, use Termux's available Python and create the virtual environment with `python -m venv .venv`; do not assume Ubuntu's `apt` packages are available.

## Architecture

- [Architecture](docs/ARCHITECTURE.md)
- [Research workflow](docs/RESEARCH.md)
- [Asset rights and provenance](docs/ASSET_RIGHTS.md)
- [Script workflow](docs/SCRIPT_WORKFLOW.md)
- [Optional Gemini draft adapter](docs/GEMINI_ADAPTER.md) (manual-only GitHub Actions workflow)
- [Local media technical inspection](docs/MEDIA_QC.md)
- [Bundle preflight orchestration](docs/REVIEW_BUNDLE.md)
- [Local FFmpeg renderer](docs/LOCAL_RENDER.md)
- [11-skill integration](docs/SKILLS.md)
- [Offline Piper TTS](docs/TTS.md)
- [Complete local production run](docs/LOCAL_PRODUCTION_RUN.md)
- [Publishing policy](config/publishing-policy.json)

## Planned stages

1. Policy and manifest validation.
2. Source-backed research packet and claim-evidence ledger (current milestone).
3. Rights ledger and asset provenance (validator implemented).
4. Script package validation, `btm-draft-script`, and an opt-in Gemini draft adapter (manual-only workflow; provider calls remain disabled by default).
5. Narration and editing/rendering adapters (offline Piper TTS, local still-image FFmpeg renderer, technical inspection, and the `btm-produce` local orchestrator implemented; subtitles/advanced editing remain future work).
6. Bundle-level preflight orchestration across research, script, rights, media, and release gates (implemented), plus guarded manual invocation of all 11 skills.
7. Run and verify an actual local sample production, including playback, synchronization, captions, factual and rights review (not yet completed). No YouTube upload integration is enabled.
8. Public publishing only after safeguards and explicit owner activation.

## Security and ownership

Never commit API keys, bot tokens, OAuth credentials, or personal access tokens. Store future credentials as narrowly scoped GitHub Actions secrets. CI uses read-only repository permissions and does not publish content.

The channel owner controls the budget, policy, and final launch decision. Automation performs authorized production tasks but cannot silently enable public publishing or paid services.
