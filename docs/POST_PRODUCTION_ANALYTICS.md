# Post-production analytics (read-only)

The analytics CLI collects YouTube Analytics API video-level rows over explicit trailing 1-day, 7-day, and 28-day windows. It stores versioned JSON snapshots and does not publish, edit metadata, read comments, or change the topic queue. OAuth uses the read-only `yt-analytics.readonly` scope and the same environment variable names used by the uploader. The OAuth refresh token must have been granted the Analytics read-only scope; otherwise the command fails visibly.

```bash
python -m pip install -e ".[publishing]"
python -m btm_pipeline.analytics_cli --end-date 2026-10-28 --output analytics/snapshots/2026-10-28.json
```

Use a completed reporting date; recent metrics can be delayed or incomplete. Preserve each snapshot under a new path. The initial collector uses core video metrics supported by the Analytics API: views, estimated minutes watched, average view duration/percentage, likes, comments, shares, and subscribers gained/lost. Impression/CTR discovery metrics and retention-curve queries are explicitly not yet collected in this first implementation. A diagnosis is a cautious review hint, not a performance grade, causal claim, or virality prediction. Any thresholds are provisional and should be calibrated against comparable channel history.

This is a development integration only until a read-only OAuth grant and real channel query have been tested. No analytics have been collected by this commit, and no next-topic decision is automated yet.
