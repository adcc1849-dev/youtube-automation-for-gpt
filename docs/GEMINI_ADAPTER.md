# Optional Gemini draft adapter

The provider adapter is disabled by default. It uses Python's standard library and makes no request unless all of the following are explicitly set in the process environment:

- `BTM_ENABLE_CLOUD_AI=1`
- `BTM_GEMINI_FREE_TIER_CONFIRMED=1` after the owner checks the current account terms, model availability, quota, and billing settings
- `GEMINI_API_KEY` containing a valid key

Optional: `GEMINI_MODEL` selects a model ID; default is `gemini-3.6-flash`. Model availability may vary by account/region and can change. A free-tier confirmation flag is a human assertion, not an API guarantee. If the account's free-tier status or billing implications are uncertain, do not enable the adapter.

## Example

Load a research packet from a local file and call `draft_script(topic, packet)` from Python. The result contains the draft package and a validation report. It never authorizes production, uploads, or publishing. Keep API keys in environment/secret storage; do not commit them or paste them into source files.

## Limits

- The adapter sends the supplied topic and research packet to Google; do not include confidential or sensitive material.
- Model output is untrusted draft text and may contain errors or unsupported claims.
- The validator flags cited claims that are not marked `human_verified`; this status must be set by a human after source review.
- No source browsing, fact-checking, rights clearance, narration, rendering, upload, or public publishing is performed.
- API availability and provider terms are not guaranteed by this repository. The adapter must remain off if the free/approved-cost boundary cannot be confirmed.
