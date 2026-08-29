import json

import pytest

from joylab_agent_os.runtime_state import (
    RuntimeState,
    RuntimeStateStore,
    seal_runtime_state,
    verify_runtime_state,
)


def state(sequence=7):
    return RuntimeState(
        runtime_id="joylab-main",
        sequence=sequence,
        active_plugins=("core8", "eps_revision"),
        checkpoints={"core8": "DEC-123", "eps_revision": "EPS-55"},
        metadata={"mode": "read_only"},
    )


def test_gold_071_runtime_state_round_trip_survives_restart(tmp_path):
    path = tmp_path / "runtime_state.json"
    store = RuntimeStateStore(path)
    saved = store.save(state())
    recovered = RuntimeStateStore(path).recover()

    assert verify_runtime_state(saved) is True
    assert recovered == state()


def test_gold_072_same_state_has_deterministic_id_and_hash():
    a = seal_runtime_state(state())
    b = seal_runtime_state(state())
    assert a.state_id == b.state_id
    assert a.sha256 == b.sha256


def test_gold_073_tampered_runtime_state_is_blocked(tmp_path):
    path = tmp_path / "runtime_state.json"
    store = RuntimeStateStore(path)
    store.save(state())

    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["state"]["sequence"] = 999
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="RUNTIME_STATE_INTEGRITY_FAILED"):
        store.load()


def test_gold_074_corrupt_json_is_blocked(tmp_path):
    path = tmp_path / "runtime_state.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="RUNTIME_STATE_CORRUPT_JSON"):
        RuntimeStateStore(path).load()


def test_gold_075_missing_state_does_not_fake_recovery(tmp_path):
    with pytest.raises(FileNotFoundError, match="RUNTIME_STATE_NOT_FOUND"):
        RuntimeStateStore(tmp_path / "missing.json").recover()


def test_gold_076_sequence_must_be_non_negative():
    with pytest.raises(ValueError, match="SEQUENCE_MUST_BE_NON_NEGATIVE"):
        seal_runtime_state(state(sequence=-1))
