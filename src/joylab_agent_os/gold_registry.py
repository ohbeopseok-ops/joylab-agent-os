from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ALLOWED_STATUSES = {"CERTIFIED", "CANDIDATE", "INVALID"}


@dataclass(frozen=True)
class GoldCaseEntry:
    id: str
    status: str
    component: str
    source_test: str
    provenance: dict


class GoldCaseRegistry:
    def __init__(self, entries: Iterable[GoldCaseEntry]) -> None:
        self._entries = tuple(entries)
        ids = [e.id for e in self._entries]
        if len(ids) != len(set(ids)):
            raise ValueError("DUPLICATE_GOLD_ID")
        bad = [e.status for e in self._entries if e.status not in ALLOWED_STATUSES]
        if bad:
            raise ValueError("INVALID_GOLD_STATUS")

    @classmethod
    def from_json(cls, path: str | Path) -> "GoldCaseRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        entries = [
            GoldCaseEntry(
                id=row["id"],
                status=row["status"],
                component=row["component"],
                source_test=row["source_test"],
                provenance=row["provenance"],
            )
            for row in payload["cases"]
        ]
        return cls(entries)

    def entries(self) -> tuple[GoldCaseEntry, ...]:
        return self._entries

    def get(self, gold_id: str) -> GoldCaseEntry:
        for entry in self._entries:
            if entry.id == gold_id:
                return entry
        raise ValueError("GOLD_CASE_NOT_FOUND")

    def by_status(self, status: str) -> tuple[GoldCaseEntry, ...]:
        if status not in ALLOWED_STATUSES:
            raise ValueError("INVALID_GOLD_STATUS")
        return tuple(e for e in self._entries if e.status == status)

    def certified_ids(self) -> tuple[str, ...]:
        return tuple(e.id for e in self.by_status("CERTIFIED"))

    def validate_contiguous(self, start: int = 1) -> bool:
        expected = start
        for entry in sorted(self._entries, key=lambda e: int(e.id.split("_")[1])):
            if entry.id != f"GOLD_{expected:03d}":
                return False
            expected += 1
        return True

    def provenance_complete(self) -> bool:
        for entry in self._entries:
            p = entry.provenance
            if not p.get("repository"):
                return False
            if not p.get("pull_request"):
                return False
            if not p.get("evidence_refs"):
                return False
        return True
