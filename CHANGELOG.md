# Changelog

All notable JoyLab Agent OS milestones are recorded here.

## [Unreleased]

Future work must start after the V0.5.3 frozen certified baseline.

## [0.5.3-frozen] — 2026-08-29

Frozen certified baseline at PR #13.

Frozen commit:
`9e9cb2cfc75aaf6430225c729522c72d1306f71a`

Release anchor:
`release/v0.5.3-frozen`

### Added
- AdapterRegistry and DomainPluginRegistry.
- Governed Gold Case JSON Registry.
- Unified V0.5 Certification Gate.
- Python 3.11 / 3.12 / 3.13 matrix dependency.
- Regression gate.
- JSON Schema gate.
- EVS integrity gate.
- EVG integrity gate.
- Approval Audit gate.

### Verification
- Python 3.11: GREEN.
- Python 3.12: GREEN.
- Python 3.13: GREEN.
- GOLD_001 through GOLD_070: CERTIFIED.
- Unified Certification Gate: GREEN.

### Freeze rule
- V0.5.3 behavior is historically fixed at the frozen commit.
- Future work starts as V0.6+.
- The release anchor must not move forward.

## [0.4.2-frozen] — 2026-08-29

Historical frozen baseline at PR #7.

Frozen commit:
`53ec9f5626c895bee780b20e971fb25be2748cef`

### Added
- Governed Skill Registry and lifecycle gates.
- Append-only Experience Logger.
- Deterministic Certification Gate.
- EvidenceBuilder and EvidenceSnapshot lineage.
- Evidence Snapshot JSON Schema, SHA-256 sealing, and immutable EVS IDs.
- MemoryRouter with WORKING / OPERATIONAL / EVIDENCE tiers.
- MemoryWritePolicy with governed operational and evidence writes.
- Core8 E2E adapter.
- Versioned SkillCandidateGenerator.
- Governed SkillCurator with no in-place CERTIFIED mutation.
- Candidate Diff and append-only Approval Audit Log.
- Typed EvidenceGraph.
- Full provenance path:
  `Core8 Decision -> Experience -> EVS -> Skill Candidate -> Approval Audit -> Certified Skill`.
- Orphan detection and strict provenance-completeness checks.

### Verification
- Python 3.11: GREEN.
- Python 3.12: GREEN.
- Python 3.13: GREEN.
- Gold Cases: GOLD_001 through GOLD_040 GREEN at the frozen baseline.

### Governance invariants
- CERTIFIED skills are immutable in place.
- A new behavior requires a new candidate version.
- Approval requires attributable actor/reason/evidence.
- Missing critical evidence is never silently converted to PASS.
- Investment ranking does not bypass execution, portfolio, or human gates.
- Evidence history remains append-only and reviewable.

### Not included in this frozen baseline
The following landed after the V0.4.2 baseline and are intentionally excluded:
- V0.4.3 EvidenceGraph graph-snapshot sealing.
- V0.5 multi-investment-domain adapters.

## [0.4.1]
- Candidate Diff.
- Approval Audit Log.
- GOLD_030 through GOLD_034.

## [0.4.0]
- SkillCandidateGenerator.
- SkillCurator.
- CERTIFIED base immutability.
- GOLD_025 through GOLD_029.

## [0.3.1]
- Core8 E2E Adapter.
- GOLD_022 through GOLD_024.

## [0.3.0]
- Evidence integrity.
- MemoryRouter.
- MemoryWritePolicy.
- GOLD_014 through GOLD_021.

## [0.2.0]
- EvidenceBuilder.
- EvidenceSnapshot.
- GOLD_008 through GOLD_013.

## [0.1.0]
- Skill Registry.
- Experience Logger.
- Certification Gate.
- GOLD_001 through GOLD_007.
