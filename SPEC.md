# SPEC — JoyLab Agent OS V0.5.3

## Status

**FROZEN CERTIFIED BASELINE**

Frozen commit:
`9e9cb2cfc75aaf6430225c729522c72d1306f71a`

Release anchor:
`release/v0.5.3-frozen`

## Certified release decision

```text
Python 3.11 / 3.12 / 3.13
 + Regression
 + GOLD_001~070 CERTIFIED
 + Gold Provenance
 + JSON Schema
 + EVS Integrity
 + EVG Integrity
 + Approval Audit
        ↓
V05CertificationGate
        ↓
PASS
```

## Required checks

- python_ci
- regression
- gold_contiguous
- gold_provenance
- gold_no_invalid
- gold_certified_minimum >= 70
- schema
- evs
- evg
- audit

Any failed check blocks release.

## Frozen governance

- CERTIFIED skills are immutable in place.
- new Gold Cases start as CANDIDATE.
- promotion requires GREEN evidence.
- historical provenance is append-only.
- release/v0.5.3-frozen must remain anchored to the frozen commit.
- post-freeze feature work starts at V0.6 or later.

## Definition of Done

- GOLD_001~070 CERTIFIED
- Python 3.11 GREEN
- Python 3.12 GREEN
- Python 3.13 GREEN
- V05CertificationGate GREEN
- frozen SHA anchored
- frozen release notes committed
