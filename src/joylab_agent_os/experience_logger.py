from __future__ import annotations

from .models import ExperienceRecord


class ExperienceLogger:
    """In-memory append-only logger for V0.1.

    Persistence adapters are deliberately deferred to V0.2.
    """

    def __init__(self) -> None:
        self._records: list[ExperienceRecord] = []
        self._ids: set[str] = set()

    def append(self, record: ExperienceRecord) -> None:
        if record.experience_id in self._ids:
            raise ValueError("EXPERIENCE_ID_ALREADY_EXISTS")
        self._records.append(record)
        self._ids.add(record.experience_id)

    def for_skill(self, skill_id: str) -> tuple[ExperienceRecord, ...]:
        return tuple(r for r in self._records if r.skill_id == skill_id)

    def count(self, skill_id: str) -> int:
        return sum(1 for r in self._records if r.skill_id == skill_id)

    def all(self) -> tuple[ExperienceRecord, ...]:
        return tuple(self._records)
