from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


RUNTIME_STATE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class RuntimeState:
    runtime_id: str
    sequence: int
    active_plugins: tuple[str, ...] = ()
    checkpoints: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeStateEnvelope:
    schema_version: str
    state_id: str
    sha256: str
    state: RuntimeState


def runtime_state_payload(state: RuntimeState) -> dict[str, Any]:
    return {
        "runtime_id": state.runtime_id,
        "sequence": state.sequence,
        "active_plugins": list(state.active_plugins),
        "checkpoints": state.checkpoints,
        "metadata": state.metadata,
    }


def runtime_state_from_payload(payload: dict[str, Any]) -> RuntimeState:
    try:
        return RuntimeState(
            runtime_id=str(payload["runtime_id"]),
            sequence=int(payload["sequence"]),
            active_plugins=tuple(str(x) for x in payload.get("active_plugins", ())),
            checkpoints={str(k): str(v) for k, v in payload.get("checkpoints", {}).items()},
            metadata=dict(payload.get("metadata", {})),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("RUNTIME_STATE_INVALID_SHAPE") from exc


def canonical_state_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def runtime_state_sha256(state: RuntimeState) -> str:
    body = canonical_state_json(runtime_state_payload(state)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def seal_runtime_state(state: RuntimeState) -> RuntimeStateEnvelope:
    if not state.runtime_id.strip():
        raise ValueError("RUNTIME_ID_REQUIRED")
    if state.sequence < 0:
        raise ValueError("SEQUENCE_MUST_BE_NON_NEGATIVE")
    digest = runtime_state_sha256(state)
    return RuntimeStateEnvelope(
        schema_version=RUNTIME_STATE_SCHEMA_VERSION,
        state_id=f"RTS-{digest[:20]}",
        sha256=digest,
        state=state,
    )


def verify_runtime_state(envelope: RuntimeStateEnvelope) -> bool:
    digest = runtime_state_sha256(envelope.state)
    return (
        envelope.schema_version == RUNTIME_STATE_SCHEMA_VERSION
        and envelope.sha256 == digest
        and envelope.state_id == f"RTS-{digest[:20]}"
    )


class RuntimeStateStore:
    """Atomic JSON persistence for non-evidence runtime state.

    This store never rewrites EVS/EVG artifacts or approval history.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, state: RuntimeState) -> RuntimeStateEnvelope:
        envelope = seal_runtime_state(state)
        payload = {
            "schema_version": envelope.schema_version,
            "state_id": envelope.state_id,
            "sha256": envelope.sha256,
            "state": runtime_state_payload(envelope.state),
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            dir=self.path.parent,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise
        return envelope

    def load(self) -> RuntimeStateEnvelope:
        if not self.path.exists():
            raise FileNotFoundError("RUNTIME_STATE_NOT_FOUND")
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("RUNTIME_STATE_CORRUPT_JSON") from exc

        try:
            state_payload = payload["state"]
            state = runtime_state_from_payload(state_payload)
            envelope = RuntimeStateEnvelope(
                schema_version=payload["schema_version"],
                state_id=payload["state_id"],
                sha256=payload["sha256"],
                state=state,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("RUNTIME_STATE_INVALID_SHAPE") from exc

        if not verify_runtime_state(envelope):
            raise ValueError("RUNTIME_STATE_INTEGRITY_FAILED")
        return envelope

    def recover(self) -> RuntimeState:
        return self.load().state
