# TASKS — PR #1

## P0 — Repository foundation
- [x] create `joylab-agent-os`
- [x] Python 3.11+ package
- [x] pytest configuration
- [x] CI workflow

## P0 — Skill Registry
- [x] SkillState enum
- [x] SkillRecord
- [x] SkillRegistry
- [x] lifecycle transition validation
- [x] certified overwrite protection

## P0 — Experience Logger
- [x] ExperienceRecord
- [x] append-only logger
- [x] query by skill id
- [x] count evidence records

## P0 — Certification Gate
- [x] CertificationPolicy
- [x] CertificationEvidence
- [x] CertificationResult
- [x] deterministic reason codes
- [x] pass/fail evaluation

## P0 — Gold Cases
- [x] GOLD_001 valid certification
- [x] GOLD_002 insufficient samples
- [x] GOLD_003 OOS fail
- [x] GOLD_004 regression fail
- [x] GOLD_005 hard gate violation
- [x] GOLD_006 certified overwrite blocked
- [x] GOLD_007 invalid lifecycle jump blocked

## P1 — Follow-up
- [ ] EvidenceBuilder
- [ ] JSON persistence adapter
- [ ] registry schema migration
- [ ] CI standard gate hardening
