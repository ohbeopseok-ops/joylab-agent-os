# Knowledge Compound Engine V0.1 — Specification

## Inputs
Supported logical input types: URL/article, PDF text, YouTube transcript, screenshot-derived text, note, bookmark export.

## Ingestion contract
Every ingested item must produce:
- stable source id
- canonical text
- SHA256 fingerprint
- captured timestamp
- source metadata
- raw storage pointer when available

Duplicate fingerprints do not create a second source record.

## Claim extraction contract
A claim must be atomic enough to verify independently. Extractor output must never directly mark a claim VERIFIED.

## Verification contract
Verifier returns:
- status: VERIFIED | CONFLICT | REJECTED | NEEDS_REVIEW
- confidence 0..100
- evidence relations
- reason codes

Default auto-promotion threshold: confidence >= 85, at least one SUPPORTS relation, no unresolved CONTRADICTS relation, no hard-gate violation.

## Wiki contract
Verified pages are rendered as Markdown with YAML frontmatter containing source ids, claim ids, confidence, status, created_at and updated_at. Obsidian is a projection, not the canonical database.

## Routine contract
Nightly routine is idempotent. Re-running the same inputs must not duplicate sources, claims or pages.

## Security contract
- secrets never stored in wiki pages
- source ingestion can be domain/visibility allowlisted
- customer PII and restricted corporate material must be excluded or redacted before cloud processing
- logs record identifiers and hashes, not sensitive raw content unless policy allows it

## Observability
Each routine_run records counts, duration, status, failures and promoted artifact ids. Every wiki page and skill candidate must be traceable back to source and evidence.

## Non-goals V0.1
- unrestricted autonomous browsing
- autonomous write access to certified skills
- semantic vector search dependency
- multi-user RBAC beyond basic ownership boundary
- automatic live Supabase migration execution

## Acceptance tests
1. identical source is deduplicated
2. conflicting evidence blocks verification
3. low confidence blocks verification
4. verified claim can render an Obsidian page
5. uncertified lesson cannot be promoted as skill
6. repeated nightly run is idempotent
