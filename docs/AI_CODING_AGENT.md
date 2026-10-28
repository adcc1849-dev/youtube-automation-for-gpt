# AI coding agent (first version)

This repository includes a **manual, draft-PR-only** AI coding agent for development tasks. It runs in GitHub Actions, so it does not require a PC or an always-running Android process.

## Configure Cloudflare Workers AI (recommended first provider)

Cloudflare currently includes **10,000 Neurons per day** in its free Workers AI allocation. The allowance resets at 00:00 UTC; usage above the free allocation requires a paid Workers plan. This is a usage allowance, not a fixed number of coding tasks. Check the dashboard before running larger tasks.

Official references:
- [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)
- [OpenAI-compatible endpoint](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/)
- [Workers AI model catalog](https://developers.cloudflare.com/workers-ai/models/)
- [Create a Workers AI API token](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)

### 1. Create a Cloudflare API token

1. Sign in to the [Cloudflare dashboard](https://dash.cloudflare.com/).
2. Open **Workers AI** and select **Use REST API**.
3. Choose **Create a Workers AI API Token**, review the permissions, create it, and copy the token securely.
4. Copy your **Account ID** from the same page.

If you create a token manually instead of using the template, Cloudflare's Workers AI REST API documentation says it needs **Workers AI – Read** and **Workers AI – Edit** permissions. Treat this token as a secret.

### 2. Add three GitHub repository Actions secrets

Open [this repository's Actions secrets settings](https://github.com/adcc1849-dev/youtube-automation-for-gpt/settings/secrets/actions), select **New repository secret**, and create:

- `AI_API_KEY`: the Cloudflare Workers AI API token you just created.
- `AI_BASE_URL`: `https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/ai/v1` — replace `YOUR_ACCOUNT_ID` with your Cloudflare Account ID. Do not add `/chat/completions` at the end; the agent appends it.
- `AI_MODEL`: `@cf/qwen/qwen3-30b-a3b-fp8`

The selected Qwen model is listed in the official catalog and supports chat completions, reasoning, and function calling. It has a 32,768-token context window. Its model page lists per-token pricing; requests first consume the account's daily free Neurons allocation. Confirm the current quota in Cloudflare's dashboard.

### 3. Test safely

After adding the secrets, open **Actions → AI coding agent (manual, draft PR only) → Run workflow**. Use a small, non-destructive task first, such as:

`Add one focused unit test for an existing pure helper. Do not change publishing, credentials, workflows, dependencies, or production settings.`

Use `feat/v3-end-to-end-production` as the base branch. Inspect the run logs and resulting draft PR. If the API returns an authentication, model, or quota error, do not paste the token into chat or logs; check the secret names, Account ID, model identifier, and Cloudflare dashboard.

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
