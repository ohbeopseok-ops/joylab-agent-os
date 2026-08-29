# SPEC — JoyLab Agent OS V0.4 Skill Evolution

## Status

**IMPLEMENTATION CANDIDATE: PR #5**

## 1. Principle

The system may propose improvements, but a CERTIFIED skill is never edited in place.

```text
CERTIFIED v1.0.0
   -> improvement proposal
   -> SkillCandidate v1.0.1
   -> register DISCOVERED
   -> transition CANDIDATE
   -> future evidence/testing/certification
```

The original CERTIFIED version remains unchanged.

## 2. SkillCandidateGenerator

Inputs:
- base SkillRecord
- rationale
- change summary
- optional proposed version

Outputs:
- deterministic candidate_id
- base version
- proposed version
- rationale
- change summary

Default version behavior is patch bump.

## 3. SkillCurator

Inspired by Hermes Curator but restricted to governance-safe actions.

It may:
- KEEP
- REVIEW
- PROPOSE_DEPRECATE
- propose a new candidate version
- submit that new candidate version

It may not:
- patch a CERTIFIED record in place
- silently deprecate a CERTIFIED record
- weaken certification rules
- bypass candidate/testing gates

## 4. Activity policy

Default thresholds:
- stale_after_days = 30
- archive_after_days = 90
- pinned skills bypass activity recommendations

At archive threshold the curator emits a recommendation only.

## 5. Hermes mapping

Adopted:
- lifecycle maintenance concept
- stale/archive thresholds
- pinned protection
- background-review-ready design

Modified:
- automatic patch -> versioned candidate proposal
- automatic archive -> deprecation recommendation

Rejected:
- direct mutation of CERTIFIED skills

## 6. Definition of Done

- GOLD_001~024 remain green
- GOLD_025~029 pass
- Python 3.11/3.12/3.13 CI green
- CERTIFIED base remains byte/record equivalent after candidate submission
