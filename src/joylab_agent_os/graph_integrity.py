from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .evidence_graph import EvidenceGraph


GRAPH_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class EvidenceGraphSnapshotArtifact:
    schema_version: str
    graph_snapshot_id: str
    sha256: str
    nodes: tuple[dict[str, str], ...]
    edges: tuple[dict[str, str], ...]


def graph_payload(graph: EvidenceGraph) -> dict[str, Any]:
    nodes = tuple(
        {
            "node_id": node.node_id,
            "node_type": node.node_type.value,
            "label": node.label,
        }
        for node in graph.nodes()
    )
    edges = tuple(
        {
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "edge_type": edge.edge_type.value,
        }
        for edge in graph.edges()
    )
    return {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "nodes": list(nodes),
        "edges": list(edges),
    }


def canonical_graph_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def graph_sha256(graph: EvidenceGraph) -> str:
    body = canonical_graph_json(graph_payload(graph)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def graph_snapshot_id(graph: EvidenceGraph) -> str:
    digest = graph_sha256(graph)
    return f"EVG-{digest[:20]}"


def seal_graph(graph: EvidenceGraph) -> EvidenceGraphSnapshotArtifact:
    payload = graph_payload(graph)
    digest = hashlib.sha256(canonical_graph_json(payload).encode("utf-8")).hexdigest()
    return EvidenceGraphSnapshotArtifact(
        schema_version=GRAPH_SCHEMA_VERSION,
        graph_snapshot_id=f"EVG-{digest[:20]}",
        sha256=digest,
        nodes=tuple(payload["nodes"]),
        edges=tuple(payload["edges"]),
    )


def verify_graph_snapshot(artifact: EvidenceGraphSnapshotArtifact) -> bool:
    payload = {
        "schema_version": artifact.schema_version,
        "nodes": list(artifact.nodes),
        "edges": list(artifact.edges),
    }
    canonical = canonical_graph_json(payload)
    expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    expected_id = f"EVG-{expected_hash[:20]}"
    return (
        artifact.schema_version == GRAPH_SCHEMA_VERSION
        and artifact.sha256 == expected_hash
        and artifact.graph_snapshot_id == expected_id
    )


def graph_artifact_to_json(artifact: EvidenceGraphSnapshotArtifact) -> str:
    payload = {
        "schema_version": artifact.schema_version,
        "graph_snapshot_id": artifact.graph_snapshot_id,
        "sha256": artifact.sha256,
        "nodes": list(artifact.nodes),
        "edges": list(artifact.edges),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
