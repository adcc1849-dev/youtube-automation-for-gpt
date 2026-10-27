# Asset rights and provenance ledger

Every visual, audio clip, music cue, font, image, footage segment, and externally sourced graphic intended for an episode must have a ledger record before it can pass the asset-rights gate.

## Required workflow

1. Assign a stable, unique `asset_id` and describe the exact asset.
2. Record where it came from and when it was captured.
3. Record the specific license/permission, license URL, and evidence URL. A source page is not automatically proof of reuse rights.
4. Record the intended YouTube use, whether commercial use and modification are allowed, and required attribution.
5. Record a named human reviewer and review date. Re-check the terms when material changes or the rights are time-sensitive.
6. Mark restricted or unclear rights as blocked. Do not include the asset until resolved.
7. Keep the ledger ID associated with the timeline/render manifest so every asset used in the final cut can be traced back.

## Asset kinds

- `original`: created by the production team; identify the creator and retain evidence of authorship/ownership and contributor terms.
- `generated`: identify the generator/model and the date the relevant terms were checked. Confirm the applicable provider terms for the specific account, model, and intended use.
- `third_party`: identify the rights holder and retain the exact license or written permission applicable to the asset.

## Fail-closed rules

The validator blocks missing or duplicate IDs, incomplete provenance, non-HTTPS evidence links, unresolved/unknown licenses, unreviewed records, missing commercial-use or modification permission, missing required attribution, and explicitly restricted/unclear rights. It is a completeness check—not a license lookup, legal opinion, or guarantee that a URL is authentic or that the recorded license applies.

The sample in `examples/asset-rights-ledger.example.json` is schema documentation only; its example.org URLs are placeholders and must never be used as clearance evidence.

## CLI

After installing the package in a Python environment:

```sh
python -c 'import json; from btm_pipeline.rights import validate_asset_rights_ledger; print(json.dumps(validate_asset_rights_ledger(json.load(open("examples/asset-rights-ledger.example.json"))), indent=2))'
```

A passing report means only that the record is structurally complete. Human rights review remains mandatory. This component does not upload, publish, fetch assets, contact providers, or spend money.
