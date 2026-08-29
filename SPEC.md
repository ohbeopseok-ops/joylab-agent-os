# SPEC — JoyLab Agent OS V0.3.1 Core8 E2E

## Status

**IMPLEMENTATION CANDIDATE: PR #4**

## 1. Purpose

Prove that a real investment-domain decision can traverse the governed runtime without bypassing evidence or certification rules.

```text
Core8 Decision
  -> ExperienceRecord
  -> ExperienceLogger
  -> EvidenceBuilder
  -> EvidenceSnapshot
  -> EVS-ID / SHA-256
  -> CertificationGate
  -> Evidence Memory
```

## 2. Core8 boundary contract

The adapter consumes a normalized `Core8Decision`:
- decision_id
- skill_id
- skill_version
- ticker
- action
- confidence
- success
- Gold/OOS/regression/hard-gate flags

It does not import or mutate Core8 internals.

## 3. Governance

A single investment decision must NOT receive fake certification.

With production defaults:
- sample count 1 -> certification FAIL
- evidence snapshot is still sealed
- immutable evidence may still be persisted to EVIDENCE memory

A frozen evidence batch may certify only when the existing CertificationPolicy passes.

## 4. Independence

Core8 source contracts were reviewed from:
- `schemas/master_runtime_v0_1.schema.json`
- `src/master_runtime_v0_1.py`
- `GOLD_CASE_STANDARD_V0.1.md`

JoyLab Agent OS keeps the repositories independent through an adapter boundary.

## 5. Definition of Done

- existing GOLD_001~021 remain green
- GOLD_022~024 pass
- Python 3.11/3.12/3.13 CI green
- single-sample decision does not certify
- hard-gate violations cannot certify
