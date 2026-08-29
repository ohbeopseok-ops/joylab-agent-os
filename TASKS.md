# TASKS — PR #19 Crash Consistency / Recovery Reconciliation V0.6.4

## Baseline
- [x] V0.6.3 Persistent Experience / Evidence Store merged
- [x] GOLD_001~102 CERTIFIED
- [x] V0.5.3 frozen baseline untouched

## P0 — Crash consistency
- [x] TX_PREPARED lineage marker
- [x] TX_COMMITTED lineage marker
- [x] deterministic RTX transaction ID
- [x] prepared payload carries Experience / EVS / next RuntimeState
- [x] RuntimeState payload recovery helper
- [x] deterministic prepare_next_state API
- [x] RecoveryReconciler
- [x] crash after PREPARED recovery
- [x] crash after Experience recovery
- [x] crash after Evidence recovery
- [x] crash after RuntimeState recovery
- [x] idempotent reconciliation
- [x] lineage-ahead RuntimeState restoration
- [x] untracked state-ahead hard block
- [x] conflicting Experience hard block
- [x] RuntimeOrchestrator crash-safe commit path

## Gold
- [x] GOLD_103~112 coded as CANDIDATE
- [ ] promote only after GREEN CI
- [ ] final CI requires GOLD_001~112 CERTIFIED
