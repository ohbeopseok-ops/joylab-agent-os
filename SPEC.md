# SPEC — JoyLab Agent OS V0.6.3 Persistent Experience / Evidence Store

## Status
IMPLEMENTATION CANDIDATE — PR #18

## Purpose

Preserve Experience → Evidence lineage across process restarts without mutating the V0.5.3 frozen trust contracts.

```text
ExperienceRecord
   ↓
PersistentLineageJournal
   ↓
EvidenceBuilder
   ↓
EvidenceSnapshot / EVS
   ↓
same append-only hash chain
```

## Journal contract

Each JSONL entry contains:
- schema_version
- monotonic sequence
- kind: EXPERIENCE or EVIDENCE
- prev_hash
- entry_hash
- payload

Each entry hash covers its sequence, kind, previous hash, and payload.

## Recovery hard blocks

Recovery fails on:
- truncated final line
- malformed JSON
- unsupported schema version
- sequence gap/reordering
- previous-hash mismatch
- entry-hash mismatch
- invalid Experience payload
- EVS integrity failure

## Persistent views

`PersistentExperienceStore` provides the ExperienceLogger-compatible operations required by RuntimeOrchestrator.

`PersistentEvidenceStore` persists verified EVS artifacts and can return the latest artifact per exact skill_id + skill_version.

## Restart E2E

After restart, a second successful orchestration uses all recovered Experiences for the exact skill/version, extends source_experience_ids, seals a new EVS, and persists it into the same lineage journal.

## Concurrency boundary

V0.6.3 is a single-writer journal contract. Multi-process locking/transactions are intentionally deferred.

## Governance

GOLD_093~102 start as CANDIDATE and may become CERTIFIED only after GREEN CI evidence.

## DoD

- GOLD_001~092 remain green
- GOLD_093~102 pass
- Python 3.11/3.12/3.13 green
- Certification Gate green
- final registry GOLD_001~102 CERTIFIED
