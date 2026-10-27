# Beyond the Machine — v3.0

A free-first, hybrid open-source + cloud-AI production system for faceless AI and future-technology documentaries.

## Current status

**Milestones 1–3 in progress.** The foundation includes deterministic release gates, a structured research packet validator, and a fail-closed asset rights/provenance ledger. This is not yet a complete automated video production system.

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
- [Optional Gemini draft adapter](docs/GEMINI_ADAPTER.md)
- [Publishing policy](config/publishing-policy.json)

## Planned stages

1. Policy and manifest validation.
2. Source-backed research packet and claim-evidence ledger (current milestone).
3. Rights ledger and asset provenance (validator implemented).
4. Script package validation and an opt-in Gemini draft adapter (both implemented; provider calls remain disabled by default).
5. Narration and editing/rendering adapters.
6. Technical, metadata, factual, rights, and security gates.
7. Staged private end-to-end testing.
8. Public publishing only after safeguards and explicit owner activation.

## Security and ownership

Never commit API keys, bot tokens, OAuth credentials, or personal access tokens. Store future credentials as narrowly scoped GitHub Actions secrets. CI uses read-only repository permissions and does not publish content.

The channel owner controls the budget, policy, and final launch decision. Automation performs authorized production tasks but cannot silently enable public publishing or paid services.
