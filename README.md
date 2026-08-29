# joylab-agent-os

Governed-learning runtime for JoyLab.

## V0.1 Goal

Build the smallest reliable loop that can:

1. register versioned skills,
2. log immutable execution experiences,
3. evaluate skill candidates against certification gates,
4. promote only evidence-backed candidates to `CERTIFIED`.

The V0.1 rule is:

> AI may propose. Evidence must verify. Gates decide. Certified skills never self-modify.

## Core lifecycle

`DISCOVERED -> CANDIDATE -> TESTING -> CERTIFIED -> DEPRECATED`

## PR #1 Scope

PR #1 implements only:

- Skill Registry
- Experience Logger
- Certification Gate
- pytest Gold Cases
- GitHub Actions CI

Out of scope:

- LLM reflection
- autonomous skill mutation
- external memory providers
- web UI
- investment order execution
- cron/scheduler

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
```

## Package layout

```text
src/joylab_agent_os/
  models.py
  skill_registry.py
  experience_logger.py
  certification_gate.py
tests/
  test_gold_cases.py
docs/
  HERMES_MAPPING.md
```

## Governance invariants

- `CERTIFIED` skills are immutable in-place.
- Promotion requires explicit certification evaluation.
- Experience records are append-only.
- Failed gates return machine-readable reasons.
- No financial order execution exists in V0.1.
