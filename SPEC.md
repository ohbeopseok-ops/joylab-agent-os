# SPEC — JoyLab Agent OS V0.4.3 EvidenceGraph Integrity

## Status

**IMPLEMENTATION CANDIDATE: PR #8**

## 1. Purpose

Seal a complete provenance graph so lineage changes become detectable.

```text
EvidenceGraph
  -> deterministic nodes/edges
  -> canonical JSON
  -> SHA-256
  -> EVG-{first 20 hex chars}
  -> EvidenceGraphSnapshotArtifact
```

## 2. Artifact contract

The graph snapshot contains:
- schema_version
- graph_snapshot_id
- sha256
- nodes
- edges

Snapshot ID format:
`EVG-[0-9a-f]{20}`

## 3. Determinism

Node ordering is by node_id.
Edge ordering is by source_id, target_id, edge_type.

Equivalent graphs must produce identical:
- canonical JSON
- SHA-256
- graph snapshot ID

## 4. Tamper detection

Any change to:
- node ID/type/label
- source/target/edge type
- sha256
- graph snapshot ID

must invalidate verification.

## 5. Definition of Done

- GOLD_001~040 remain green
- GOLD_041~044 pass
- Python 3.11/3.12/3.13 CI green
- graph snapshot JSON Schema committed
- node/edge/hash tampering detected
