from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .evidence_builder import EvidenceBuilder
from .models import EvidenceSnapshot, EvidenceSnapshotArtifact, ExperienceRecord
from .persistent_lineage import (
    PersistentEvidenceStore,
    PersistentExperienceStore,
    PersistentLineageJournal,
    TX_COMMITTED_KIND,
    TX_PREPARED_KIND,
    evidence_from_payload,
    evidence_payload,
    experience_from_payload,
    experience_payload,
)
from .runtime_state import (
    RuntimeState,
    RuntimeStateStore,
    runtime_state_from_payload,
    runtime_state_payload,
    seal_runtime_state,
)
from .scheduled_ingestion import ScheduleSpec, ScheduledIngestionRunner
from .snapshot_integrity import seal_snapshot


@dataclass(frozen=True)
class CrashTransaction:
    tx_id: str
    schedule_id: str
    domain: str
    run_key: str
    now_epoch: int
    base_sequence: int
    experience: ExperienceRecord
    evidence_artifact: EvidenceSnapshotArtifact
    next_state: RuntimeState


@dataclass(frozen=True)
class CrashCommitResult:
    state: RuntimeState
    evidence: EvidenceSnapshot
    evidence_artifact: EvidenceSnapshotArtifact
    tx_id: str


@dataclass(frozen=True)
class RecoveryReport:
    status: str
    recovered_transactions: tuple[str, ...] = ()
    reason: str = ""


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _tx_id(payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return f"RTX-{digest[:20]}"


def transaction_payload(tx: CrashTransaction) -> dict[str, Any]:
    state_envelope = seal_runtime_state(tx.next_state)
    return {
        "tx_id": tx.tx_id,
        "schedule_id": tx.schedule_id,
        "domain": tx.domain,
        "run_key": tx.run_key,
        "now_epoch": tx.now_epoch,
        "base_sequence": tx.base_sequence,
        "experience": experience_payload(tx.experience),
        "evidence": evidence_payload(tx.evidence_artifact),
        "next_state": runtime_state_payload(tx.next_state),
        "next_state_id": state_envelope.state_id,
        "next_state_sha256": state_envelope.sha256,
    }


def transaction_from_payload(payload: dict[str, Any]) -> CrashTransaction:
    try:
        experience = experience_from_payload(dict(payload["experience"]))
        artifact = evidence_from_payload(dict(payload["evidence"]))
        next_state = runtime_state_from_payload(dict(payload["next_state"]))
        raw = {
            "schedule_id": str(payload["schedule_id"]),
            "domain": str(payload["domain"]),
            "run_key": str(payload["run_key"]),
            "now_epoch": int(payload["now_epoch"]),
            "base_sequence": int(payload["base_sequence"]),
            "experience_id": experience.experience_id,
            "snapshot_id": artifact.snapshot_id,
            "next_state_id": str(payload["next_state_id"]),
        }
        expected_tx_id = _tx_id(raw)
        if str(payload["tx_id"]) != expected_tx_id:
            raise ValueError("RECOVERY_TX_ID_MISMATCH")
        envelope = seal_runtime_state(next_state)
        if envelope.state_id != str(payload["next_state_id"]):
            raise ValueError("RECOVERY_STATE_ID_MISMATCH")
        if envelope.sha256 != str(payload["next_state_sha256"]):
            raise ValueError("RECOVERY_STATE_HASH_MISMATCH")
        if next_state.sequence != int(payload["base_sequence"]) + 1:
            raise ValueError("RECOVERY_SEQUENCE_CONTRACT_FAILED")
        return CrashTransaction(
            tx_id=expected_tx_id,
            schedule_id=raw["schedule_id"],
            domain=raw["domain"],
            run_key=raw["run_key"],
            now_epoch=raw["now_epoch"],
            base_sequence=raw["base_sequence"],
            experience=experience,
            evidence_artifact=artifact,
            next_state=next_state,
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("RECOVERY_"):
            raise
        raise ValueError("RECOVERY_TX_PAYLOAD_INVALID") from exc


class RecoveryReconciler:
    def __init__(
        self,
        *,
        state_store: RuntimeStateStore,
        journal: PersistentLineageJournal,
        experiences: PersistentExperienceStore,
        evidence: PersistentEvidenceStore,
        runtime_id: str = "joylab-main",
    ) -> None:
        self.state_store = state_store
        self.journal = journal
        self.experiences = experiences
        self.evidence = evidence
        self.runtime_id = runtime_id

    def _state_or_none(self) -> RuntimeState | None:
        try:
            return self.state_store.recover()
        except FileNotFoundError:
            return None

    def _transactions(self) -> tuple[dict[str, CrashTransaction], set[str], bool]:
        prepared: dict[str, CrashTransaction] = {}
        committed: set[str] = set()
        has_markers = False
        for entry in self.journal.recover_entries():
            if entry.kind == TX_PREPARED_KIND:
                has_markers = True
                tx = transaction_from_payload(entry.payload)
                if tx.tx_id in prepared:
                    raise ValueError("RECOVERY_DUPLICATE_PREPARED_TX")
                prepared[tx.tx_id] = tx
            elif entry.kind == TX_COMMITTED_KIND:
                has_markers = True
                tx_id = str(entry.payload.get("tx_id", ""))
                if not tx_id:
                    raise ValueError("RECOVERY_COMMIT_TX_ID_REQUIRED")
                committed.add(tx_id)
        unknown = committed.difference(prepared)
        if unknown:
            raise ValueError("RECOVERY_COMMIT_WITHOUT_PREPARE")
        return prepared, committed, has_markers

    def _validate_checkpoint_lineage(self, state: RuntimeState | None) -> None:
        if state is None:
            return
        ids = {r.experience_id for r in self.experiences.all()}
        for experience_id in state.checkpoints.values():
            if experience_id not in ids:
                raise ValueError("RECOVERY_BLOCKED_CHECKPOINT_WITHOUT_EXPERIENCE")

    def _ensure_experience(self, tx: CrashTransaction) -> None:
        if self.experiences.contains_id(tx.experience.experience_id):
            existing = next(
                r for r in self.experiences.all()
                if r.experience_id == tx.experience.experience_id
            )
            if existing != tx.experience:
                raise ValueError("RECOVERY_BLOCKED_EXPERIENCE_CONFLICT")
            return
        self.experiences.append(tx.experience)

    def _ensure_evidence(self, tx: CrashTransaction) -> None:
        artifact = tx.evidence_artifact
        if self.evidence.contains_id(artifact.snapshot_id):
            existing = next(
                a for a in self.evidence.all()
                if a.snapshot_id == artifact.snapshot_id
            )
            if existing != artifact:
                raise ValueError("RECOVERY_BLOCKED_EVIDENCE_CONFLICT")
            return
        self.evidence.append(artifact)

    def _ensure_state(self, tx: CrashTransaction) -> None:
        current = self._state_or_none()
        if current is None:
            if tx.base_sequence != 0:
                raise ValueError("RECOVERY_BLOCKED_BASE_STATE_MISSING")
            self.state_store.save(tx.next_state)
            return
        if current == tx.next_state:
            return
        if current.sequence == tx.base_sequence:
            self.state_store.save(tx.next_state)
            return
        raise ValueError("RECOVERY_BLOCKED_RUNTIME_DIVERGED")

    def _append_committed(self, tx: CrashTransaction) -> None:
        self.journal.append(
            TX_COMMITTED_KIND,
            {
                "tx_id": tx.tx_id,
                "next_state_id": seal_runtime_state(tx.next_state).state_id,
                "sequence": tx.next_state.sequence,
            },
        )

    def reconcile(self) -> RecoveryReport:
        try:
            prepared, committed, has_markers = self._transactions()
            state = self._state_or_none()

            if not has_markers:
                self._validate_checkpoint_lineage(state)
                return RecoveryReport("LEGACY_CONSISTENT")

            committed_txs = [
                tx for tx_id, tx in prepared.items() if tx_id in committed
            ]
            if committed_txs:
                latest = max(committed_txs, key=lambda tx: tx.next_state.sequence)
                if state is None or state.sequence < latest.next_state.sequence:
                    self._ensure_experience(latest)
                    self._ensure_evidence(latest)
                    self.state_store.save(latest.next_state)
                    state = latest.next_state
                elif (
                    state.sequence == latest.next_state.sequence
                    and state != latest.next_state
                ):
                    raise ValueError("RECOVERY_BLOCKED_COMMITTED_STATE_DIVERGED")

            recovered: list[str] = []
            pending = sorted(
                (
                    tx for tx_id, tx in prepared.items()
                    if tx_id not in committed
                ),
                key=lambda tx: tx.next_state.sequence,
            )
            for tx in pending:
                self._ensure_experience(tx)
                self._ensure_evidence(tx)
                self._ensure_state(tx)
                self._append_committed(tx)
                recovered.append(tx.tx_id)

            state = self._state_or_none()
            prepared, committed, _ = self._transactions()
            committed_sequences = [
                tx.next_state.sequence
                for tx_id, tx in prepared.items()
                if tx_id in committed
            ]
            if committed_sequences and state is not None:
                max_committed = max(committed_sequences)
                if state.sequence > max_committed:
                    raise ValueError("RECOVERY_BLOCKED_STATE_AHEAD_UNTRACKED")

            self._validate_checkpoint_lineage(state)
            return RecoveryReport(
                "RECOVERED" if recovered else "CONSISTENT",
                tuple(recovered),
            )
        except ValueError as exc:
            return RecoveryReport("RECOVERY_BLOCKED", reason=str(exc))


class CrashConsistencyCoordinator:
    def __init__(
        self,
        *,
        ingestion: ScheduledIngestionRunner,
        experiences: PersistentExperienceStore,
        evidence: PersistentEvidenceStore,
        evidence_builder: EvidenceBuilder | None = None,
    ) -> None:
        if experiences.journal.path != evidence.journal.path:
            raise ValueError("CRASH_COORDINATOR_REQUIRES_SHARED_JOURNAL")
        self.ingestion = ingestion
        self.experiences = experiences
        self.evidence = evidence
        self.journal = experiences.journal
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.reconciler = RecoveryReconciler(
            state_store=ingestion.state_store,
            journal=self.journal,
            experiences=experiences,
            evidence=evidence,
            runtime_id=ingestion.runtime_id,
        )

    def build_transaction(
        self,
        *,
        schedule: ScheduleSpec,
        run_key: str,
        now_epoch: int,
        experience: ExperienceRecord,
        base_state: RuntimeState,
    ) -> CrashTransaction:
        if self.experiences.contains_id(experience.experience_id):
            raise ValueError("EXPERIENCE_ID_ALREADY_EXISTS")
        next_state = self.ingestion.prepare_next_state(
            spec=schedule,
            run_key=run_key,
            now_epoch=now_epoch,
            experience=experience,
            state=base_state,
        )
        records = self.experiences.all() + (experience,)
        snapshot = self.evidence_builder.build(
            experience.skill_id,
            experience.skill_version,
            records,
        )
        artifact = seal_snapshot(snapshot)
        raw = {
            "schedule_id": schedule.schedule_id,
            "domain": schedule.domain,
            "run_key": run_key,
            "now_epoch": now_epoch,
            "base_sequence": base_state.sequence,
            "experience_id": experience.experience_id,
            "snapshot_id": artifact.snapshot_id,
            "next_state_id": seal_runtime_state(next_state).state_id,
        }
        tx_id = _tx_id(raw)
        return CrashTransaction(
            tx_id=tx_id,
            schedule_id=schedule.schedule_id,
            domain=schedule.domain,
            run_key=run_key,
            now_epoch=now_epoch,
            base_sequence=base_state.sequence,
            experience=experience,
            evidence_artifact=artifact,
            next_state=next_state,
        )

    def commit(self, tx: CrashTransaction) -> CrashCommitResult:
        report = self.reconciler.reconcile()
        if report.status == "RECOVERY_BLOCKED":
            raise ValueError(report.reason)

        self.journal.append(TX_PREPARED_KIND, transaction_payload(tx))
        self.experiences.append(tx.experience)
        self.evidence.append(tx.evidence_artifact)
        self.ingestion.state_store.save(tx.next_state)
        self.reconciler._append_committed(tx)
        return CrashCommitResult(
            state=tx.next_state,
            evidence=tx.evidence_artifact.snapshot,
            evidence_artifact=tx.evidence_artifact,
            tx_id=tx.tx_id,
        )
