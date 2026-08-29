from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .models import SkillRecord, SkillState


@dataclass(frozen=True)
class SkillCandidate:
    candidate_id: str
    skill_id: str
    base_version: str
    proposed_version: str
    name: str
    domain: str
    rationale: str
    change_summary: str


def _next_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError("VERSION_MUST_BE_SEMVER")
    major, minor, patch = map(int, parts)
    return f"{major}.{minor}.{patch + 1}"


class SkillCandidateGenerator:
    """Creates versioned improvement proposals without mutating the base skill."""

    def generate(
        self,
        base: SkillRecord,
        *,
        rationale: str,
        change_summary: str,
        proposed_version: str | None = None,
    ) -> SkillCandidate:
        if not rationale.strip():
            raise ValueError("RATIONALE_REQUIRED")
        if not change_summary.strip():
            raise ValueError("CHANGE_SUMMARY_REQUIRED")

        next_version = proposed_version or _next_patch(base.version)
        if next_version == base.version:
            raise ValueError("CANDIDATE_VERSION_MUST_DIFFER")

        digest = sha256(
            f"{base.skill_id}|{base.version}|{next_version}|{rationale}|{change_summary}".encode("utf-8")
        ).hexdigest()[:16]

        return SkillCandidate(
            candidate_id=f"SKC-{digest}",
            skill_id=base.skill_id,
            base_version=base.version,
            proposed_version=next_version,
            name=base.name,
            domain=base.domain,
            rationale=rationale.strip(),
            change_summary=change_summary.strip(),
        )

    @staticmethod
    def to_skill_record(candidate: SkillCandidate) -> SkillRecord:
        return SkillRecord(
            skill_id=candidate.skill_id,
            name=candidate.name,
            domain=candidate.domain,
            version=candidate.proposed_version,
            state=SkillState.DISCOVERED,
            metadata={
                "candidate_id": candidate.candidate_id,
                "base_version": candidate.base_version,
                "rationale": candidate.rationale,
                "change_summary": candidate.change_summary,
            },
        )
