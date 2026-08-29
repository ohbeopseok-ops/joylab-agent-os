# SPEC — JoyLab Agent OS V0.5.3 Unified Certification Gate

## Status
IMPLEMENTATION CANDIDATE — PR #13

## Purpose

Produce one deterministic release decision from the full trust stack.

```text
Python CI
 + Regression
 + Gold Registry
 + JSON Schema
 + EVS Integrity
 + EVG Integrity
 + Approval Audit
        ↓
V05CertificationGate
        ↓
PASS / FAIL + reason codes
```

## Checks

- python_ci
- regression
- gold_contiguous
- gold_provenance
- gold_no_invalid
- gold_certified_minimum
- schema
- evs
- evg
- audit

Any failed check blocks release.

## Governance bootstrap

PR #13 Gold Cases GOLD_065~070 enter the registry as CANDIDATE.
They may become CERTIFIED only after the first complete CI run is GREEN.
The final PR run then requires all GOLD_001~070 to be CERTIFIED.

## DoD

- existing GOLD_001~064 remain green
- GOLD_065~070 pass
- candidates promoted only after evidence
- final Python 3.11/3.12/3.13 green
- final certification-gate job green
- required certified Gold minimum = 70
