# SPEC — JoyLab Agent OS V0.5 Investment Adapters

## Status
**IMPLEMENTATION CANDIDATE: PR #9**

## 1. Purpose

Normalize the main investment engines into the same Agent OS evidence boundary.

```text
AI Power --------┐
NVDA Event ------┤
EPS Revision ----┼-> ExperienceRecord -> Evidence -> EVS/EVG -> Governance
Master Ranking --┘
```

## 2. Source contracts reviewed

From `joylab-core8-engine`:
- `src/joylab_core8/eps_revision.py`
- `NVDA_EVENT_ENGINE_V0.1_MASTER_BUILD_PROMPT.md`
- `docs/investment-analysis/frameworks/MASTER_OPPORTUNITY_RANKING_V0.1.md`
- `docs/investment-analysis/MASTER_RANKING_REGISTRY_V0.1.json`

## 3. Hard invariants

### AI Power
Power constraints may affect semiconductor and power-infrastructure directions differently.
Do not flatten a dual-direction signal.

### NVDA Event
Missing critical evidence remains UNKNOWN.
None is never silently converted to numeric zero.

### EPS Revision
`revision_1m_pct <= -10.0` emits:
- `hard_gate_violation`
- `buy_block`

### Master Ranking
- rank #1 does not equal BUY
- thesis, execution, and portfolio gates must pass
- human approval remains mandatory

## 4. Definition of Done
- GOLD_001~044 remain green
- GOLD_045~052 pass
- Python 3.11/3.12/3.13 CI green
- all four adapters emit normalized ExperienceRecord
