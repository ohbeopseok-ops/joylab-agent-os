import pytest

from joylab_agent_os.adapter_registry import AdapterRegistry
from joylab_agent_os.adapters.core8 import Core8Adapter, Core8Decision
from joylab_agent_os.runtime_state import RuntimeStateStore
from joylab_agent_os.scheduled_ingestion import ScheduleSpec, ScheduledIngestionRunner


def registry():
    r = AdapterRegistry()
    r.register("core8", Core8Decision, Core8Adapter.to_experience)
    return r


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


def spec(**overrides):
    values = dict(
        schedule_id="core8-hourly",
        domain="core8",
        interval_seconds=3600,
        enabled=True,
    )
    values.update(overrides)
    return ScheduleSpec(**values)


def test_gold_077_due_run_executes_and_advances_checkpoint(tmp_path):
    store = RuntimeStateStore(tmp_path / "state.json")
    runner = ScheduledIngestionRunner(state_store=store, adapters=registry())

    result = runner.run(
        spec=spec(), run_key="RUN-001", now_epoch=1000, signal=signal()
    )

    assert result.status == "EXECUTED"
    assert result.state.sequence == 1
    assert result.state.checkpoints["core8"] == "DEC-001"


def test_gold_078_duplicate_is_blocked_after_restart(tmp_path):
    path = tmp_path / "state.json"
    first = ScheduledIngestionRunner(
        state_store=RuntimeStateStore(path), adapters=registry()
    )
    first.run(spec=spec(), run_key="RUN-001", now_epoch=1000, signal=signal())

    restarted = ScheduledIngestionRunner(
        state_store=RuntimeStateStore(path), adapters=registry()
    )
    result = restarted.run(
        spec=spec(), run_key="RUN-001", now_epoch=5000, signal=signal("DEC-002")
    )

    assert result.status == "DUPLICATE"
    assert result.state.sequence == 1
    assert result.state.checkpoints["core8"] == "DEC-001"


def test_gold_079_not_due_does_not_advance_state(tmp_path):
    store = RuntimeStateStore(tmp_path / "state.json")
    runner = ScheduledIngestionRunner(state_store=store, adapters=registry())
    runner.run(spec=spec(), run_key="RUN-001", now_epoch=1000, signal=signal())

    result = runner.run(
        spec=spec(), run_key="RUN-002", now_epoch=2000, signal=signal("DEC-002")
    )

    assert result.status == "NOT_DUE"
    assert store.recover().sequence == 1
    assert store.recover().checkpoints["core8"] == "DEC-001"


def test_gold_080_due_after_interval_executes_and_increments_sequence(tmp_path):
    store = RuntimeStateStore(tmp_path / "state.json")
    runner = ScheduledIngestionRunner(state_store=store, adapters=registry())
    runner.run(spec=spec(), run_key="RUN-001", now_epoch=1000, signal=signal())

    result = runner.run(
        spec=spec(), run_key="RUN-002", now_epoch=4600, signal=signal("DEC-002")
    )

    assert result.status == "EXECUTED"
    assert result.state.sequence == 2
    assert result.state.checkpoints["core8"] == "DEC-002"


def test_gold_081_adapter_failure_never_advances_checkpoint(tmp_path):
    r = AdapterRegistry()

    def fail(_):
        raise RuntimeError("adapter failed")

    r.register("core8", Core8Decision, fail)
    store = RuntimeStateStore(tmp_path / "state.json")
    runner = ScheduledIngestionRunner(state_store=store, adapters=r)

    with pytest.raises(RuntimeError, match="adapter failed"):
        runner.run(spec=spec(), run_key="RUN-001", now_epoch=1000, signal=signal())

    with pytest.raises(FileNotFoundError):
        store.recover()


def test_gold_082_disabled_schedule_does_not_persist_state(tmp_path):
    store = RuntimeStateStore(tmp_path / "state.json")
    runner = ScheduledIngestionRunner(state_store=store, adapters=registry())

    result = runner.run(
        spec=spec(enabled=False),
        run_key="RUN-001",
        now_epoch=1000,
        signal=signal(),
    )

    assert result.status == "DISABLED"
    assert result.state.sequence == 0
    with pytest.raises(FileNotFoundError):
        store.recover()


def test_gold_083_invalid_interval_is_blocked(tmp_path):
    runner = ScheduledIngestionRunner(
        state_store=RuntimeStateStore(tmp_path / "state.json"),
        adapters=registry(),
    )
    with pytest.raises(ValueError, match="INTERVAL_MUST_BE_POSITIVE"):
        runner.run(
            spec=spec(interval_seconds=0),
            run_key="RUN-001",
            now_epoch=1000,
            signal=signal(),
        )
