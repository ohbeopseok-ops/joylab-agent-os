from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable


class ApprovalDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass(frozen=True)
class ApprovalAuditRecord:
    audit_id: str
    candidate_id: str
    skill_id: str
    base_version: str
    proposed_version: str
    actor: str
    decision: ApprovalDecision
    reason: str
    evidence_refs: tuple[str, ...]
    diff_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ApprovalAuditLog:
    """Append-only governance ledger for candidate approvals and rejections."""

    def __init__(self) -> None:
        self._records: list[ApprovalAuditRecord] = []
        self._ids: set[str] = set()

    @staticmethod
    def build_record(
        *,
        candidate_id: str,
        skill_id: str,
        base_version: str,
        proposed_version: str,
        actor: str,
        decision: ApprovalDecision,
        reason: str,
        evidence_refs: Iterable[str],
        diff_id: str,
    ) -> ApprovalAuditRecord:
        actor = actor.strip()
        reason = reason.strip()
        diff_id = diff_id.strip()
        refs = tuple(x.strip() for x in evidence_refs if x.strip())

        if not actor:
            raise ValueError("ACTOR_REQUIRED")
        if not reason:
            raise ValueError("APPROVAL_REASON_REQUIRED")
        if not diff_id:
            raise ValueError("DIFF_ID_REQUIRED")
        if decision is ApprovalDecision.APPROVE and not refs:
            raise ValueError("APPROVAL_REQUIRES_EVIDENCE")

        payload = {
            "candidate_id": candidate_id,
            "skill_id": skill_id,
            "base_version": base_version,
            "proposed_version": proposed_version,
            "actor": actor,
            "decision": decision.value,
            "reason": reason,
            "evidence_refs": refs,
            "diff_id": diff_id,
        }
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return ApprovalAuditRecord(
            audit_id=f"AUD-{digest[:20]}",
            candidate_id=candidate_id,
            skill_id=skill_id,
            base_version=base_version,
            proposed_version=proposed_version,
            actor=actor,
            decision=decision,
            reason=reason,
            evidence_refs=refs,
            diff_id=diff_id,
        )

    def append(self, record: ApprovalAuditRecord) -> None:
        if record.audit_id in self._ids:
            raise ValueError("AUDIT_ID_ALREADY_EXISTS")
        self._records.append(record)
        self._ids.add(record.audit_id)

    def for_candidate(self, candidate_id: str) -> tuple[ApprovalAuditRecord, ...]:
        return tuple(r for r in self._records if r.candidate_id == candidate_id)

    def all(self) -> tuple[ApprovalAuditRecord, ...]:
        return tuple(self._records)
