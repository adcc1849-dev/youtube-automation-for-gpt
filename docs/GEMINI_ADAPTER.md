# Optional Gemini draft adapter

The provider adapter is disabled by default in local use. It uses Python's standard library and makes no request unless all of the following are explicitly set in the process environment:

- `BTM_ENABLE_CLOUD_AI=1`
- `BTM_GEMINI_FREE_TIER_CONFIRMED=1` after the owner checks the current account terms, model availability, quota, and billing settings
- `GEMINI_API_KEY` containing a valid key

Optional: `GEMINI_MODEL` selects a model ID; default is `gemini-3.6-flash`. Model availability may vary by account/region and can change. A free-tier confirmation flag is a human assertion, not an API guarantee. If the account's free-tier status or billing implications are uncertain, do not enable the adapter.

## Local CLI

```sh
btm-draft-script "How humanoid robots work in factories" research-packet.json script-draft.json
```

The result contains a draft package and a validation report. It never authorizes production, uploads, or publishing.

## Optional GitHub Actions workflow

`.github/workflows/draft-script.yml` is manual-only (`workflow_dispatch`) and does not publish. To use it, the repository owner must first review current Google AI account terms and billing status, then configure a `GEMINI_API_KEY` Actions secret. The workflow requires the repository variable `BTM_GEMINI_FREE_TIER_CONFIRMED=1`; without it, the run stops before calling the provider. Optionally set `GEMINI_MODEL` as a repository variable. The workflow stores only the draft JSON as a short-retention Actions artifact.

This flag does not prove Google will treat the call as free. If cost or quota cannot be confirmed, do not set the variable or run the workflow. The workflow is never scheduled and contains no YouTube upload code. Optional Telegram notifications are off unless the owner sets `BTM_TELEGRAM_NOTIFICATIONS_ENABLED=1` and configures `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` secrets. The notification only says a draft artifact is ready; it is not an approval gate, does not expose the topic, and notification failure does not block the draft.

## Limits

- The adapter sends the supplied topic and research packet to Google; do not include confidential or sensitive material.
- Model output is untrusted draft text and may contain errors or unsupported claims.
- The `yt-script` skill is guidance, not evidence. The validator flags cited claims that are not marked `human_verified`; that status must be set by a human after source review.
- No source browsing, fact-checking, rights clearance, narration, rendering, upload, or public publishing is performed.
