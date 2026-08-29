# TASKS — PR #2 EvidenceBuilder V0.2

## V0.1 Governed Core
- [x] Skill Registry
- [x] Experience Logger
- [x] Certification Gate
- [x] Gold Cases
- [x] CI matrix

## P0 — Evidence Builder
- [x] EvidenceSnapshot model
- [x] filter evidence by skill id + version
- [x] aggregate sample count
- [x] aggregate Gold Case count
- [x] aggregate confidence
- [x] OOS pass/fail derivation
- [x] regression pass/fail derivation
- [x] hard-gate violation count
- [x] snapshot -> CertificationEvidence conversion

## P0 — Gold Cases
- [x] GOLD_008 valid snapshot certifies
- [x] GOLD_009 other skills/versions excluded
- [x] GOLD_010 OOS failure overrides pass
- [x] GOLD_011 regression failure overrides pass
- [x] GOLD_012 hard-gate violations counted
- [x] GOLD_013 missing confidence defaults to zero

## P1 — Next
- [ ] JSON persistence adapter
- [ ] Evidence Snapshot serialization
- [ ] schema versioning
- [ ] Memory Router V0.3
