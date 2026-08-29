# ARCHITECTURE — JoyLab Agent OS V0.1

## 1. Architectural principle

JoyLab Agent OS uses **Governed Learning**, not unrestricted autonomous learning.

```text
Task
  -> Execution
  -> Experience Log
  -> Candidate
  -> Evidence
  -> Certification Gate
       | PASS
       v
    CERTIFIED
       |
       +-> next task
       |
       ` FAIL -> TESTING / ARCHIVE
```

## 2. V0.1 components

### SkillRegistry
Source of truth for skill metadata and lifecycle state.

Responsibilities:
- create/register skills
- enforce valid state transitions
- retrieve by skill id
- prevent silent overwrite of certified versions

### ExperienceLogger
Append-only execution evidence.

Responsibilities:
- log result
- preserve timestamp / skill version / metrics
- provide evidence by skill id
- never rewrite historical records

### CertificationGate
Deterministic promotion evaluator.

Default V0.1 gates:
- samples >= 20
- gold_cases >= 10
- confidence >= 80
- OOS pass
- regression pass
- hard_gate_violations == 0

### Gold Cases
pytest fixtures proving:
- valid candidate certifies
- insufficient samples fail
- OOS failure blocks
- regression failure blocks
- hard-gate violation blocks
- certified skill cannot be silently overwritten

## 3. Future layers

```text
Interfaces
  -> Agent Router
  -> Domain Plugins
  -> Skill Runtime
  -> Memory Router
  -> Experience Logger
  -> Skill Evolution Engine
  -> Certification Gate
  -> Registry
```

Domain plugins remain independent:
- Investment
- CS
- Content

## 4. Hermes-derived design patterns

Adopted:
- provider isolation
- deterministic lifecycle transitions
- recoverable archival
- usage metadata
- graph-oriented skill relations
- timeout/failure isolation

Modified:
- autonomous curator -> governed curator
- direct skill mutation -> candidate version proposal
- memory write -> policy-gated write

Rejected:
- automatic mutation of certified production skills
- implicit promotion based only on LLM judgment
