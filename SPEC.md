# SPEC — JoyLab Agent OS V0.5.2 Gold Registry

## Status
IMPLEMENTATION CANDIDATE — PR #12

## Purpose

Promote Gold Cases from pytest naming convention to governed data.

Each registry entry contains:
- id
- status
- component
- source_test
- provenance.repository
- provenance.pull_request
- provenance.evidence_refs

Allowed states:
- CERTIFIED
- CANDIDATE
- INVALID

Current merged baseline registers GOLD_001 through GOLD_059 as CERTIFIED.

## Invariants
- duplicate IDs are blocked
- unknown statuses are blocked
- current baseline IDs are contiguous
- every case requires provenance
- registry status does not rewrite historical test code

## DoD
- GOLD_001~059 remain green
- GOLD_060~064 pass
- Python 3.11/3.12/3.13 green
