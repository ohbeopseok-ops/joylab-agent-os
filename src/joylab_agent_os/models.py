from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SkillState(str, Enum):
    DISCOVERED = "DISCOVERED"
    CANDIDATE = "CANDIDATE"
    TESTING = "TESTING"
    CERTIFIED = "CERTIFIED"
    DEPRECATED = "DEPRECATED"


@dataclass(frozen=True)
class SkillRecord:
    skill_id: str
    name: str
    domain: str
    version: str
    state: SkillState = SkillState.DISCOVERED
    created_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperienceRecord:
    experience_id: str
    skill_id: str
    skill_version: str
    success: bool
    metrics: dict[str, float] = field(default_factory=dict)
    tags: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class EvidenceSnapshot:
    skill_id: str
    skill_version: str
    samples: int
    successful_samples: int
    gold_cases: int
    confidence: float
    oos_pass: bool
    regression_pass: bool
    hard_gate_violations: int
    source_experience_ids: tuple[str, ...]


@dataclass(frozen=True)
class CertificationEvidence:
    samples: int
    gold_cases: int
    confidence: float
    oos_pass: bool
    regression_pass: bool
    hard_gate_violations: int = 0


@dataclass(frozen=True)
class CertificationPolicy:
    version: str = "V0.1"
    min_samples: int = 20
    min_gold_cases: int = 10
    min_confidence: float = 80.0
    require_oos_pass: bool = True
    require_regression_pass: bool = True
    max_hard_gate_violations: int = 0


@dataclass(frozen=True)
class CertificationResult:
    passed: bool
    reasons: tuple[str, ...]
    evaluated_policy: str
