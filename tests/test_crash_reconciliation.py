import os

import pytest

from joylab_agent_os.adapter_registry import AdapterRegistry, DomainPlugin, DomainPluginRegistry
from joylab_agent_os.adapters.core8 import Core8Adapter, Core8Decision
from joylab_agent_os.crash_reconciliation import (
    CrashConsistencyCoordinator,
    RecoveryReconciler,
    transaction_payload,
)
from joylab_agent_os.evidence_builder import EvidenceBuilder
from joylab_agent_os.models import ExperienceRecord
from joylab_agent_os.persistent_lineage import (
    PersistentEvidenceStore,
    PersistentExperienceStore,
    PersistentLineageJournal,
    TX_COMMITTED_KIND,
    TX_PREPARED_KIND,
)
from joylab_agent_os.runtime_orchestrator import RuntimeOrchestrator
from joylab_agent_os.runtime_state import RuntimeState, RuntimeStateStore
from joylab_agent_os.scheduled_ingestion import ScheduleSpec, ScheduledIngestionRunner


def decision(exp_id="EXP-001", confidence=90.0):
    return Core8Decision(
        decision_id=exp_id,
        skill_id="CORE8_DECISION",
        skill_version="1.0.0",
        ticker="005930",
        action="HOLD",
        confidence=confidence,
        success=True,
    )


def schedule():
    return ScheduleSpec("core8-hourly", "core8", 3600, True)


def env(tmp_path):
    runtime_path = tmp_path / "runtime.json"
    lineage_path = tmp_path / "lineage.jsonl"
    adapters = AdapterRegistry()
    adapters.register("core8", Core8Decision, Core8Adapter.to_experience)
    ingestion = ScheduledIngestionRunner(
        state_store=RuntimeStateStore(runtime_path),
        adapters=adapters,
    )
    journal = PersistentLineageJournal(lineage_path)
    experiences = PersistentExperienceStore(journal)
    evidence = PersistentEvidenceStore(journal)
    coordinator = CrashConsistencyCoordinator(
        ingestion=ingestion,
        experiences=experiences,
        evidence=evidence,
        evidence_builder=EvidenceBuilder(),
    )
    return ingestion, journal, experiences, evidence, coordinator


def tx_for(tmp_path, exp_id="EXP-001", now_epoch=1000, run_key="RUN-001"):
    ingestion, journal, experiences, evidence, coordinator = env(tmp_path)
    base = ingestion.current_state()
    exp = Core8Adapter.to_experience(decision(exp_id))
    tx = coordinator.build_transaction(
        schedule=schedule(),
        run_key=run_key,
        now_epoch=now_epoch,
        experience=exp,
        base_state=base,
    )
    return ingestion, journal, experiences, evidence, coordinator, tx


def test_gold_103_normal_commit_writes_prepare_and_commit_markers(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    result = coordinator.commit(tx)

    kinds = [e.kind for e in journal.recover_entries()]
    assert kinds == [
        TX_PREPARED_KIND,
        "EXPERIENCE",
        "EVIDENCE",
        TX_COMMITTED_KIND,
    ]
    assert result.state.sequence == 1
    assert experiences.contains_id("EXP-001")
    assert evidence.contains_id(result.evidence_artifact.snapshot_id)


def test_gold_104_crash_after_prepare_is_fully_recovered(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    journal.append(TX_PREPARED_KIND, transaction_payload(tx))

    report = coordinator.reconciler.reconcile()

    assert report.status == "RECOVERED"
    assert report.recovered_transactions == (tx.tx_id,)
    assert ingestion.state_store.recover() == tx.next_state
    assert experiences.contains_id(tx.experience.experience_id)
    assert evidence.contains_id(tx.evidence_artifact.snapshot_id)


def test_gold_105_crash_after_experience_replays_only_missing_steps(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    journal.append(TX_PREPARED_KIND, transaction_payload(tx))
    experiences.append(tx.experience)

    report = coordinator.reconciler.reconcile()

    assert report.status == "RECOVERED"
    assert experiences.count("CORE8_DECISION") == 1
    assert evidence.contains_id(tx.evidence_artifact.snapshot_id)
    assert ingestion.state_store.recover() == tx.next_state


def test_gold_106_crash_after_evidence_restores_state_and_commit(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    journal.append(TX_PREPARED_KIND, transaction_payload(tx))
    experiences.append(tx.experience)
    evidence.append(tx.evidence_artifact)

    report = coordinator.reconciler.reconcile()

    assert report.status == "RECOVERED"
    assert ingestion.state_store.recover() == tx.next_state
    assert [e.kind for e in journal.recover_entries()][-1] == TX_COMMITTED_KIND


def test_gold_107_crash_after_state_before_commit_only_finishes_marker(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    journal.append(TX_PREPARED_KIND, transaction_payload(tx))
    experiences.append(tx.experience)
    evidence.append(tx.evidence_artifact)
    ingestion.state_store.save(tx.next_state)

    report = coordinator.reconciler.reconcile()

    assert report.status == "RECOVERED"
    assert experiences.count("CORE8_DECISION") == 1
    assert len(evidence.all()) == 1
    assert [e.kind for e in journal.recover_entries()][-1] == TX_COMMITTED_KIND


def test_gold_108_untracked_state_ahead_is_blocked(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    coordinator.commit(tx)
    current = ingestion.state_store.recover()
    ingestion.state_store.save(
        RuntimeState(
            runtime_id=current.runtime_id,
            sequence=current.sequence + 1,
            active_plugins=current.active_plugins,
            checkpoints=current.checkpoints,
            metadata=current.metadata,
        )
    )

    report = coordinator.reconciler.reconcile()

    assert report.status == "RECOVERY_BLOCKED"
    assert report.reason == "RECOVERY_BLOCKED_STATE_AHEAD_UNTRACKED"


def test_gold_109_conflicting_experience_payload_blocks_recovery(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    journal.append(TX_PREPARED_KIND, transaction_payload(tx))
    experiences.append(
        ExperienceRecord(
            experience_id=tx.experience.experience_id,
            skill_id=tx.experience.skill_id,
            skill_version=tx.experience.skill_version,
            success=False,
            metrics={"confidence": 1.0},
            tags=(),
        )
    )

    report = coordinator.reconciler.reconcile()

    assert report.status == "RECOVERY_BLOCKED"
    assert report.reason == "RECOVERY_BLOCKED_EXPERIENCE_CONFLICT"


def test_gold_110_recovery_is_idempotent(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    journal.append(TX_PREPARED_KIND, transaction_payload(tx))

    first = coordinator.reconciler.reconcile()
    second = coordinator.reconciler.reconcile()

    assert first.status == "RECOVERED"
    assert second.status == "CONSISTENT"
    assert experiences.count("CORE8_DECISION") == 1
    assert len(evidence.all()) == 1
    assert sum(1 for e in journal.recover_entries() if e.kind == TX_COMMITTED_KIND) == 1


def test_gold_111_orchestrator_uses_crash_safe_commit_protocol(tmp_path):
    ingestion, journal, experiences, evidence, coordinator = env(tmp_path)
    plugins = DomainPluginRegistry()
    plugins.register(DomainPlugin("core8-plugin", "core8", "1.0.0", True))
    orchestrator = RuntimeOrchestrator(
        plugins=plugins,
        ingestion=ingestion,
        experiences=experiences,
        evidence_builder=EvidenceBuilder(),
        evidence_store=evidence,
        commit_coordinator=coordinator,
    )

    result = orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=decision("EXP-001"),
    )

    assert result.status == "EXECUTED"
    assert result.runtime_sequence == 1
    assert [e.kind for e in journal.recover_entries()] == [
        TX_PREPARED_KIND,
        "EXPERIENCE",
        "EVIDENCE",
        TX_COMMITTED_KIND,
    ]


def test_gold_112_lineage_ahead_restores_missing_runtime_state(tmp_path):
    ingestion, journal, experiences, evidence, coordinator, tx = tx_for(tmp_path)
    coordinator.commit(tx)
    os.unlink(ingestion.state_store.path)

    report = coordinator.reconciler.reconcile()

    assert report.status == "CONSISTENT"
    assert ingestion.state_store.recover() == tx.next_state
