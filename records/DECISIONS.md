# JoyLab Durable Decisions

This file is append-oriented. Record only decisions that should influence future work across sessions or tools.

## D-2026-09-06-001 — Global baseline repository
Status: LOCKED
Decision: Use `ohbeopseok-ops/joylab-agent-os` as the Source of Truth for reusable JoyLab agent skills and durable non-sensitive operating records.
Reason: Avoid duplicating global behavior across project repositories.

## D-2026-09-06-002 — Cross-agent bootstrap
Status: LOCKED
Decision: New work should load `skills/joylab-core/SKILL.md`, `records/BASELINE.md`, relevant entries in this decision log, and then the target project's local instructions.
Reason: Preserve continuity independent of chat memory or a specific model/tool.

## D-2026-09-06-003 — Five JoyLab pillars
Status: LOCKED
Decision: Default knowledge architecture uses INVEST / AI / WORK / BOOKS / BUILD.
Reason: These pillars cover JoyLab's durable domains while keeping the top-level taxonomy compact.

## D-2026-09-06-004 — JOYLAB 7
Status: LOCKED
Decision: Default editorial/research sequence is HOOK → FACT → WHY → TRANSMISSION → JUDGMENT → SCENARIO → NEXT.
Reason: Separate evidence from interpretation and convert news or observations into reusable knowledge.

## D-2026-09-06-005 — Completion vocabulary
Status: LOCKED
Decision: Use PASS or BLOCKED for execution completion where practical; partially verified work is not complete.
Reason: Reduce ambiguous completion claims and support reliable handoff.

## D-2026-09-06-006 — Privacy boundary
Status: LOCKED
Decision: Do not store secrets, credentials, customer-level data, restricted employer information, health data, or other sensitive personal data in the global baseline repository.
Reason: The baseline is meant to be widely reusable and may be public.
