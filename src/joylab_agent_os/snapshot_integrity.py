from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from .models import EvidenceSnapshot, EvidenceSnapshotArtifact


SCHEMA_VERSION = "1.0"


def snapshot_payload(snapshot: EvidenceSnapshot) -> dict[str, Any]:
    payload = asdict(snapshot)
    payload["source_experience_ids"] = list(snapshot.source_experience_ids)
    return payload


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def snapshot_sha256(snapshot: EvidenceSnapshot) -> str:
    body = canonical_json(snapshot_payload(snapshot)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def snapshot_id(snapshot: EvidenceSnapshot) -> str:
    digest = snapshot_sha256(snapshot)
    return f"EVS-{digest[:20]}"


def seal_snapshot(snapshot: EvidenceSnapshot) -> EvidenceSnapshotArtifact:
    digest = snapshot_sha256(snapshot)
    return EvidenceSnapshotArtifact(
        schema_version=SCHEMA_VERSION,
        snapshot_id=f"EVS-{digest[:20]}",
        sha256=digest,
        snapshot=snapshot,
    )


def verify_snapshot(artifact: EvidenceSnapshotArtifact) -> bool:
    expected_hash = snapshot_sha256(artifact.snapshot)
    expected_id = f"EVS-{expected_hash[:20]}"
    return (
        artifact.schema_version == SCHEMA_VERSION
        and artifact.sha256 == expected_hash
        and artifact.snapshot_id == expected_id
    )


def artifact_to_json(artifact: EvidenceSnapshotArtifact) -> str:
    payload = {
        "schema_version": artifact.schema_version,
        "snapshot_id": artifact.snapshot_id,
        "sha256": artifact.sha256,
        "snapshot": snapshot_payload(artifact.snapshot),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
