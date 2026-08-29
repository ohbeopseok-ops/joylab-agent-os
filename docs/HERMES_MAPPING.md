# Hermes -> JoyLab Function/Class Mapping

Source files reviewed:
- `agent/memory_manager.py`
- `agent/curator.py`
- `agent/learning_graph.py`

## 1. memory_manager.py

Hermes pattern | JoyLab mapping | Decision
---|---|---
`MemoryManager.add_provider()` | `MemoryRouter.register_provider()` | ADOPT
`prefetch_all()` | `MemoryRouter.recall()` | ADOPT
external prefetch timeout | provider timeout policy | ADOPT
background sync | asynchronous evidence/memory write | ADOPT later
`normalize_tool_schema()` | tool contract validator | ADOPT
context sanitation / scrubber | memory context boundary sanitizer | ADOPT
provider failure isolation | failure-isolated adapters | ADOPT
automatic memory writes | `MemoryWritePolicy.evaluate()` | MODIFY

JoyLab rule:
Memory providers may propose writes, but Operational Memory requires policy approval.

## 2. curator.py

Hermes pattern | JoyLab mapping | Decision
---|---|---
idle background review | `SkillCurator.review_due()` | ADOPT later
stale transition | `SkillLifecyclePolicy` | ADOPT
archive instead of delete | recoverable `DEPRECATED` state | ADOPT
pinned bypass | protected/certified lock | MODIFY
LLM patch/consolidate | `SkillCandidateGenerator` | MODIFY
automatic patch of agent-created skills | candidate-only mutation | REJECT for certified skills

JoyLab invariant:
Curator may produce a candidate version. It cannot rewrite a certified skill.

## 3. learning_graph.py

Hermes pattern | JoyLab mapping | Decision
---|---|---
`SkillNode` | `SkillGraphNode` | ADOPT
`related_skills` edges | explicit dependency/relationship edges | ADOPT
usage timestamps | evidence recency | ADOPT
use count | execution count | ADOPT
memory-skill lexical overlap | evidence-skill links | MODIFY
density stats | coverage / orphan skill diagnostics | ADOPT

JoyLab extension:
Graph edges should carry typed relations:
- DEPENDS_ON
- DERIVED_FROM
- SUPERSEDES
- VALIDATED_BY
- USED_BY

## 4. Class target for V0.3+

```text
MemoryRouter
  register_provider()
  recall()
  propose_write()
  apply_write_policy()

SkillCurator
  review_due()
  detect_stale()
  propose_archive()
  propose_candidate_version()

EvidenceGraph
  add_skill_node()
  add_evidence_node()
  link()
  orphan_skills()
  certification_lineage()
```

## 5. Main architectural difference

Hermes:
`experience -> learn -> mutate -> reuse`

JoyLab:
`experience -> candidate -> evidence -> certification -> versioned promotion -> reuse`
