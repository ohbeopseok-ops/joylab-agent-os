# SPEC — JoyLab Agent OS V0.5.1 Adapter & Plugin Registry

## Status
IMPLEMENTATION CANDIDATE — PR #11

## Purpose

Route supported investment-domain signals through one governed registry.

```text
domain + signal
    -> AdapterRegistry
    -> exact signal-type check
    -> domain adapter
    -> ExperienceRecord
```

Supported default domains:
- core8
- ai_power
- nvda_event
- eps_revision
- master_ranking

DomainPluginRegistry separately tracks which plugins are enabled.

## Hard rules
- unknown domain => block
- wrong signal class => block
- duplicate adapter registration => block
- registry does not weaken adapter-level investment hard rules

## DoD
- GOLD_001~052 remain green
- GOLD_053~059 pass
- Python 3.11/3.12/3.13 green
