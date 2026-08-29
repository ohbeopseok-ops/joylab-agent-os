# SPEC — JoyLab Agent OS V0.2

## Status

**IMPLEMENTATION CANDIDATE: V0.2 / PR #2**

## 1. Governed evidence pipeline

```text
ExperienceRecord[]
  -> EvidenceBuilder.build()
  -> EvidenceSnapshot
  -> EvidenceBuilder.to_certification_evidence()
  -> CertificationEvidence
  -> CertificationGate.evaluate()
```

## 2. Evidence Snapshot contract

The snapshot shall be scoped to one exact `skill_id + skill_version`.

Fields:
- skill_id
- skill_version
- samples
- successful_samples
- gold_cases
- confidence
- oos_pass
- regression_pass
- hard_gate_violations
- source_experience_ids

## 3. Deterministic aggregation rules

- `samples`: selected experience count
- `successful_samples`: selected records where success is true
- `gold_cases`: records tagged `gold_case`
- `confidence`: arithmetic mean of available `metrics["confidence"]`; 0.0 when absent
- `oos_pass`: at least one `oos_pass` and no `oos_fail`
- `regression_pass`: at least one `regression_pass` and no `regression_fail`
- `hard_gate_violations`: records tagged `hard_gate_violation`
- evidence from other skill ids or versions must be excluded

## 4. Certification policy

V0.1 gate policy remains unchanged:

```yaml
min_samples: 20
min_gold_cases: 10
min_confidence: 80
require_oos_pass: true
require_regression_pass: true
max_hard_gate_violations: 0
```

## 5. Safety invariants

- source Experience records remain append-only
- EvidenceBuilder does not mutate Experience records
- fail evidence overrides pass markers for OOS and regression
- snapshot preserves source Experience IDs for lineage
- CertificationGate remains deterministic

## 6. Definition of Done — PR #2

PR #2 is complete only when:
- all V0.1 tests continue to pass
- EvidenceBuilder Gold Cases pass
- Python 3.11 / 3.12 / 3.13 CI are green
- no V0.1 certification rule regresses
