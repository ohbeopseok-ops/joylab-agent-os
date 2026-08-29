# SPEC — JoyLab Agent OS V0.6.1 Scheduled Ingestion

## Status
IMPLEMENTATION CANDIDATE — PR #16

## Purpose

Execute repeatable domain ingestion without duplicate processing or checkpoint drift.

```text
ScheduleSpec + run_key + now_epoch + signal
          ↓
      due / duplicate checks
          ↓
      AdapterRegistry
          ↓
      ExperienceRecord
          ↓
  RuntimeState checkpoint
          ↓
     atomic persistence
```

## Determinism
The runtime does not read wall-clock time. The caller supplies `now_epoch`.

This makes replay, tests, and Gold Cases deterministic across environments.

## State semantics
A successful ingestion:
- increments RuntimeState.sequence
- updates the domain checkpoint to experience_id
- records the schedule's last success epoch
- records the run_key for duplicate protection
- adds the domain to active_plugins

The following do not mutate persisted state:
- duplicate run
- disabled schedule
- not-due schedule
- adapter failure

## Duplicate protection
run_key history is persisted in RuntimeState metadata and survives restart.
History is bounded to the latest 100 run keys per schedule.

## Governance
- V0.5.3 frozen contracts remain unchanged.
- GOLD_077~083 start as CANDIDATE.
- promotion requires GREEN CI evidence.

## DoD
- GOLD_001~076 remain green
- GOLD_077~083 pass
- Python 3.11/3.12/3.13 green
- Certification Gate green
- final registry GOLD_001~083 CERTIFIED
