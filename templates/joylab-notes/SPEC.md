# JoyLab Notes SPEC V0.1

## Product Vision
JoyLab Notes is the canonical knowledge media hub for INVEST, AI, WORK, BOOKS, and BUILD.

## Source of Truth
Global rules: `ohbeopseok-ops/joylab-agent-os`
Project rules: this repository's `AGENTS.md`, `SPEC.md`, `TASKS.md`, `ROADMAP.md`.

## V0.1 Scope
- Home
- 5 Pillar pages
- Article page
- Search
- Node/Tag pages
- Related Articles
- MDX/Markdown content
- Responsive UI
- SEO metadata
- Sitemap
- RSS
- Basic analytics

## Non-goals
- Authentication
- Comments/community
- Payments
- AI chatbot
- Automated NAVER/SNS publishing
- Complex graph visualization

## Article Contract
Every article must validate against JOYLAB 7 schema and pass Quality Gate before PUBLISHED.

## Architecture Principle
Content OS = production factory
JOYLAB 7 = editorial/reasoning engine
JoyLab Notes = canonical store
Channels = distribution
Knowledge Graph = long-term asset

## Release Gate
PASS only when typecheck, lint, tests, build, regression, content schema validation, and gold-case checks are green. Otherwise BLOCKED.
