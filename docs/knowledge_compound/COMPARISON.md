# Grok Bot vs Prime Agent vs JoyLab Agent OS

## Decision frame
Compare six axes: Memory, Skill, Routine, Evidence, Recovery, Certification.

| Axis | Grok Bot pattern | Prime Agent pattern | JoyLab target | Decision |
|---|---|---|---|---|
| Memory | persistent computer/files/session | continual memory + reusable notes | canonical structured memory + local wiki | ADOPT concept, keep provider-neutral |
| Skill | user-created/agent-authored procedures | skill creator/refine loop | candidate -> regression -> certification -> promotion | ADOPT with governance |
| Routine | recurring background jobs | repeated agent workflows | scheduler with auditable run records | ADOPT |
| Evidence | source/file context, lighter formal lineage | learning from execution | claim-to-source lineage + hashes | STRENGTHEN |
| Recovery | persistent environment reduces restart cost | self-improvement harness | explicit crash/replay/reconciliation | KEEP JoyLab approach |
| Certification | not the primary control plane | refine/self-improve emphasis | deterministic hard gate + gold cases | REJECT autonomous promotion |

## What to take
1. Persistent dedicated workspace.
2. Raw -> wiki separation.
3. Reusable skills as first-class artifacts.
4. Scheduled ingestion and review.
5. Long-running background routines.
6. Continual lesson capture from repeated work.

## What to modify
1. Memory writes become policy-gated writes.
2. Skill creation becomes SkillCandidate creation.
3. Self-refinement must produce a diff and evidence bundle.
4. Nightly jobs must be idempotent and replayable.
5. Wiki pages must carry source fingerprints and verification state.

## What to reject
1. Automatic mutation of certified production skills.
2. LLM-only truth judgment.
3. Memory without source lineage.
4. Provider-specific canonical memory.
5. Silent overwrite of prior decisions or evidence.

## JoyLab competitive position
JoyLab should not compete on 'agent remembers more'. The defensible design is 'agent can prove why it remembers, what changed, and whether the learned behavior passed regression'.

## Promotion lifecycle
```text
RAW
 -> NORMALIZED
 -> CLAIMED
 -> VERIFIED_KNOWLEDGE
 -> LESSON_CANDIDATE
 -> REGRESSION_PASS
 -> CERTIFIED_SKILL
```

Any failure keeps the artifact in its prior auditable state.
