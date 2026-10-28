# AI coding agent (first version)

This repository includes a **manual, draft-PR-only** AI coding agent for development tasks. It runs in GitHub Actions, so it does not require a PC or an always-running Android process.

## Configure the provider

In the repository, open **Settings → Secrets and variables → Actions → New repository secret** and create these three secrets:

- `AI_API_KEY`: the provider API key.
- `AI_BASE_URL`: HTTPS API base URL for an OpenAI-compatible chat-completions endpoint, normally ending in `/v1` (do not include the API key).
- `AI_MODEL`: the exact model identifier supported by that endpoint.

Do not paste API keys into issues, workflow inputs, source files, or chat. The workflow fails closed if any secret is missing. Provider quotas and model compatibility vary; this code does not assume that a local phone-only endpoint is reachable from GitHub's cloud runner.

## Run a task from your phone

1. Open **Actions → AI coding agent (manual, draft PR only)**.
2. Tap **Run workflow**.
3. Enter one specific engineering task, for example: `Add unit tests for the research packet validator's malformed-input handling without changing publishing safeguards.`
4. Keep the base branch set to `feat/v3-end-to-end-production` unless you intentionally want to target another existing development branch.
5. Start the workflow and monitor its logs. It creates a separate `agent/task-<run-id>` branch and attempts to open a draft PR.
6. Inspect the diff and test result before merging. A failed test run may still produce a draft PR for diagnosis.

## Safety boundaries in v1

- Manual trigger only; no scheduled loop and no autonomous background service.
- At most four complete file replacements per run.
- The model can change only `src/`, `tests/`, `docs/`, `config/`, `examples/`, and `README.md`; workflow files and publishing controls are excluded.
- Generated code is not imported or executed in the same step that holds the model API key. Tests run in a later step without the model API key.
- Every run uses a separate branch and a draft PR; no auto-merge, YouTube upload, or publishing activation.
- Review changes carefully. AI output is untrusted, and the allowlist is a guardrail—not a substitute for review.
- GitHub Actions free usage and the selected model's free quota may be limited. This is a task-triggered worker, not guaranteed 24/7 execution.

## Current limitation

Version 1 is a bounded single-task implementation pass. It does not yet autonomously retry after test failures, maintain a multi-task queue, or decide to start another task. Those should be added only after the first end-to-end run works with the selected provider.
