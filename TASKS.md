# TASKS — PR #16 Scheduled Ingestion V0.6.1

## V0.6 runtime foundation
- [x] persistent RuntimeState
- [x] restart recovery
- [x] GOLD_071~076 CERTIFIED
- [x] PR #15 merged

## P0 — Scheduled ingestion
- [x] ScheduleSpec
- [x] deterministic now_epoch input
- [x] interval due check
- [x] checkpoint-aware execution
- [x] duplicate-run protection across restart
- [x] adapter routing
- [x] adapter failure leaves state unchanged
- [x] disabled schedule no-op
- [x] not-due no-op
- [x] successful run increments runtime sequence
- [x] bounded run history

## Gold
- [x] GOLD_077~083 coded as CANDIDATE
- [x] promote only after GREEN CI
- [x] final CI requires GOLD_001~083 CERTIFIED
