# SPEC — JoyLab Agent OS V0.4.2 EvidenceGraph

## Status

**IMPLEMENTATION CANDIDATE: PR #7**

## 1. Purpose

Make the entire learning and certification lineage queryable.

```text
Core8 Decision
  -> Experience
  -> Evidence Snapshot (EVS)
  -> Skill Candidate
  -> Approval Audit
  -> Certified Skill
```

The graph must answer:
- where did this certified skill come from?
- which decision/experience generated its evidence?
- which EVS supports it?
- which candidate version was reviewed?
- who approved it?
- is any provenance node missing or orphaned?

## 2. Node types

- DECISION
- EXPERIENCE
- EVIDENCE_SNAPSHOT
- SKILL_CANDIDATE
- APPROVAL_AUDIT
- CERTIFIED_SKILL

## 3. Edge types

- PRODUCED
- SEALED_AS
- SUPPORTS
- PROPOSES
- CERTIFIED_AS
- APPROVED_BY
- DERIVED_FROM
- VALIDATED_BY

All edges require both endpoints to exist.
Self-edges and exact duplicate edges are blocked.

## 4. Provenance contract

A strict certified-skill provenance check can require:
- DECISION
- EXPERIENCE
- EVIDENCE_SNAPSHOT
- SKILL_CANDIDATE
- APPROVAL_AUDIT

Missing required node types make provenance incomplete.

## 5. Diagnostics

EvidenceGraph provides:
- lineage path lookup
- orphan node detection
- provenance completeness check
- deterministic edge listing

## 6. Definition of Done

- GOLD_001~034 remain green
- GOLD_035~040 pass
- Python 3.11/3.12/3.13 CI green
- full Core8 Decision -> Certified Skill path is queryable
- missing approval audit is detectable
