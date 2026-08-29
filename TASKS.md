# TASKS — PR #17 Runtime Orchestration V0.6.2

## Runtime foundation
- [x] V0.6 Persistent Runtime State merged
- [x] V0.6.1 Scheduled Ingestion merged
- [x] GOLD_001~083 CERTIFIED

## P0 — Runtime Orchestrator
- [x] DomainPluginRegistry gate
- [x] disabled plugin block
- [x] plugin/schedule domain consistency check
- [x] ScheduledIngestionRunner integration
- [x] AdapterRegistry integration
- [x] ExperienceLogger append on success only
- [x] EvidenceBuilder integration
- [x] EVS sealing on success only
- [x] duplicate/no-due no-evidence semantics
- [x] adapter failure no-state/no-evidence semantics
- [x] duplicate experience ID cannot advance runtime state
- [x] duplicate schedule does not re-call adapter
- [x] public current_state API

## Gold
- [x] GOLD_084~092 coded as CANDIDATE
- [ ] promote only after GREEN CI
- [ ] final CI requires GOLD_001~092 CERTIFIED
