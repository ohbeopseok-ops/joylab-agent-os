# TASKS — PR #3 MemoryRouter V0.3

## V0.2 integrity hardening
- [x] Evidence Snapshot JSON Schema
- [x] canonical JSON serialization
- [x] SHA-256 content hash
- [x] deterministic immutable snapshot ID
- [x] tamper verification
- [x] GOLD_014 ~ GOLD_016

## P0 — Memory Router
- [x] MemoryTier enum
- [x] MemoryProvider protocol
- [x] one provider per memory tier
- [x] recall timeout isolation
- [x] provider failure isolation
- [x] context fence sanitation
- [x] governed write dispatch

## P0 — MemoryWritePolicy
- [x] WORKING auto-approval
- [x] OPERATIONAL requires user approval or certified source
- [x] EVIDENCE requires immutable flag + source ref
- [x] failed writes never mutate provider

## P0 — Gold Cases
- [x] GOLD_017 sanitized recall
- [x] GOLD_018 failure isolation
- [x] GOLD_019 timeout isolation
- [x] GOLD_020 operational governance
- [x] GOLD_021 immutable evidence write

## Next
- [ ] persistent provider adapter
- [ ] async background sync
- [ ] memory write audit log
- [ ] Skill Curator V0.4
