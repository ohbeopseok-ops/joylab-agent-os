# Knowledge Compound Engine V0.1 — Tasks

## P0 Foundation
- [x] Architecture/spec/data model documented
- [x] Grok/Prime/JoyLab adoption matrix documented
- [x] Core Python verification primitives implemented
- [x] Supabase migration drafted
- [x] Unit tests drafted
- [ ] Apply migration to selected Supabase project
- [ ] Configure Obsidian vault path on self-hosted runtime

## P1 Ingestion
- [ ] URL/article adapter
- [ ] PDF text adapter
- [ ] YouTube transcript adapter
- [ ] screenshot/note adapter
- [ ] canonical normalizer
- [ ] SHA256 dedupe registry

## P1 Verification
- [ ] claim extractor adapter interface
- [ ] evidence resolver interface
- [ ] conflict detector
- [ ] confidence calibration
- [ ] source freshness policy

## P1 Projection
- [ ] Obsidian Markdown renderer
- [ ] page/claim backlinks
- [ ] evidence footer
- [ ] atomic file writes

## P2 Nightly Routine
- [ ] self-hosted scheduler or local Task Scheduler
- [ ] collect -> verify -> project -> lesson flow
- [ ] routine_run audit record
- [ ] retry/replay policy
- [ ] daily summary artifact

## P2 Skill Promotion
- [ ] LessonCandidate adapter to existing CertificationGate
- [ ] regression bundle generation
- [ ] gold-case linkage
- [ ] certified skill immutable versioning

## Release Gate
V0.1 is GREEN only if tests prove duplicate prevention, conflict blocking, confidence blocking, lineage preservation and no direct certified-skill mutation.
