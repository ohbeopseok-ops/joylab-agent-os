# ROADMAP — JoyLab Agent OS

## V0.1 — Governed Core ✅
## V0.2 — Evidence Builder ✅
## V0.3 — Memory Router ✅
## V0.3.1 — Core8 E2E Adapter ✅
## V0.4 — Skill Evolution ✅
## V0.4.1 — Governance Audit ✅
## V0.4.2 — Evidence Graph ✅ FROZEN BASELINE
## V0.4.3 — EvidenceGraph Integrity ✅
## V0.5 — Investment Adapter Expansion ✅
## V0.5.1 — Adapter & Plugin Registry ✅
## V0.5.2 — Gold Registry ✅
## V0.5.3 — Unified Certification Gate ✅ FROZEN CERTIFIED BASELINE

Frozen SHA:
`9e9cb2cfc75aaf6430225c729522c72d1306f71a`

Release anchor:
`release/v0.5.3-frozen`

## V0.6 — Persistent Runtime State ✅
- atomic JSON state persistence
- restart recovery
- runtime state SHA-256 integrity
- immutable RTS snapshot ID
- runtime state JSON Schema
- corruption/integrity hard blocks

## V0.6.1 — Scheduled Ingestion ✅
- deterministic schedule contracts
- caller-supplied now_epoch
- checkpoint-aware ingestion
- duplicate-run protection across restart
- no checkpoint advance on adapter failure
- disabled/not-due no-op semantics

## V0.6.2 — Adapter / Plugin Orchestration 🚧
- enabled-plugin gate
- plugin/schedule domain consistency
- scheduled adapter execution
- append-only Experience logging
- EvidenceSnapshot generation
- EVS sealing on successful execution only
- duplicate/not-due/disabled/failure evidence suppression
- compatibility-preserving orchestration boundary

## V1.0 — JoyLab Personal Agent OS
- unified router
- governed skill evolution
- multi-domain provenance
- multi-interface runtime
