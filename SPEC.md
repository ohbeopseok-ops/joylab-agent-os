# SPEC — JoyLab Agent OS V0.6 Persistent Runtime State

## Status
IMPLEMENTATION CANDIDATE — PR #15

## Purpose

Persist non-evidence runtime execution state without changing the frozen V0.5.3 trust contracts.

```text
RuntimeState
  -> canonical JSON
  -> SHA-256
  -> RTS-{20 hex}
  -> atomic JSON write
  -> restart recovery
```

## State scope
- runtime_id
- monotonic sequence/checkpoint marker
- active plugins
- per-domain checkpoints
- non-evidence runtime metadata

## Hard boundary
RuntimeStateStore must not rewrite EVS, EVG, Gold provenance, or Approval Audit history.

## Integrity
- corrupt JSON => block
- hash/id mismatch => block
- missing state => explicit not-found
- negative sequence => block
- successful save uses temp file + fsync + atomic replace

## Governance
GOLD_071~076 enter as CANDIDATE and may be promoted only after CI evidence is GREEN.

## DoD
- GOLD_001~070 remain green
- GOLD_071~076 pass
- Python 3.11/3.12/3.13 green
- certification-gate green
- final registry GOLD_001~076 CERTIFIED
