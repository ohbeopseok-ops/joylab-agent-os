# joylab-agent-os

Governed-learning runtime for JoyLab.

> AI may propose. Evidence must verify. Gates decide. Certified skills never self-modify.

## Current version: V0.6.5

JoyLab Agent OS now implements the governed evidence pipeline:

```text
Experience Log
  -> EvidenceBuilder
  -> Evidence Snapshot
  -> CertificationEvidence
  -> Certification Gate
```

## Core lifecycle

`DISCOVERED -> CANDIDATE -> TESTING -> CERTIFIED -> DEPRECATED`

## Implemented

### V0.1
- Skill Registry
- Experience Logger
- Certification Gate
- pytest Gold Cases
- GitHub Actions CI

### V0.2
- EvidenceSnapshot
- EvidenceBuilder
- skill/version filtering
- sample and Gold Case aggregation
- confidence aggregation
- OOS / regression derivation
- hard-gate violation aggregation
- source experience lineage

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
  evidence_builder.py
  certification_gate.py

tests/
  test_gold_cases.py
  test_evidence_builder.py

docs/
  HERMES_MAPPING.md
```

## Governance invariants

- `CERTIFIED` skills are immutable in-place.
- Promotion requires explicit certification evaluation.
- Experience records are append-only.
- Evidence is scoped to exact skill id + version.
- Failed gates return machine-readable reasons.
- No financial order execution exists in the core runtime.


## Vercel runtime adapter

V0.6.5 adds a thin FastAPI delivery adapter without moving governance logic out of the core runtime.

Endpoints:

- `/` — runtime dashboard
- `/api` — runtime status
- `/api/health` — health check
- `/api/version` — deployed package version
- `/api/capabilities` — governed runtime capabilities
- `/api/certification-policy` — active certification policy
- `/docs` — FastAPI OpenAPI UI

The release gate reruns regression and certification checks, then smoke-tests the deployed Vercel URL.
