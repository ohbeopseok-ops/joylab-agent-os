from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import EvidenceSnapshot, EvidenceSnapshotArtifact, ExperienceRecord
from .snapshot_integrity import seal_snapshot, verify_snapshot


GENESIS_HASH = "0" * 64
JOURNAL_SCHEMA_VERSION = "1.0"
EXPERIENCE_KIND = "EXPERIENCE"
EVIDENCE_KIND = "EVIDENCE"


@dataclass(frozen=True)
class LineageEntry:
    schema_version: str
    sequence: int
    kind: str
    prev_hash: str
    entry_hash: str
    payload: dict[str, Any]


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _entry_hash(
    *,
    sequence: int,
    kind: str,
    prev_hash: str,
    payload: dict[str, Any],
) -> str:
    body = _canonical(
        {
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "sequence": sequence,
            "kind": kind,
            "prev_hash": prev_hash,
            "payload": payload,
        }
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def experience_payload(record: ExperienceRecord) -> dict[str, Any]:
    return {
        "experience_id": record.experience_id,
        "skill_id": record.skill_id,
        "skill_version": record.skill_version,
        "success": record.success,
        "metrics": record.metrics,
        "tags": list(record.tags),
        "created_at": record.created_at.isoformat(),
    }


def experience_from_payload(payload: dict[str, Any]) -> ExperienceRecord:
    try:
        return ExperienceRecord(
            experience_id=str(payload["experience_id"]),
            skill_id=str(payload["skill_id"]),
            skill_version=str(payload["skill_version"]),
            success=bool(payload["success"]),
            metrics={str(k): float(v) for k, v in payload.get("metrics", {}).items()},
            tags=tuple(str(x) for x in payload.get("tags", ())),
            created_at=datetime.fromisoformat(str(payload["created_at"])),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("EXPERIENCE_PAYLOAD_INVALID") from exc


def evidence_payload(artifact: EvidenceSnapshotArtifact) -> dict[str, Any]:
    s = artifact.snapshot
    return {
        "schema_version": artifact.schema_version,
        "snapshot_id": artifact.snapshot_id,
        "sha256": artifact.sha256,
        "snapshot": {
            "skill_id": s.skill_id,
            "skill_version": s.skill_version,
            "samples": s.samples,
            "successful_samples": s.successful_samples,
            "gold_cases": s.gold_cases,
            "confidence": s.confidence,
            "oos_pass": s.oos_pass,
            "regression_pass": s.regression_pass,
            "hard_gate_violations": s.hard_gate_violations,
            "source_experience_ids": list(s.source_experience_ids),
        },
    }


def evidence_from_payload(payload: dict[str, Any]) -> EvidenceSnapshotArtifact:
    try:
        raw = payload["snapshot"]
        snapshot = EvidenceSnapshot(
            skill_id=str(raw["skill_id"]),
            skill_version=str(raw["skill_version"]),
            samples=int(raw["samples"]),
            successful_samples=int(raw["successful_samples"]),
            gold_cases=int(raw["gold_cases"]),
            confidence=float(raw["confidence"]),
            oos_pass=bool(raw["oos_pass"]),
            regression_pass=bool(raw["regression_pass"]),
            hard_gate_violations=int(raw["hard_gate_violations"]),
            source_experience_ids=tuple(str(x) for x in raw["source_experience_ids"]),
        )
        artifact = EvidenceSnapshotArtifact(
            schema_version=str(payload["schema_version"]),
            snapshot_id=str(payload["snapshot_id"]),
            sha256=str(payload["sha256"]),
            snapshot=snapshot,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("EVIDENCE_PAYLOAD_INVALID") from exc
    if not verify_snapshot(artifact):
        raise ValueError("EVIDENCE_ARTIFACT_INTEGRITY_FAILED")
    return artifact


class PersistentLineageJournal:
    """Single-writer append-only, hash-chained JSONL journal."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def recover_entries(self) -> tuple[LineageEntry, ...]:
        if not self.path.exists():
            return ()

        entries: list[LineageEntry] = []
        expected_prev = GENESIS_HASH
        expected_sequence = 1

        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError("LINEAGE_JOURNAL_READ_FAILED") from exc

        if text and not text.endswith("\n"):
            raise ValueError("LINEAGE_JOURNAL_TRUNCATED_TAIL")

        for raw_line in text.splitlines():
            if not raw_line.strip():
                raise ValueError("LINEAGE_JOURNAL_EMPTY_LINE")
            try:
                row = json.loads(raw_line)
                entry = LineageEntry(
                    schema_version=str(row["schema_version"]),
                    sequence=int(row["sequence"]),
                    kind=str(row["kind"]),
                    prev_hash=str(row["prev_hash"]),
                    entry_hash=str(row["entry_hash"]),
                    payload=dict(row["payload"]),
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError("LINEAGE_JOURNAL_CORRUPT_JSON") from exc

            if entry.schema_version != JOURNAL_SCHEMA_VERSION:
                raise ValueError("LINEAGE_SCHEMA_VERSION_MISMATCH")
            if entry.sequence != expected_sequence:
                raise ValueError("LINEAGE_SEQUENCE_MISMATCH")
            if entry.prev_hash != expected_prev:
                raise ValueError("LINEAGE_PREV_HASH_MISMATCH")
            if entry.kind not in {EXPERIENCE_KIND, EVIDENCE_KIND}:
                raise ValueError("LINEAGE_KIND_INVALID")

            expected_hash = _entry_hash(
                sequence=entry.sequence,
                kind=entry.kind,
                prev_hash=entry.prev_hash,
                payload=entry.payload,
            )
            if entry.entry_hash != expected_hash:
                raise ValueError("LINEAGE_ENTRY_HASH_MISMATCH")

            if entry.kind == EXPERIENCE_KIND:
                experience_from_payload(entry.payload)
            else:
                evidence_from_payload(entry.payload)

            entries.append(entry)
            expected_prev = entry.entry_hash
            expected_sequence += 1

        return tuple(entries)

    def append(self, kind: str, payload: dict[str, Any]) -> LineageEntry:
        entries = self.recover_entries()
        sequence = len(entries) + 1
        prev_hash = entries[-1].entry_hash if entries else GENESIS_HASH
        digest = _entry_hash(
            sequence=sequence,
            kind=kind,
            prev_hash=prev_hash,
            payload=payload,
        )
        entry = LineageEntry(
            schema_version=JOURNAL_SCHEMA_VERSION,
            sequence=sequence,
            kind=kind,
            prev_hash=prev_hash,
            entry_hash=digest,
            payload=payload,
        )
        row = {
            "schema_version": entry.schema_version,
            "sequence": entry.sequence,
            "kind": entry.kind,
            "prev_hash": entry.prev_hash,
            "entry_hash": entry.entry_hash,
            "payload": entry.payload,
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            with os.fdopen(fd, "a", encoding="utf-8") as handle:
                handle.write(line)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            raise
        return entry


class PersistentExperienceStore:
    def __init__(self, journal: PersistentLineageJournal | str | Path) -> None:
        self.journal = (
            journal if isinstance(journal, PersistentLineageJournal)
            else PersistentLineageJournal(journal)
        )

    def all(self) -> tuple[ExperienceRecord, ...]:
        return tuple(
            experience_from_payload(e.payload)
            for e in self.journal.recover_entries()
            if e.kind == EXPERIENCE_KIND
        )

    def contains_id(self, experience_id: str) -> bool:
        return any(r.experience_id == experience_id for r in self.all())

    def append(self, record: ExperienceRecord) -> None:
        if self.contains_id(record.experience_id):
            raise ValueError("EXPERIENCE_ID_ALREADY_EXISTS")
        self.journal.append(EXPERIENCE_KIND, experience_payload(record))

    def for_skill(self, skill_id: str) -> tuple[ExperienceRecord, ...]:
        return tuple(r for r in self.all() if r.skill_id == skill_id)

    def count(self, skill_id: str) -> int:
        return sum(1 for r in self.all() if r.skill_id == skill_id)


class PersistentEvidenceStore:
    def __init__(self, journal: PersistentLineageJournal | str | Path) -> None:
        self.journal = (
            journal if isinstance(journal, PersistentLineageJournal)
            else PersistentLineageJournal(journal)
        )

    def all(self) -> tuple[EvidenceSnapshotArtifact, ...]:
        return tuple(
            evidence_from_payload(e.payload)
            for e in self.journal.recover_entries()
            if e.kind == EVIDENCE_KIND
        )

    def contains_id(self, snapshot_id: str) -> bool:
        return any(a.snapshot_id == snapshot_id for a in self.all())

    def append(self, artifact: EvidenceSnapshotArtifact) -> None:
        if not verify_snapshot(artifact):
            raise ValueError("EVIDENCE_ARTIFACT_INTEGRITY_FAILED")
        if self.contains_id(artifact.snapshot_id):
            raise ValueError("EVIDENCE_SNAPSHOT_ALREADY_EXISTS")
        self.journal.append(EVIDENCE_KIND, evidence_payload(artifact))

    def latest_for_skill(
        self,
        skill_id: str,
        skill_version: str,
    ) -> EvidenceSnapshotArtifact | None:
        matches = [
            a for a in self.all()
            if a.snapshot.skill_id == skill_id
            and a.snapshot.skill_version == skill_version
        ]
        return matches[-1] if matches else None

    def rebuild_latest_from_experiences(
        self,
        *,
        skill_id: str,
        skill_version: str,
        experiences: PersistentExperienceStore,
        evidence_builder: Any,
    ) -> EvidenceSnapshotArtifact:
        snapshot = evidence_builder.build(
            skill_id,
            skill_version,
            experiences.all(),
        )
        return seal_snapshot(snapshot)
