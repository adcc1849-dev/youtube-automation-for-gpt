# Post-production analytics (read-only)

The analytics CLI collects YouTube Analytics API video-level rows over explicit trailing 1-day, 7-day, and 28-day windows. It stores versioned JSON snapshots and does not publish, edit metadata, read comments, or change the topic queue. OAuth uses the read-only `yt-analytics.readonly` scope and the same environment variable names used by the uploader. The OAuth refresh token must have been granted the Analytics read-only scope; otherwise the command fails visibly.

```bash
python -m pip install -e ".[publishing]"
python -m btm_pipeline.analytics_cli --end-date 2026-10-28 --output analytics/snapshots/2026-10-28.json
```

Use a completed reporting date; recent metrics can be delayed or incomplete. Preserve each snapshot under a new path. The initial collector uses core video metrics supported by the Analytics API: views, estimated minutes watched, average view duration/percentage, likes, comments, shares, and subscribers gained/lost. Impression/CTR discovery metrics and retention-curve queries are explicitly not yet collected in this first implementation. A diagnosis is a cautious review hint, not a performance grade, causal claim, or virality prediction. Any thresholds are provisional and should be calibrated against comparable channel history.

This is a development integration only until a read-only OAuth grant and real channel query have been tested. No analytics have been collected by this commit, and no next-topic decision is automated yet.


## Next-topic ranking

The `btm-rank-topics` command is a transparent editorial aid. It ranks candidate topics from seven documented 0–5 scores: audience fit, demand evidence, novelty/timing, story strength, evidence quality, visual potential, and production feasibility. Each candidate needs a list of traceable source URLs and a blockers list. Component scores should be backed by research notes, not guessed by a model.

Prepare a JSON list of candidates. Example structure (replace the placeholder URL with a real verified source):

```json
[
  {
    "title": "How warehouse robots handle unpredictable tasks",
    "scores": {
      "audience_fit": 5,
      "demand_evidence": 3,
      "novelty_timing": 4,
      "story_strength": 4,
      "evidence_quality": 4,
      "visual_potential": 5,
      "production_feasibility": 4
    },
    "evidence_sources": ["https://example.org/replace-with-a-verified-source"],
    "blockers": [],
    "analytics_evidence": []
  }
]
```

Run:

```bash
python -m btm_pipeline.topic_queue_cli candidates.json analytics/topic-queue-2026-10-28.json --completed-topics config/completed-topics.json
```

The output is versioned and cannot overwrite an existing path. Candidates with no traceable sources, unresolved blockers, or already-completed titles cannot be selected as the next research topic. Analytics evidence is preserved only when explicitly supplied with provenance; the scorer does not collect analytics, invent demand, or claim causation. A ranked candidate still needs the full research, factual review, and rights-feasibility checks.

## OAuth scope requirement

The same refresh token must have been authorized for `https://www.googleapis.com/auth/youtube.upload`, `https://www.googleapis.com/auth/youtube.readonly`, and `https://www.googleapis.com/auth/yt-analytics.readonly`. A refresh token cannot grant scopes that were not included in the original OAuth consent. Re-authorize if necessary and keep all credentials in GitHub Actions secrets. No live analytics or next-topic selection has been run against the channel yet.
