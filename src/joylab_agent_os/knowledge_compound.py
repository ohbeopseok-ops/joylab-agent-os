from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import re
from typing import Iterable


class ClaimStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    CONFLICT = "CONFLICT"
    REJECTED = "REJECTED"


class EvidenceRelation(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CONTEXT = "CONTEXT"


@dataclass(frozen=True)
class Evidence:
    source_id: str
    relation: EvidenceRelation
    locator: str | None = None


@dataclass(frozen=True)
class ClaimCandidate:
    text: str
    confidence: float
    source_id: str
    evidence: tuple[Evidence, ...] = ()
    hard_gate_violations: int = 0


@dataclass(frozen=True)
class VerificationResult:
    status: ClaimStatus
    reason_codes: tuple[str, ...]

    @property
    def promotable(self) -> bool:
        return self.status is ClaimStatus.VERIFIED


def canonicalize_text(text: str) -> str:
    """Normalize text for deterministic fingerprints without changing semantics."""
    return re.sub(r"\s+", " ", text).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(canonicalize_text(text).encode("utf-8")).hexdigest()


def verify_claim(candidate: ClaimCandidate, *, threshold: float = 85.0) -> VerificationResult:
    reasons: list[str] = []

    if not candidate.source_id.strip():
        reasons.append("SOURCE_MISSING")
    if not canonicalize_text(candidate.text):
        reasons.append("CLAIM_EMPTY")
    if candidate.hard_gate_violations > 0:
        reasons.append("HARD_GATE_VIOLATION")
    if candidate.confidence < threshold:
        reasons.append("LOW_CONFIDENCE")

    relations = {item.relation for item in candidate.evidence}
    if EvidenceRelation.CONTRADICTS in relations:
        reasons.append("UNRESOLVED_CONTRADICTION")
    if EvidenceRelation.SUPPORTS not in relations:
        reasons.append("SUPPORTING_EVIDENCE_MISSING")

    if reasons:
        status = (
            ClaimStatus.CONFLICT
            if "UNRESOLVED_CONTRADICTION" in reasons
            else ClaimStatus.REJECTED
        )
        return VerificationResult(status=status, reason_codes=tuple(reasons))

    return VerificationResult(status=ClaimStatus.VERIFIED, reason_codes=())


def can_verify_page(results: Iterable[VerificationResult]) -> bool:
    materialized = tuple(results)
    return bool(materialized) and all(result.promotable for result in materialized)


def render_obsidian_page(
    *,
    title: str,
    domain: str,
    body_md: str,
    source_ids: Iterable[str],
    claim_ids: Iterable[str],
    confidence: float,
) -> str:
    sources = ", ".join(sorted(set(source_ids)))
    claims = ", ".join(sorted(set(claim_ids)))
    return (
        "---\n"
        f'title: "{title}"\n'
        f'domain: "{domain}"\n'
        "status: VERIFIED\n"
        f"confidence: {confidence:.2f}\n"
        f'source_ids: "{sources}"\n'
        f'claim_ids: "{claims}"\n'
        "---\n\n"
        f"{body_md.strip()}\n"
    )
