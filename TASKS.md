# TASKS — PR #15 Persistent Runtime State V0.6

## Frozen baseline
- [x] V0.5.3 remains anchored at release/v0.5.3-frozen
- [x] V0.6 work occurs only on a new feature branch

## P0 — Runtime state
- [x] RuntimeState model
- [x] RuntimeStateEnvelope
- [x] deterministic RTS ID
- [x] SHA-256 integrity
- [x] atomic temp-write + os.replace
- [x] restart recovery
- [x] corrupt JSON block
- [x] integrity mismatch block
- [x] JSON Schema

## Gold
- [x] GOLD_071~076 coded as CANDIDATE
- [ ] promote only after GREEN CI
- [ ] final CI requires GOLD_001~076 CERTIFIED
