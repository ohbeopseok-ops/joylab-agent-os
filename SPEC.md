# SPEC — JoyLab Agent OS V0.1

## Status

**FROZEN CANDIDATE: V0.1 / PR #1**

## 1. Functional requirements

### FR-001 Skill registration
The system shall register a `SkillRecord` with:
- skill_id
- name
- domain
- version
- state
- created_at
- metadata

### FR-002 Valid lifecycle
Allowed transitions:
- DISCOVERED -> CANDIDATE
- CANDIDATE -> TESTING
- TESTING -> CERTIFIED
- CERTIFIED -> DEPRECATED
- TESTING -> DEPRECATED

No transition may bypass `TESTING` into `CERTIFIED`.

### FR-003 Append-only experience
ExperienceLogger shall append immutable `ExperienceRecord` entries.

### FR-004 Evidence aggregation
Certification evidence shall include:
- samples
- gold_cases
- confidence
- oos_pass
- regression_pass
- hard_gate_violations

### FR-005 Deterministic gate
The same evidence and policy shall always return the same result.

### FR-006 Explainable rejection
A failed certification shall contain reason codes.

### FR-007 Certified immutability
A certified skill may not be replaced in-place.
A changed implementation requires a new version and a new certification cycle.

## 2. Non-functional requirements

- Python >= 3.11
- no external runtime dependency in V0.1
- unit tests deterministic
- JSON-serializable records
- UTC timestamps
- domain-neutral core
- no network requirement for tests

## 3. Certification policy V0.1

```yaml
min_samples: 20
min_gold_cases: 10
min_confidence: 80
require_oos_pass: true
require_regression_pass: true
max_hard_gate_violations: 0
```

## 4. Result model

```json
{
  "passed": false,
  "reasons": ["INSUFFICIENT_SAMPLES"],
  "evaluated_policy": "V0.1"
}
```

## 5. Definition of Done — PR #1

PR #1 is complete only when:
- package imports cleanly
- all Gold Cases pass
- lifecycle guard is tested
- certified overwrite guard is tested
- certification output is deterministic
- README quickstart works
- GitHub Actions CI is green
