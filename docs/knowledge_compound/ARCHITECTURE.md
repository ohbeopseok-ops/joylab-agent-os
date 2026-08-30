# JoyLab Knowledge Compound Engine V0.1 — Architecture

## Goal
Build a governed persistent knowledge layer for JoyLab Agent OS. The system must compound useful knowledge without compounding unverified errors.

## Core principle
Model is a replaceable worker. JoyLab's durable asset is Knowledge + Evidence + Skill + Decision + History.

```text
INPUT
  -> INGEST
  -> NORMALIZE
  -> DEDUPLICATE
  -> CLAIM EXTRACTION
  -> EVIDENCE LINK
  -> VERIFICATION GATE
  -> WIKI PROMOTION
  -> LESSON CANDIDATE
  -> REGRESSION
  -> CERTIFICATION
  -> SKILL PROMOTION
```

## Runtime layers
1. Intake Layer: article, PDF, YouTube transcript, screenshot, note, bookmark.
2. Raw Vault: immutable source copy + content hash.
3. Knowledge Layer: normalized markdown pages and topic links.
4. Evidence Registry: source, claim, citation, confidence, verification state.
5. Decision Journal: decision, assumptions, evidence ids, outcome.
6. Skill Registry: reusable procedures generated only from certified lessons.
7. Routine Scheduler: recurring ingestion and review jobs.
8. Certification Engine: deterministic gates before production skill promotion.

## Storage split
- Obsidian: human-readable knowledge workspace and local-first editing.
- Supabase/Postgres: canonical structured registry, lineage, status, metrics.
- GitHub: versioned schemas, skills, rules, migrations, tests and audit trail.

## Folder contract
```text
JoyLab_Brain/
  00_INBOX/
  01_RAW/{articles,pdf,youtube,images,notes}/
  02_KNOWLEDGE/{investment,ai,cs,leadership,projects}/
  03_EVIDENCE/
  04_SKILLS/
  05_ROUTINES/
  06_PROJECTS/
  07_DECISIONS/
  99_ARCHIVE/
```

## Hard gates
A knowledge page cannot become VERIFIED when any of the following is true:
- no source URI or source fingerprint
- no extracted claim
- confidence below configured threshold
- conflicting evidence remains unresolved
- source date is required but missing
- PII/security policy violation

A lesson cannot become a CERTIFIED_SKILL when any of the following is true:
- regression test failed
- gold case coverage below threshold
- hard gate violation > 0
- no evidence lineage to verified knowledge

## Failure philosophy
Fail closed for promotion, fail open for collection. Raw intake may continue when verification fails, but promotion to verified knowledge or certified skill is blocked.

## Model routing
The orchestrator is provider-neutral. Workers are selected by capability and cost. No provider may own canonical memory.

## Nightly cycle
```text
collect bookmarks/inbox
 -> fingerprint + dedupe
 -> parse and normalize
 -> extract claims
 -> cross-check evidence
 -> promote PASS items to wiki
 -> create lesson candidates
 -> run regression/gold cases
 -> promote only certified skills
 -> emit audit summary
```

## Definition of Done V0.1
- deterministic source fingerprinting
- immutable raw record
- claim/evidence lineage
- verification gate
- Obsidian page renderer
- Supabase migration
- nightly routine plan
- unit tests for PASS/BLOCK behavior
