# Knowledge Compound Engine V0.1 — Data Model

## Entities

### knowledge_sources
Immutable source identity and ingest metadata.
- id UUID PK
- source_type text
- source_uri text
- title text
- content_sha256 text UNIQUE
- captured_at timestamptz
- source_date timestamptz nullable
- raw_path text nullable
- metadata jsonb

### knowledge_claims
Atomic factual or procedural claims extracted from sources.
- id UUID PK
- source_id UUID FK
- claim_text text
- claim_sha256 text UNIQUE
- confidence numeric(5,2)
- status text: CANDIDATE | VERIFIED | CONFLICT | REJECTED
- created_at timestamptz

### evidence_links
Evidence relations supporting or contradicting claims.
- id UUID PK
- claim_id UUID FK
- source_id UUID FK
- relation text: SUPPORTS | CONTRADICTS | CONTEXT
- locator text nullable
- evidence_text text nullable
- created_at timestamptz

### knowledge_pages
Human-readable wiki artifacts.
- id UUID PK
- slug text UNIQUE
- title text
- domain text
- body_md text
- status text: DRAFT | VERIFIED | ARCHIVED
- confidence numeric(5,2)
- obsidian_path text nullable
- updated_at timestamptz

### page_claims
Many-to-many page/claim mapping.
- page_id UUID FK
- claim_id UUID FK
- PRIMARY KEY(page_id, claim_id)

### lesson_candidates
Potential reusable procedures derived from verified knowledge or runtime experience.
- id UUID PK
- title text
- body_md text
- source_page_id UUID nullable FK
- evidence_snapshot_id text nullable
- status text: CANDIDATE | TESTING | CERTIFIED | REJECTED | ARCHIVED
- created_at timestamptz

### routine_runs
Audit record for recurring jobs.
- id UUID PK
- routine_name text
- started_at timestamptz
- finished_at timestamptz nullable
- status text: RUNNING | PASS | PARTIAL | FAIL
- input_count int
- promoted_count int
- blocked_count int
- error_count int
- evidence jsonb

## Identity rules
- SHA256 is computed from canonical normalized content, never from mutable title alone.
- Source records are append-only.
- A claim's text hash prevents duplicate semantic copies after canonical text normalization.
- Wiki page status may change; prior claim/evidence lineage must remain queryable.

## Verification rule
A page can be VERIFIED only when all linked production claims are VERIFIED, no unresolved CONTRADICTS evidence exists, and each claim has at least one source relation.

## Skill promotion rule
A lesson may enter CERTIFIED only through the existing JoyLab CertificationGate, never by direct database update from an LLM worker.
