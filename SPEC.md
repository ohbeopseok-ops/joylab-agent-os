# SPEC — JoyLab Agent OS V0.6.4 Crash Consistency / Recovery Reconciliation

## Status
IMPLEMENTATION CANDIDATE — PR #19

## Purpose

Make RuntimeState and the Persistent Lineage Journal recoverable as one logical commit across process crashes.

```text
READY
  ↓
calculate Experience + EVS + next RuntimeState
  ↓
TX_PREPARED
  ↓
EXPERIENCE
  ↓
EVIDENCE
  ↓
RuntimeState atomic save
  ↓
TX_COMMITTED
```

## Write-ahead contract

TX_PREPARED contains enough immutable information to replay the transaction:
- deterministic tx_id
- schedule/domain/run key
- base runtime sequence
- Experience payload
- EVS payload
- complete next RuntimeState payload
- next state ID/hash

TX_COMMITTED proves all logical commit stages completed.

## Recovery

For a PREPARED transaction without COMMITTED:
- missing Experience is appended
- missing EVS is appended
- RuntimeState is advanced only from the expected base sequence, or accepted if already exactly equal to next state
- COMMITTED marker is appended last

Recovery is idempotent.

## Safe automatic recovery

Automatic recovery is allowed only when the prepared transaction proves the exact next state.

The reconciler blocks instead of guessing when:
- state diverges from both base and prepared next state
- state is ahead without a tracked transaction
- checkpoint references an absent Experience
- existing Experience conflicts with prepared payload
- committed state at the same sequence differs from recorded next state
- a COMMITTED marker has no PREPARED record

## Compatibility

Legacy V0.6.3 journals without TX markers remain readable as LEGACY_CONSISTENT if RuntimeState checkpoints are backed by persisted Experiences.

## Governance

GOLD_103~112 start as CANDIDATE and may become CERTIFIED only after GREEN CI evidence.

## DoD

- GOLD_001~102 remain green
- GOLD_103~112 pass
- Python 3.11/3.12/3.13 green
- Certification Gate green
- final registry GOLD_001~112 CERTIFIED
