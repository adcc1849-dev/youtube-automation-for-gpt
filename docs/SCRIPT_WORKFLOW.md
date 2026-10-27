# Script package and editorial validation

The script package is a versioned intermediate artifact between research and production. The validator is provider-neutral: it does not call Gemini or another model, and it does not require an API key.

## Package requirements

- Title, intended audience, editorial angle, and language.
- Runtime target between 8 and 12 minutes for the channel's standard long-form format.
- Three or more named sections, each with narration and a list of research claim IDs used in that section.
- A configurable word-count range. Defaults are 1,200–1,800 words, approximately 8–12 minutes at 150 words per minute.
- An editorial status: `draft`, `needs_review`, or `approved`.

When a research packet is supplied, each referenced claim ID must exist and be marked `human_verified` in the review copy. The research collector intentionally starts claims as `unverified`; changing that status is a human editorial action, not a model inference.

## Run

```sh
python -c 'import json; from btm_pipeline.script import validate_script_package; print(json.dumps(validate_script_package(json.load(open("examples/script-package.example.json"))), indent=2))'
```

The example intentionally fails because it contains placeholder narration. Do not treat schema examples as ready content.

## Limits and safety

A pass means structurally reviewable, not factually correct, original, rights-cleared, advertiser-friendly, or ready to upload. A human must review the script against primary/source materials, verify citations, assess copyright and defamation risks, and approve the editorial version. The script validator has no network calls, provider calls, uploads, publishing, or paid dependencies.
