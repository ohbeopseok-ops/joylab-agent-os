from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Iterable

from ..certification_gate import CertificationGate
from ..evidence_builder import EvidenceBuilder
from ..experience_logger import ExperienceLogger
from ..memory_router import MemoryRouter
from ..models import (
    CertificationResult,
    ExperienceRecord,
    MemoryTier,
    MemoryWriteDecision,
    MemoryWriteProposal,
)
from ..snapshot_integrity import EvidenceSnapshotArtifact, artifact_to_json, seal_snapshot


@dataclass(frozen=True)
class Core8Decision:
    decision_id: str
    skill_id: str
    skill_version: str
    ticker: str
    action: str
    confidence: float
    success: bool
    is_gold_case: bool = False
    oos_pass: bool = False
    oos_fail: bool = False
    regression_pass: bool = False
    regression_fail: bool = False
    hard_gate_violation: bool = False


@dataclass(frozen=True)
class Core8E2EResult:
    artifact: EvidenceSnapshotArtifact
    certification: CertificationResult
    memory_write: MemoryWriteDecision


class Core8Adapter:
    """Boundary adapter from Core8 decisions into JoyLab Agent OS evidence contracts."""

    @staticmethod
    def to_experience(decision: Core8Decision) -> ExperienceRecord:
        tags: list[str] = []
        if decision.is_gold_case:
            tags.append("gold_case")
        if decision.oos_pass:
            tags.append("oos_pass")
        if decision.oos_fail:
            tags.append("oos_fail")
        if decision.regression_pass:
            tags.append("regression_pass")
        if decision.regression_fail:
            tags.append("regression_fail")
        if decision.hard_gate_violation:
            tags.append("hard_gate_violation")

        return ExperienceRecord(
            experience_id=decision.decision_id,
            skill_id=decision.skill_id,
            skill_version=decision.skill_version,
            success=decision.success,
            metrics={"confidence": float(decision.confidence)},
            tags=tuple(tags),
        )

    @staticmethod
    def ingest(
        decisions: Iterable[Core8Decision],
        logger: ExperienceLogger,
    ) -> tuple[ExperienceRecord, ...]:
        records: list[ExperienceRecord] = []
        for decision in decisions:
            record = Core8Adapter.to_experience(decision)
            logger.append(record)
            records.append(record)
        return tuple(records)

    @staticmethod
    def run_e2e(
        *,
        skill_id: str,
        skill_version: str,
        logger: ExperienceLogger,
        builder: EvidenceBuilder,
        gate: CertificationGate,
        memory: MemoryRouter,
    ) -> Core8E2EResult:
        snapshot = builder.build(skill_id, skill_version, logger.all())
        artifact = seal_snapshot(snapshot)
        evidence = builder.to_certification_evidence(snapshot)
        certification = gate.evaluate(evidence)

        payload = artifact_to_json(artifact)
        memory_write = memory.propose_write(
            MemoryWriteProposal(
                tier=MemoryTier.EVIDENCE,
                key=artifact.snapshot_id,
                value=payload,
                source_ref=artifact.snapshot_id,
                immutable=True,
                certified_source=certification.passed,
            )
        )

        return Core8E2EResult(
            artifact=artifact,
            certification=certification,
            memory_write=memory_write,
        )
