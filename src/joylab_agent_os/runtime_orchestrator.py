from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .adapter_registry import DomainPluginRegistry
from .evidence_builder import EvidenceBuilder
from .experience_logger import ExperienceLogger
from .models import EvidenceSnapshot, EvidenceSnapshotArtifact, ExperienceRecord
from .scheduled_ingestion import ScheduleSpec, ScheduledIngestionResult, ScheduledIngestionRunner
from .snapshot_integrity import seal_snapshot


@dataclass(frozen=True)
class OrchestrationResult:
    status: str
    experience: ExperienceRecord | None
    evidence: EvidenceSnapshot | None
    evidence_artifact: EvidenceSnapshotArtifact | None
    runtime_sequence: int


class RuntimeOrchestrator:
    """Governed plugin -> schedule -> adapter -> state -> evidence runtime."""

    def __init__(
        self,
        *,
        plugins: DomainPluginRegistry,
        ingestion: ScheduledIngestionRunner,
        experiences: ExperienceLogger,
        evidence_builder: EvidenceBuilder | None = None,
        evidence_store: Any | None = None,
    ) -> None:
        self.plugins = plugins
        self.ingestion = ingestion
        self.experiences = experiences
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.evidence_store = evidence_store

    def execute(
        self,
        *,
        plugin_id: str,
        schedule: ScheduleSpec,
        run_key: str,
        now_epoch: int,
        signal: Any,
    ) -> OrchestrationResult:
        plugin = self.plugins.get(plugin_id)

        if not plugin.enabled:
            state = self.ingestion.current_state()
            return OrchestrationResult(
                status="PLUGIN_DISABLED",
                experience=None,
                evidence=None,
                evidence_artifact=None,
                runtime_sequence=state.sequence,
            )

        if plugin.domain.strip().lower() != schedule.domain.strip().lower():
            raise ValueError("PLUGIN_SCHEDULE_DOMAIN_MISMATCH")

        schedule_status, schedule_state = self.ingestion.check_status(
            spec=schedule,
            run_key=run_key,
            now_epoch=now_epoch,
        )
        if schedule_status != "READY":
            return OrchestrationResult(
                status=schedule_status,
                experience=None,
                evidence=None,
                evidence_artifact=None,
                runtime_sequence=schedule_state.sequence,
            )

        prepared = self.ingestion.adapters.route(schedule.domain, signal)
        if self.experiences.contains_id(prepared.experience_id):
            raise ValueError("EXPERIENCE_ID_ALREADY_EXISTS")

        result = self.ingestion.run_prepared(
            spec=schedule,
            run_key=run_key,
            now_epoch=now_epoch,
            experience=prepared,
        )

        if result.status != "EXECUTED" or result.experience is None:
            return OrchestrationResult(
                status=result.status,
                experience=None,
                evidence=None,
                evidence_artifact=None,
                runtime_sequence=result.state.sequence,
            )

        self.experiences.append(result.experience)
        records = self.experiences.all()
        snapshot = self.evidence_builder.build(
            result.experience.skill_id,
            result.experience.skill_version,
            records,
        )
        artifact = seal_snapshot(snapshot)
        if self.evidence_store is not None:
            self.evidence_store.append(artifact)

        return OrchestrationResult(
            status="EXECUTED",
            experience=result.experience,
            evidence=snapshot,
            evidence_artifact=artifact,
            runtime_sequence=result.state.sequence,
        )
