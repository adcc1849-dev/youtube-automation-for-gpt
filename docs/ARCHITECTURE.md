# Architecture and implementation boundaries

## Operating model

The owner sets the objective, budget, policy, and public-launch decision. The automation performs authorized work and reports evidence. Models are replaceable components, not the source of truth.

## Current foundation

- `src/btm_pipeline/gates.py`: deterministic fail-closed checks over a production manifest.
- `src/btm_pipeline/cli.py`: local/CI manifest validation.
- `config/publishing-policy.json`: default project policy.
- `tests/test_gates.py`: regression tests for blocked releases and policy boundaries.
- `.github/workflows/ci.yml`: tests the Python core with read-only GitHub token permissions.

The demo manifest intentionally fails because its claims and assets are placeholders and no rendered media exists. That is expected.

## Intended pipeline

1. Topic intake and brief.
2. Research packet with source URLs, publication dates, and claim-to-source mapping.
3. Script draft, with each factual claim linked to evidence.
4. Rights ledger for every third-party or generated asset, including source, license terms, proof, attribution, and review state.
5. Narration and render adapter.
6. Automated technical inspection of the actual output file.
7. Metadata and security checks.
8. Private test upload and retrieval verification, without public visibility.
9. Release decision only when all mandatory checks pass.

## Fail-closed rule

A missing field, invalid URL, unresolved rights review, unverified claim, missing technical check, or absent security result blocks release. Passing a data-manifest check does not independently prove that the underlying claim or license is correct. Source inspection, actual media analysis, and where appropriate human review remain necessary.

## Publishing boundary

No YouTube upload integration is implemented in this foundation. Public publishing is disabled in configuration. Any future uploader must enforce policy in code, require successful staged private end-to-end tests, and require a separate explicit owner activation. It must never activate itself from a model response, schedule, Telegram message, or repository permission.

## Cost and credentials

The current core has no runtime dependencies and makes no external API calls. Future providers must be opt-in, free-tier-compatible by default, and disabled when costs cannot be ruled out. Credentials belong in secret storage, never source files or artifacts.

## Agent skills

The planned integration should preserve all 11 skills: `yt-script`, `yt-package`, `yt-edit`, `yt-comment`, `yt-plan`, `yt-viral`, `yt-retention`, `yt-shorts`, `yt-seo`, `yt-chapters`, and `yt-audit`. The adapter must not claim to execute upstream helper utilities unless those utilities are actually present and invoked. Inputs such as comments, transcripts, or analytics must not be invented when unavailable.
