# TASKS — PR #18 Persistent Experience / Evidence Store V0.6.3

## Baseline
- [x] V0.6.2 Runtime Orchestration merged
- [x] GOLD_001~092 CERTIFIED
- [x] V0.5.3 frozen baseline untouched

## P0 — Persistent lineage
- [x] PersistentLineageJournal
- [x] append-only JSONL
- [x] SHA-256 chained entries
- [x] monotonic sequence validation
- [x] PersistentExperienceStore
- [x] PersistentEvidenceStore
- [x] EVS integrity verification on recovery
- [x] duplicate Experience ID block across restart
- [x] duplicate EVS ID block
- [x] truncated tail detection
- [x] tamper detection
- [x] deleted-entry/sequence detection
- [x] RuntimeOrchestrator persistent evidence sink
- [x] restart E2E lineage continuation
- [x] JSON Schema

## Gold
- [x] GOLD_093~102 coded as CANDIDATE
- [x] promote only after GREEN CI
- [x] final CI requires GOLD_001~102 CERTIFIED
