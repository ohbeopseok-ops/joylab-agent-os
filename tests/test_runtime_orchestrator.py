import pytest

from joylab_agent_os.adapter_registry import (
    AdapterRegistry,
    DomainPlugin,
    DomainPluginRegistry,
)
from joylab_agent_os.adapters.core8 import Core8Adapter, Core8Decision
from joylab_agent_os.evidence_builder import EvidenceBuilder
from joylab_agent_os.experience_logger import ExperienceLogger
from joylab_agent_os.runtime_orchestrator import RuntimeOrchestrator
from joylab_agent_os.runtime_state import RuntimeStateStore
from joylab_agent_os.scheduled_ingestion import ScheduleSpec, ScheduledIngestionRunner
from joylab_agent_os.snapshot_integrity import verify_snapshot


def signal(decision_id="DEC-001"):
    return Core8Decision(
        decision_id=decision_id,
        skill_id="CORE8_DECISION",
        skill_version="1.0.0",
        ticker="005930",
        action="HOLD",
        confidence=88.0,
        success=True,
    )


def schedule(**overrides):
    values = dict(
        schedule_id="core8-hourly",
        domain="core8",
        interval_seconds=3600,
        enabled=True,
    )
    values.update(overrides)
    return ScheduleSpec(**values)


def build(tmp_path, *, plugin_enabled=True, adapter=None):
    adapters = AdapterRegistry()
    adapters.register("core8", Core8Decision, adapter or Core8Adapter.to_experience)

    plugins = DomainPluginRegistry()
    plugins.register(DomainPlugin("core8-plugin", "core8", "1.0.0", plugin_enabled))

    ingestion = ScheduledIngestionRunner(
        state_store=RuntimeStateStore(tmp_path / "runtime.json"),
        adapters=adapters,
    )
    logger = ExperienceLogger()
    orchestrator = RuntimeOrchestrator(
        plugins=plugins,
        ingestion=ingestion,
        experiences=logger,
        evidence_builder=EvidenceBuilder(),
    )
    return orchestrator, ingestion, logger


def test_gold_084_enabled_plugin_executes_full_path_to_evs(tmp_path):
    orchestrator, _, logger = build(tmp_path)

    result = orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal(),
    )

    assert result.status == "EXECUTED"
    assert result.runtime_sequence == 1
    assert result.experience is not None
    assert result.evidence is not None
    assert result.evidence.source_experience_ids == ("DEC-001",)
    assert result.evidence_artifact is not None
    assert verify_snapshot(result.evidence_artifact) is True
    assert logger.count("CORE8_DECISION") == 1


def test_gold_085_disabled_plugin_blocks_before_state_and_evidence(tmp_path):
    orchestrator, ingestion, logger = build(tmp_path, plugin_enabled=False)

    result = orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal(),
    )

    assert result.status == "PLUGIN_DISABLED"
    assert result.evidence_artifact is None
    assert logger.all() == ()
    with pytest.raises(FileNotFoundError):
        ingestion.state_store.recover()


def test_gold_086_plugin_schedule_domain_mismatch_is_blocked(tmp_path):
    orchestrator, ingestion, logger = build(tmp_path)

    with pytest.raises(ValueError, match="PLUGIN_SCHEDULE_DOMAIN_MISMATCH"):
        orchestrator.execute(
            plugin_id="core8-plugin",
            schedule=schedule(domain="eps_revision"),
            run_key="RUN-001",
            now_epoch=1000,
            signal=signal(),
        )

    assert logger.all() == ()
    with pytest.raises(FileNotFoundError):
        ingestion.state_store.recover()


def test_gold_087_duplicate_run_creates_no_second_evidence(tmp_path):
    orchestrator, _, logger = build(tmp_path)
    orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal(),
    )

    result = orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=5000,
        signal=signal("DEC-002"),
    )

    assert result.status == "DUPLICATE"
    assert result.evidence_artifact is None
    assert logger.count("CORE8_DECISION") == 1


def test_gold_088_not_due_creates_no_new_experience_or_evidence(tmp_path):
    orchestrator, _, logger = build(tmp_path)
    orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal(),
    )

    result = orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-002",
        now_epoch=2000,
        signal=signal("DEC-002"),
    )

    assert result.status == "NOT_DUE"
    assert result.evidence_artifact is None
    assert logger.count("CORE8_DECISION") == 1


def test_gold_089_adapter_failure_leaves_state_and_evidence_untouched(tmp_path):
    def fail(_):
        raise RuntimeError("adapter failed")

    orchestrator, ingestion, logger = build(tmp_path, adapter=fail)

    with pytest.raises(RuntimeError, match="adapter failed"):
        orchestrator.execute(
            plugin_id="core8-plugin",
            schedule=schedule(),
            run_key="RUN-001",
            now_epoch=1000,
            signal=signal(),
        )

    assert logger.all() == ()
    with pytest.raises(FileNotFoundError):
        ingestion.state_store.recover()


def test_gold_090_second_success_extends_evidence_lineage(tmp_path):
    orchestrator, _, logger = build(tmp_path)
    orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal("DEC-001"),
    )
    result = orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-002",
        now_epoch=4600,
        signal=signal("DEC-002"),
    )

    assert result.status == "EXECUTED"
    assert result.runtime_sequence == 2
    assert result.evidence is not None
    assert result.evidence.samples == 2
    assert result.evidence.source_experience_ids == ("DEC-001", "DEC-002")
    assert logger.count("CORE8_DECISION") == 2


def test_gold_091_duplicate_experience_id_never_advances_runtime_state(tmp_path):
    orchestrator, ingestion, logger = build(tmp_path)
    orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal("DEC-SAME"),
    )

    with pytest.raises(ValueError, match="EXPERIENCE_ID_ALREADY_EXISTS"):
        orchestrator.execute(
            plugin_id="core8-plugin",
            schedule=schedule(),
            run_key="RUN-002",
            now_epoch=4600,
            signal=signal("DEC-SAME"),
        )

    state = ingestion.state_store.recover()
    assert state.sequence == 1
    assert state.checkpoints["core8"] == "DEC-SAME"
    assert logger.count("CORE8_DECISION") == 1


def test_gold_092_duplicate_schedule_does_not_call_adapter_again(tmp_path):
    calls = {"count": 0}

    def counted(value):
        calls["count"] += 1
        return Core8Adapter.to_experience(value)

    orchestrator, _, logger = build(tmp_path, adapter=counted)
    orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal("DEC-001"),
    )
    result = orchestrator.execute(
        plugin_id="core8-plugin",
        schedule=schedule(),
        run_key="RUN-001",
        now_epoch=5000,
        signal=signal("DEC-002"),
    )

    assert result.status == "DUPLICATE"
    assert calls["count"] == 1
    assert logger.count("CORE8_DECISION") == 1
