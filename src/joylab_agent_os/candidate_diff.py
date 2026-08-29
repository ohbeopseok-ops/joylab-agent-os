from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from .models import SkillRecord
from .skill_candidate import SkillCandidate


@dataclass(frozen=True)
class CandidateDiffArtifact:
    diff_id: str
    candidate_id: str
    skill_id: str
    base_version: str
    proposed_version: str
    changes: tuple[tuple[str, str, str], ...]
    sha256: str


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


class CandidateDiffBuilder:
    """Builds a deterministic review artifact for a proposed skill version."""

    def build(self, base: SkillRecord, candidate: SkillCandidate) -> CandidateDiffArtifact:
        if base.skill_id != candidate.skill_id:
            raise ValueError("SKILL_ID_MISMATCH")
        if base.version != candidate.base_version:
            raise ValueError("BASE_VERSION_MISMATCH")

        proposed_metadata = {
            **base.metadata,
            "candidate_id": candidate.candidate_id,
            "base_version": candidate.base_version,
            "rationale": candidate.rationale,
            "change_summary": candidate.change_summary,
        }

        changes: list[tuple[str, str, str]] = [
            ("version", base.version, candidate.proposed_version),
            ("rationale", str(base.metadata.get("rationale", "")), candidate.rationale),
            (
                "change_summary",
                str(base.metadata.get("change_summary", "")),
                candidate.change_summary,
            ),
        ]

        base_meta = _canonical(base.metadata)
        proposed_meta = _canonical(proposed_metadata)
        if base_meta != proposed_meta:
            changes.append(("metadata", base_meta, proposed_meta))

        payload = {
            "candidate_id": candidate.candidate_id,
            "skill_id": candidate.skill_id,
            "base_version": candidate.base_version,
            "proposed_version": candidate.proposed_version,
            "changes": changes,
        }
        digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()

        return CandidateDiffArtifact(
            diff_id=f"DIF-{digest[:20]}",
            candidate_id=candidate.candidate_id,
            skill_id=candidate.skill_id,
            base_version=candidate.base_version,
            proposed_version=candidate.proposed_version,
            changes=tuple(changes),
            sha256=digest,
        )
