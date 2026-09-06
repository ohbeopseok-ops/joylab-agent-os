# JoyLab Baseline Record V1.0

## Purpose
Durable non-sensitive context that should survive across chats, tools, and projects.

## Working identity
JoyLab is a practical knowledge and execution system focused on investment, AI, work/leadership, books, and building useful systems.

## Default goals
- Turn facts into reusable knowledge rather than isolated posts.
- Make outputs immediately usable in real work.
- Prefer concise structure, explicit decisions, and measurable completion criteria.
- Build systems that another agent or future session can continue without relying on hidden chat context.

## Default working style
- Define objective and scope first.
- Distinguish fact, interpretation, and decision.
- Use stepwise plans for complex work.
- Prefer evidence-backed recommendations.
- Preserve useful prior work; merge or migrate before deleting.
- Build in small verified increments.
- Use PASS / BLOCKED for execution status.
- Record durable decisions in `records/DECISIONS.md`.

## Content architecture
Five primary pillars:
1. INVEST
2. AI
3. WORK
4. BOOKS
5. BUILD

Default content/research flow:
HOOK → FACT → WHY → TRANSMISSION → JUDGMENT → SCENARIO → NEXT

## Knowledge architecture principle
Source → Evidence → Knowledge Node → Pillar Asset → Distribution Channel → Feedback → Rule Update

Distribution channels may include blog, social, video, documents, apps, or internal training materials. The source-of-truth record should remain separate from the distribution format.

## Development principle
Stable behavior first, then small version upgrades. Every meaningful change should have a clear acceptance criterion and, when software is involved, appropriate regression checks.

## Repository roles
- `joylab-agent-os`: global reusable agent skills, records, schemas, Gold Cases, operating rules.
- Project repositories: project-specific code, specs, tasks, tests, and local decisions.
- A project may reference the global baseline but should keep its own specific Source of Truth.

## Privacy / security boundary
Do not put credentials, secrets, customer data, restricted employer information, health data, or other sensitive personal data in this global baseline.
