from __future__ import annotations

from dataclasses import dataclass

from .models import SkillRecord, SkillState
from .skill_candidate import SkillCandidate, SkillCandidateGenerator
from .skill_registry import SkillRegistry


@dataclass(frozen=True)
class CuratorRecommendation:
    action: str
    reason: str
    skill_id: str
    version: str


class SkillCurator:
    """Governed skill maintainer inspired by Hermes Curator.

    The curator can recommend lifecycle actions and submit NEW candidate versions.
    It never edits a CERTIFIED skill in place.
    """

    def __init__(
        self,
        *,
        candidate_generator: SkillCandidateGenerator | None = None,
        stale_after_days: int = 30,
        archive_after_days: int = 90,
    ) -> None:
        if stale_after_days < 0 or archive_after_days < stale_after_days:
            raise ValueError("INVALID_CURATOR_THRESHOLDS")
        self.generator = candidate_generator or SkillCandidateGenerator()
        self.stale_after_days = stale_after_days
        self.archive_after_days = archive_after_days

    def review_activity(
        self,
        skill: SkillRecord,
        *,
        days_since_last_use: int,
        pinned: bool = False,
    ) -> CuratorRecommendation:
        if pinned:
            return CuratorRecommendation("KEEP", "PINNED", skill.skill_id, skill.version)

        if days_since_last_use >= self.archive_after_days:
            return CuratorRecommendation(
                "PROPOSE_DEPRECATE",
                "ARCHIVE_THRESHOLD_REACHED",
                skill.skill_id,
                skill.version,
            )

        if days_since_last_use >= self.stale_after_days:
            return CuratorRecommendation(
                "REVIEW",
                "STALE_THRESHOLD_REACHED",
                skill.skill_id,
                skill.version,
            )

        return CuratorRecommendation("KEEP", "ACTIVE", skill.skill_id, skill.version)

    def propose_improvement(
        self,
        base: SkillRecord,
        *,
        rationale: str,
        change_summary: str,
        proposed_version: str | None = None,
    ) -> SkillCandidate:
        return self.generator.generate(
            base,
            rationale=rationale,
            change_summary=change_summary,
            proposed_version=proposed_version,
        )

    def submit_candidate(
        self,
        registry: SkillRegistry,
        candidate: SkillCandidate,
    ) -> SkillRecord:
        base = registry.get(candidate.skill_id, candidate.base_version)

        # The base record is read-only here. Certified skills must stay untouched.
        before = base
        new_record = self.generator.to_skill_record(candidate)
        registry.register(new_record)
        submitted = registry.transition(
            new_record.skill_id,
            new_record.version,
            SkillState.CANDIDATE,
        )

        after = registry.get(before.skill_id, before.version)
        if after != before:
            raise RuntimeError("BASE_SKILL_MUTATION_DETECTED")

        return submitted
