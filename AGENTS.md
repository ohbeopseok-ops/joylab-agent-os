# JoyLab Global Agent Bootstrap

This repository is the Source of Truth for reusable JoyLab agent behavior.

## Mandatory bootstrap order
1. Read `skills/joylab-core/SKILL.md`.
2. Read `records/BASELINE.md`.
3. Read `records/DECISIONS.md` for locked decisions relevant to the task.
4. Read the target project's own `AGENTS.md`, `SPEC.md`, `TASKS.md`, and `ROADMAP.md` when present.
5. Project-specific rules override this global baseline when they are more specific and do not violate a locked global rule.

## Operating rule
Do not depend on chat memory alone for durable project behavior. Stable rules belong in GitHub records or project files.

## Output rule
Every substantial deliverable should be reproducible from repository context: inputs, assumptions, decisions, output format, and validation criteria must be explicit enough that another agent can continue the work.

## Safety boundary
Never commit customer data, credentials, secrets, private company information, health information, or other sensitive personal data into this baseline repository.
