# AGENTS.md — JoyLab Notes

## Bootstrap
1. Read global baseline from `ohbeopseok-ops/joylab-agent-os`:
   - `AGENTS.md`
   - `skills/joylab-core/SKILL.md`
   - `records/BASELINE.md`
   - `records/DECISIONS.md`
   - `docs/JOYLAB7_QUALITY_GATE_V1.md`
   - `schemas/joylab7.article.schema.json`
2. Read local `SPEC.md`, `ROADMAP.md`, `TASKS.md`.
3. Do not override local hard rules with generic assumptions.

## Working Rules
- Use small vertical slices.
- No hidden fallback values.
- Preserve existing behavior unless the task explicitly changes it.
- Every meaningful change must include validation evidence.
- Status is PASS or BLOCKED.
- Content cannot become PUBLISHED unless JOYLAB 7 score >=85 and all Hard Gates pass.

## Content Pillars
INVEST / AI / WORK / BOOKS / BUILD

## Build Sequence
SPEC -> PLAN -> IMPLEMENT -> TYPECHECK -> LINT -> TEST -> BUILD -> REVIEW -> REGRESSION -> DOCS -> RELEASE GATE

## Security
Never commit customer PII, credentials, restricted corporate data, or private sensitive records.
