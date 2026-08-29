from __future__ import annotations

from dataclasses import replace

from .models import SkillRecord, SkillState


class SkillRegistryError(ValueError):
    pass


class SkillRegistry:
    _ALLOWED = {
        SkillState.DISCOVERED: {SkillState.CANDIDATE},
        SkillState.CANDIDATE: {SkillState.TESTING},
        SkillState.TESTING: {SkillState.CERTIFIED, SkillState.DEPRECATED},
        SkillState.CERTIFIED: {SkillState.DEPRECATED},
        SkillState.DEPRECATED: set(),
    }

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], SkillRecord] = {}

    def register(self, skill: SkillRecord) -> SkillRecord:
        key = (skill.skill_id, skill.version)
        existing = self._records.get(key)
        if existing is not None:
            if existing.state is SkillState.CERTIFIED:
                raise SkillRegistryError("CERTIFIED_SKILL_IMMUTABLE")
            raise SkillRegistryError("SKILL_VERSION_ALREADY_EXISTS")
        self._records[key] = skill
        return skill

    def get(self, skill_id: str, version: str) -> SkillRecord:
        try:
            return self._records[(skill_id, version)]
        except KeyError as exc:
            raise SkillRegistryError("SKILL_NOT_FOUND") from exc

    def transition(
        self,
        skill_id: str,
        version: str,
        target: SkillState,
    ) -> SkillRecord:
        current = self.get(skill_id, version)
        if target not in self._ALLOWED[current.state]:
            raise SkillRegistryError(
                f"INVALID_TRANSITION:{current.state.value}->{target.value}"
            )
        updated = replace(current, state=target)
        self._records[(skill_id, version)] = updated
        return updated

    def all(self) -> tuple[SkillRecord, ...]:
        return tuple(self._records.values())
