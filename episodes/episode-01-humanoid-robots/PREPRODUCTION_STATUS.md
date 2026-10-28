# Episode 01 pre-production status

**As of:** 2026-10-28  
**Decision:** BLOCKED — do not render or publish as a final episode yet.  
**Branch:** `feat/episode-humanoid-research-draft`  
**Pull request:** https://github.com/adcc1849-dev/youtube-automation-for-gpt/pull/15

## Completed in repository

- Topic and editorial angle selected: humanoid robots in factories, separating deployed tasks, pilots, and announced plans.
- Draft script and production brief exist.
- Primary company source wording checked by the assistant and recorded in `SOURCE_AUDIT.md`.
- Script claim IDs are intended to map as R1 Spartanburg operating metrics, R2 reported Spartanburg safety arrangements, R3 Leipzig/AEON pilot, R4 Digit warehouse logistics, and R5 planned GXO expansion.
- Independent context sources added: Stanford HAI AI Index 2026 and the US NIOSH Center for Occupational Robotics Research.
- Asset rights ledger template added.
- Draft remains unmerged; no render or upload was triggered.

## Mandatory gate status

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Topic and structure | PASS — draft scope | Production brief and script are present. |
| Primary-source check | ASSISTANT-CHECKED | `SOURCE_AUDIT.md`; sources are company reports and do not independently audit company metrics. |
| Independent context | ADDED, EDITOR REVIEW PENDING | Stanford HAI AI Index 2026; NIOSH workplace robotics safety context. |
| Claim IDs and tense | NEEDS FINAL CONSISTENCY REVIEW | Confirm R1–R5 labels match between script and research draft. |
| Final narration script | BLOCKED | Script is not owner/editor-approved; factual sentences need a final claim-by-claim review. |
| Visual/audio asset rights | BLOCKED | Ledger is a template; no final asset files or complete license proofs are recorded. |
| Voice model and license | BLOCKED | Exact Piper model/sidecar, license, URLs, hashes, and permitted-use review are not recorded. |
| Final title/description | DRAFT ONLY | Use provisional metadata below; finalize after script approval. |
| Captions | BLOCKED | Captions must be generated from the final narration audio and reviewed against playback. |
| Production configuration | BLOCKED | The expected `config/episode-01.json` is not yet present on this branch; asset paths and rights ledgers must be populated before running. |
| Release manifest / mandatory gates | BLOCKED | Must be populated and run against actual episode assets and technical QC evidence. |
| Publish authorization | DISABLED | No public upload or publishing was attempted. |

## Provisional metadata — not approved for upload

**Title:** How Humanoid Robots Are Learning to Work in Factories

**Description:**

Humanoid robots are moving beyond lab demonstrations into selected factory and warehouse tasks—but what have they actually proved? We examine company-reported work involving Figure 02 at BMW, BMW's AEON pilot in Leipzig, and Agility Robotics' Digit in logistics. We separate completed operations from pilots and future plans, then look at the hard questions around reliability, safety, integration, and cost.

This episode distinguishes company announcements from independent analysis. Operational metrics are attributed to the companies that reported them; a pilot is not proof of general-purpose autonomy, and a planned rollout is not a completed deployment.

Sources and further reading:
- BMW Group: https://www.bmwgroup.com/en/news/general/2026/humanoid-robot-in-leipzig.html
- Figure AI: https://www.figure.ai/news/production-at-bmw
- Agility Robotics / GXO: https://www.agilityrobotics.com/content/gxo-signs-industry-first-multi-year-agreement-with-agility-robotics
- Stanford HAI AI Index 2026: https://hai.stanford.edu/assets/files/ai_index_report_2026_chapter_2_technical.pdf
- US CDC/NIOSH Center for Occupational Robotics Research: https://www.cdc.gov/niosh/centers/robotics.html

Illustrative visuals, if used, will be identified as illustrations rather than documentary footage.

**Language:** English (US)  
**Audience:** General audience interested in AI and future technology  
**Tags (draft):** humanoid robots, industrial robotics, Figure AI, BMW robotics, Agility Robotics, Digit robot, factory automation, warehouse robotics, robotics safety, AI and future of work

## Next actions

1. Review and normalize R1–R5 mapping in the script and research draft.
2. Finalize the narration script with claim references and no stale verification labels.
3. Select actual visuals and record complete asset provenance and rights evidence.
4. Select a voice model and verify its exact license, sidecar, and hashes.
5. Create `config/episode-01.json` using the real cleared assets and ledgers.
6. Run the release-gate validator and address every blocker before dispatching a render.
7. Render in GitHub Actions only after the inputs are complete; inspect the video, audio, captions, and technical report.

**Important:** `source_checked` means the assistant compared wording with sources. It does not mean an owner/editor has approved the claim, nor does it prove the company's metrics independently. Do not change statuses to `verified` merely to satisfy a software gate.
