# Research packet workflow — milestone 2

The research packet is a structured handoff between topic research and script drafting. It records sources and the exact claims they may support.

## Required discipline

- Use the exact source page/document URL, not just a homepage where possible.
- Record publisher, publication date, access date, source type, relevance, and the claim IDs supported.
- Keep each claim in `unverified` state until a reviewer opens the source and confirms that it directly supports the claim.
- Prefer primary sources for key factual claims; use independent sources for corroboration where appropriate.
- Keep uncertainties and open questions visible rather than filling gaps with model-generated assumptions.
- A research source is not a media asset licence. Video, photographs, music, and other assets require their own provenance and reuse-rights review.
- A structurally valid packet is not proof that a source is authentic or that a claim is true.

## Example

Copy `examples/research-packet.example.json`, replace the placeholders with real sources and claims, then run:

```bash
python -c 'import json; from btm_pipeline.research import validate_research_packet; p=json.load(open("my-research.json")); print(json.dumps(validate_research_packet(p), indent=2))'
```

The result is structurally reviewable only if required fields and references are present. It never marks claims verified automatically.

## Next integration

A future research adapter may retrieve official RSS/API data, but must preserve source URLs and dates, impose network/time/size limits, and never convert headlines or snippets alone into verified claims.
