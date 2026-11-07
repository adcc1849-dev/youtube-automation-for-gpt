# Beyond the Machine — three-stage content operating system

## Purpose

Run the channel as a continuous learning loop, not as a one-off video generator. The operating cycle is:

**Pre-production → Production → Post-production → next pre-production.**

The system is free-first, designed for a faceless US-English AI/future-technology channel, and targets 8–12 minute long-form videos. It must not promise virality: scores are prioritization estimates, not predictions. Public publishing is permitted only after the publishing integration is deliberately enabled and every mandatory release gate passes.

## Stage 1 — Pre-production

### 1. Collect signals
- Collect candidate ideas from reputable current reporting, research releases, company announcements, search suggestions/trends where accessible, and the channel's own YouTube Analytics.
- Record each signal's source URL, retrieval date, publication date, and whether it is a completed event, a company claim, a forecast, or an announced future plan.
- Avoid treating social-media views or a vendor's marketing claim as proof that an idea will succeed.

### 2. Generate and score topics
Generate a candidate list, then score each topic from 0–5 on:
- **Audience fit:** relevance to AI and future technology.
- **Demand evidence:** observable search interest, recent audience questions, or related-video traction.
- **Novelty/timing:** meaningful new development rather than recycled news.
- **Story strength:** a clear question, stakes, conflict, and payoff.
- **Evidence quality:** credible, independently checkable sources.
- **Visual potential:** legal, accessible visuals that can tell the story.
- **Production feasibility:** can the episode be completed with the free-first toolchain?
- **Portfolio value:** adds a useful angle rather than duplicating the last uploads.

Keep raw observations and the weighted score separate. A provisional default weighting is audience fit 20%, demand evidence 20%, novelty/timing 15%, story strength 15%, evidence quality 15%, visual potential 10%, feasibility 5%. The weights are configuration, not a claim of scientific validity. Penalize high uncertainty, weak sources, repeated topics, and missing rights. Never infer "viral" from a score alone.

### 3. Research and script package
- Build a claim/evidence ledger: claim ID, exact proposed claim, source URL, source date, supporting passage/notes, confidence, and verification status.
- Clearly label company-reported numbers and forecasts; seek independent corroboration for consequential claims.
- Draft a 1,200–1,800-word script for an 8–12 minute episode, with a strong opening, clear chapter progression, practical explanation, limitations/counterpoints, and a conclusion.
- Create a title set, thumbnail concept, description, chapters, source list, and captions plan.
- Check originality, factual consistency, title/thumbnail accuracy, audience fit, and asset availability.
- Create a versioned production manifest. Any unresolved mandatory factual or rights issue blocks release, not merely lowers a score.

**Stage exit:** topic chosen, research packet traceable, script package validated, assets/rights plan feasible, and production manifest complete. Topic selection may be automated; fabricated evidence may not.

## Stage 2 — Production to publishing

### 1. Asset and rights intake
For every visual, sound, font, voice, and music asset, record provenance, source URL or generation method, license/terms, attribution requirements, allowed commercial/YouTube use, and file hash where practical. Unknown or incompatible rights block publishing. Prefer original diagrams, self-created visuals, public-domain/appropriately licensed assets, and clearly disclosed AI-generated illustrative scenes. Do not present illustrative AI footage as documentary evidence of a real event.

### 2. Assemble the episode
- Generate narration with a voice whose exact model and usage terms have been checked.
- Build a scene plan with one visual purpose per segment; use legally cleared footage, stills, diagrams, and AI-generated gap-filling visuals.
- Render the 16:9 video, audio mix, captions, chapters, and thumbnail. Keep source assets and render logs reproducible.
- Target 8–12 minutes, but do not pad the runtime to hit a number.

### 3. Quality gates
All mandatory gates must pass:
1. Research claims are verified and accurately represented.
2. Asset, voice, music, font, and visual rights are documented.
3. Video/audio files decode; resolution, duration, frame rate, loudness, and black/silent sections are within configured thresholds.
4. Captions exist and are checked for timing and transcription errors; chapters and metadata are consistent.
5. Thumbnail/title are compelling but not misleading; description contains useful context and sources.
6. Security checks pass; credentials never enter source files, logs, or artifacts.
7. Final bundle preflight passes and stores a machine-readable report.

Automated checks cannot fully judge factual nuance, visual quality, or caption meaning. Where a mandatory check cannot be automated reliably, route it to a documented review state; do not silently mark it passed.

### 4. Publish and verify
- Publishing is a separate, explicitly configured capability. Store YouTube OAuth credentials only as narrowly scoped GitHub Actions secrets; never commit tokens.
- Upload only after the release gate returns pass. If the upload API fails, retry safely without creating duplicate videos; record the upload/session state.
- Set the configured visibility intentionally (initial testing should be private or unlisted). Public publishing should not be enabled until staged private end-to-end upload tests pass and the owner has activated the setting.
- After upload, verify the returned video ID, URL, processing status, thumbnail, captions, metadata, and visibility. If verification fails, stop the next automated publish and alert the owner.
- Keep an audit record linking topic score, research, script version, manifest, render report, upload ID, and timestamps.

**Stage exit:** YouTube reports a successful upload, the video is processed, and post-upload metadata/visibility checks are recorded. A local MP4 or GitHub artifact is not a published video.

## Stage 3 — Post-production and learning

### 1. Gather performance data
Use the YouTube Analytics API when configured and authorized. Collect video-level metrics at comparable windows (for example, 24 hours, 7 days, and 28 days):
- Impressions and impressions click-through rate (CTR).
- Views and unique viewers where available.
- Average view duration and average percentage viewed.
- Audience-retention curve and early drop-off.
- Watch time, traffic sources, search terms where available, subscribers gained/lost.
- Likes, comments, shares, and returning viewers where available.

Record data availability, sample size, time window, video age, traffic mix, and any missing metrics. Do not compare a 24-hour video to a 28-day video as if they were equivalent. Do not treat correlation as proof that one title, thumbnail, or topic caused performance.

### 2. Diagnose, do not just rank
- **Low impressions:** investigate topic demand, packaging relevance, channel size, and timing; low impressions alone do not prove a bad video.
- **Impressions but weak CTR:** test whether title and thumbnail clearly communicate one specific promise. Change one major packaging variable at a time where feasible.
- **Good CTR but weak retention:** compare the opening promise with the actual first 30–60 seconds; check pacing, clarity, narration, and visual relevance.
- **Good retention but limited reach:** inspect traffic sources, search demand, topic breadth, and sample size before deciding the content failed.
- **Strong watch time/retention and positive audience signals:** identify the repeatable topic/format elements, then produce a related but non-duplicative follow-up.

Use channel baselines and comparable cohorts, not universal CTR/retention thresholds. No single metric is a virality guarantee.

### 3. Comments and audience questions
Classify comments into questions, corrections, requests, praise, criticism, and spam. Use them as topic signals, not as verified facts. Never expose personal information; ignore spam and do not auto-argue with viewers. Feed recurring questions and corrections into the research queue.

### 4. Choose the next topic
Update the candidate scores using actual channel performance, with safeguards against overfitting to one outlier. Prioritize:
- repeatable audience interest,
- unanswered questions from the previous episode,
- new evidence or developments,
- follow-up angles with stronger sources,
- and variety across the channel's topic portfolio.

Maintain an experiment log for title/thumbnail changes and publication timing. Do not claim an experiment is conclusive without enough data. Carry corrections and failed assumptions into the next research packet.

**Stage exit:** analytics snapshot saved, performance diagnosis written, lessons added to the topic scorer, and a ranked next-topic queue created.

## Continuous operating loop

`topic_queue → research_packet → script_package → rights_and_asset_manifest → render_bundle → release_gate → upload → upload_verification → analytics_snapshot → performance_review → topic_queue`

Each transition writes versioned artifacts and an auditable status. Failed stages stop the chain and create a retryable task with a clear reason. A failure must never be converted to success just to keep the schedule.

## Current implementation boundary

This document defines the target operating design. It does **not** claim that every stage is already implemented. The existing repository has research/script/rights/production validation and a manual cloud-render workflow, but the real end-to-end render and YouTube upload path still require verification/integration. Analytics ingestion, metric normalization, topic scoring based on channel analytics, and automated next-topic selection must each be implemented and tested before being described as operational.

## Free-first operating rules

- No paid API or subscription is assumed.
- Use official APIs within their free/authorized quotas; fail visibly when quotas or permissions are unavailable.
- Never scrape or bypass access controls where terms prohibit it.
- Do not claim a topic will go viral or fabricate analytics.
- Keep public publishing disabled until the upload path has passed staged tests and explicit owner activation.
