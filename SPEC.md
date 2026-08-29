# SPEC — JoyLab Agent OS V0.4.1 Governance Audit

## Status

**IMPLEMENTATION CANDIDATE: PR #6**

## 1. Purpose

Make every proposed skill change reviewable and every approval/rejection attributable.

```text
CERTIFIED Skill
  -> SkillCandidate
  -> CandidateDiffArtifact
  -> Evidence refs
  -> Approval / Rejection
  -> ApprovalAuditRecord
```

The audit layer answers:
- who decided?
- what changed?
- why was it approved/rejected?
- which evidence supported the decision?
- which candidate diff was reviewed?

## 2. Candidate Diff

CandidateDiffBuilder produces:
- diff_id
- candidate_id
- skill_id
- base_version
- proposed_version
- structured changes
- SHA-256

The same base + candidate produces the same diff artifact.

## 3. Approval Audit

ApprovalAuditRecord contains:
- audit_id
- candidate_id
- skill_id
- base_version
- proposed_version
- actor
- decision
- reason
- evidence_refs
- diff_id
- created_at

Approval requires at least one evidence reference.
Rejection may be recorded without evidence refs when the reason itself explains the block.

## 4. Immutability

ApprovalAuditLog is append-only.
Duplicate audit IDs are rejected.

Audit records do not mutate:
- candidate
- base skill
- Evidence Snapshot
- Certification Result

## 5. Definition of Done

- GOLD_001~029 remain green
- GOLD_030~034 pass
- Python 3.11/3.12/3.13 CI green
- approval without evidence is impossible
- duplicate audit entry is blocked
