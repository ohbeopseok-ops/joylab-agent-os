from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .adapter_registry import AdapterRegistry
from .models import ExperienceRecord
from .runtime_state import RuntimeState, RuntimeStateStore


@dataclass(frozen=True)
class ScheduleSpec:
    schedule_id: str
    domain: str
    interval_seconds: int
    enabled: bool = True


@dataclass(frozen=True)
class ScheduledIngestionResult:
    status: str
    experience: ExperienceRecord | None
    state: RuntimeState


class ScheduledIngestionRunner:
    """Deterministic checkpoint-aware scheduled ingestion.

    The caller supplies now_epoch. The runner does not read wall-clock time,
    which keeps replay and Gold Case evaluation deterministic.
    """

    MAX_RUN_HISTORY = 100

    def __init__(
        self,
        *,
        state_store: RuntimeStateStore,
        adapters: AdapterRegistry,
        runtime_id: str = "joylab-main",
    ) -> None:
        self.state_store = state_store
        self.adapters = adapters
        self.runtime_id = runtime_id

    def _state(self) -> RuntimeState:
        try:
            return self.state_store.recover()
        except FileNotFoundError:
            return RuntimeState(runtime_id=self.runtime_id, sequence=0)

    @staticmethod
    def _validate(spec: ScheduleSpec, run_key: str, now_epoch: int) -> None:
        if not spec.schedule_id.strip():
            raise ValueError("SCHEDULE_ID_REQUIRED")
        if not spec.domain.strip():
            raise ValueError("SCHEDULE_DOMAIN_REQUIRED")
        if spec.interval_seconds <= 0:
            raise ValueError("INTERVAL_MUST_BE_POSITIVE")
        if not run_key.strip():
            raise ValueError("RUN_KEY_REQUIRED")
        if now_epoch < 0:
            raise ValueError("NOW_EPOCH_MUST_BE_NON_NEGATIVE")

    @staticmethod
    def _history(state: RuntimeState) -> dict[str, list[str]]:
        raw = state.metadata.get("scheduled_ingestion_runs", {})
        if not isinstance(raw, dict):
            raise ValueError("SCHEDULE_HISTORY_INVALID")
        return {
            str(schedule_id): [str(x) for x in run_keys]
            for schedule_id, run_keys in raw.items()
        }

    @staticmethod
    def _last_success(state: RuntimeState) -> dict[str, int]:
        raw = state.metadata.get("schedule_last_success_epoch", {})
        if not isinstance(raw, dict):
            raise ValueError("SCHEDULE_LAST_SUCCESS_INVALID")
        return {str(k): int(v) for k, v in raw.items()}

    def is_due(self, spec: ScheduleSpec, state: RuntimeState, now_epoch: int) -> bool:
        last = self._last_success(state).get(spec.schedule_id)
        if last is None:
            return True
        return now_epoch >= last + spec.interval_seconds

    def run(
        self,
        *,
        spec: ScheduleSpec,
        run_key: str,
        now_epoch: int,
        signal: Any,
    ) -> ScheduledIngestionResult:
        self._validate(spec, run_key, now_epoch)
        state = self._state()
        history = self._history(state)
        already_seen = run_key in history.get(spec.schedule_id, [])

        if already_seen:
            return ScheduledIngestionResult("DUPLICATE", None, state)

        if not spec.enabled:
            return ScheduledIngestionResult("DISABLED", None, state)

        if not self.is_due(spec, state, now_epoch):
            return ScheduledIngestionResult("NOT_DUE", None, state)

        # Route before mutating state. If the adapter fails, no checkpoint advances.
        experience = self.adapters.route(spec.domain, signal)

        next_history = {k: list(v) for k, v in history.items()}
        schedule_runs = next_history.setdefault(spec.schedule_id, [])
        schedule_runs.append(run_key)
        if len(schedule_runs) > self.MAX_RUN_HISTORY:
            del schedule_runs[:-self.MAX_RUN_HISTORY]

        next_last = self._last_success(state)
        next_last[spec.schedule_id] = now_epoch

        checkpoints = dict(state.checkpoints)
        checkpoints[spec.domain.lower()] = experience.experience_id

        metadata = dict(state.metadata)
        metadata["scheduled_ingestion_runs"] = next_history
        metadata["schedule_last_success_epoch"] = next_last

        next_plugins = tuple(sorted(set(state.active_plugins) | {spec.domain.lower()}))
        next_state = RuntimeState(
            runtime_id=state.runtime_id,
            sequence=state.sequence + 1,
            active_plugins=next_plugins,
            checkpoints=checkpoints,
            metadata=metadata,
        )
        self.state_store.save(next_state)
        return ScheduledIngestionResult("EXECUTED", experience, next_state)
