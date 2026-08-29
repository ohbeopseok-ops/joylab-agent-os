# SPEC — JoyLab Agent OS V0.3

## Status

**IMPLEMENTATION CANDIDATE: V0.3 / PR #3**

## 1. Evidence integrity

Evidence snapshots are sealed as immutable artifacts.

```text
EvidenceSnapshot
  -> canonical JSON
  -> SHA-256
  -> EVS-{first 20 hex chars}
  -> EvidenceSnapshotArtifact
```

The artifact contains:
- schema_version
- snapshot_id
- sha256
- snapshot payload

Any payload/hash/id mismatch must fail verification.

## 2. Memory architecture

```text
MemoryRouter
  ├─ WORKING provider
  ├─ OPERATIONAL provider
  └─ EVIDENCE provider
```

Only one provider may be registered per tier in V0.3.

## 3. Recall contract

- provider recall is timeout-bounded
- one provider failure must not block other tiers
- memory context fence tags are stripped before injection
- empty/failed providers are skipped

## 4. Write governance

### WORKING
May be auto-approved because it is ephemeral.

### OPERATIONAL
Requires at least one:
- explicit user approval
- certified source

### EVIDENCE
Requires both:
- immutable = true
- non-empty source_ref

A denied write must not reach the provider.

## 5. Hermes-derived patterns

Adopted:
- provider routing
- timeout/failure isolation
- context sanitation
- bounded provider surface

Modified:
- Hermes sync/write behavior -> policy-gated write
- external provider model -> one provider per memory tier

Rejected:
- uncontrolled operational memory mutation

## 6. Definition of Done — PR #3

PR #3 is complete only when:
- all V0.1/V0.2 tests remain green
- snapshot tamper tests pass
- memory failure/timeout isolation tests pass
- write governance tests pass
- Python 3.11 / 3.12 / 3.13 CI are green
