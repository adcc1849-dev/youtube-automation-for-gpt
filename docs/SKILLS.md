# 11-skill integration

The repository vendors the MIT-licensed `Jakeschincariol/youtube-agent-skill` source at commit `a2feb2104981a375ffd4f87ee04f4f5344ac43c6`, including all 11 `SKILL.md` files, their bundled helper utilities/resources, and the upstream license/README. The local loader exposes the skill prompts and declares minimum input requirements.

## Skills

- `yt-script`: topic and research packet
- `yt-package`: script
- `yt-edit`: script and asset inventory
- `yt-comment`: actual comments
- `yt-plan`: channel context
- `yt-viral`: topic
- `yt-retention`: transcript or retention data
- `yt-shorts`: source script or video transcript
- `yt-seo`: script and topic
- `yt-chapters`: transcript
- `yt-audit`: actual video or channel data

## Safe use

`available_skills()` returns the catalog. `load_skill(name, available_inputs=...)` refuses to mark a skill ready when required inputs are missing. It returns the upstream `SKILL.md` text only; it does not execute helper scripts. Helper scripts must be separately audited and explicitly integrated before use. No comments, analytics, transcripts, or other unavailable data may be invented.

The Gemini script-draft adapter includes `yt-script` guidance. The generic `btm-run-skill SKILL_NAME INPUTS.json [OUTPUT.json]` CLI can invoke any registered skill when its required inputs are supplied; it is manual and opt-in, requires the same Gemini flags/key, and marks results for human review. No skill is auto-run on a schedule.

## Attribution

Source: [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill), MIT License. See `src/btm_pipeline/skill_assets/LICENSE` and the vendored README for the upstream notice.
