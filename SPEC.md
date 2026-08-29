# SPEC — JoyLab Agent OS V0.6.2 Runtime Orchestration

## Status
IMPLEMENTATION CANDIDATE — PR #17

## Purpose

Provide one governed runtime path for enabled domain plugins.

```text
DomainPluginRegistry
      ↓ enabled + domain match
ScheduleSpec
      ↓ due + unique run
AdapterRegistry
      ↓
ExperienceRecord
      ↓
RuntimeState checkpoint
      ↓
ExperienceLogger
      ↓
EvidenceBuilder
      ↓
EvidenceSnapshot
      ↓
EVS seal
```

## Hard rules

- disabled plugin => no execution, no persisted state, no evidence
- plugin/schedule domain mismatch => block
- duplicate => no new experience or evidence
- not due => no new experience or evidence
- adapter failure => no persisted state, no experience, no evidence
- duplicate experience ID => block before runtime commit
- duplicate/not-due schedule => adapter is not called
- only EXECUTED results may enter evidence lineage

## Evidence semantics

A successful orchestration builds evidence from the append-only experience set for the exact skill_id + skill_version and seals the resulting snapshot as an EVS artifact.

## Frozen boundary

V0.5.3 contracts for Gold, EVS, EVG, approval audit, and certification semantics are not rewritten.

## Governance

GOLD_084~092 start as CANDIDATE and may become CERTIFIED only after GREEN CI evidence.

## DoD

- GOLD_001~083 remain green
- GOLD_084~092 pass
- Python 3.11/3.12/3.13 green
- Certification Gate green
- final registry GOLD_001~092 CERTIFIED
