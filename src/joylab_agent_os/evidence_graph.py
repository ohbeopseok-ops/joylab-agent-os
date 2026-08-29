from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum


class GraphNodeType(str, Enum):
    DECISION = "DECISION"
    EXPERIENCE = "EXPERIENCE"
    EVIDENCE_SNAPSHOT = "EVIDENCE_SNAPSHOT"
    SKILL_CANDIDATE = "SKILL_CANDIDATE"
    CERTIFIED_SKILL = "CERTIFIED_SKILL"
    APPROVAL_AUDIT = "APPROVAL_AUDIT"


class GraphEdgeType(str, Enum):
    PRODUCED = "PRODUCED"
    SEALED_AS = "SEALED_AS"
    SUPPORTS = "SUPPORTS"
    PROPOSES = "PROPOSES"
    CERTIFIED_AS = "CERTIFIED_AS"
    APPROVED_BY = "APPROVED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    VALIDATED_BY = "VALIDATED_BY"


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: GraphNodeType
    label: str = ""


@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: GraphEdgeType


class EvidenceGraph:
    """Typed provenance graph for JoyLab governed-learning lineage."""

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: set[GraphEdge] = set()

    def add_node(self, node: GraphNode) -> None:
        existing = self._nodes.get(node.node_id)
        if existing is not None and existing != node:
            raise ValueError("NODE_ID_CONFLICT")
        self._nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source_id not in self._nodes:
            raise ValueError("SOURCE_NODE_NOT_FOUND")
        if edge.target_id not in self._nodes:
            raise ValueError("TARGET_NODE_NOT_FOUND")
        if edge.source_id == edge.target_id:
            raise ValueError("SELF_EDGE_NOT_ALLOWED")
        if edge in self._edges:
            raise ValueError("EDGE_ALREADY_EXISTS")
        self._edges.add(edge)

    def node(self, node_id: str) -> GraphNode:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise ValueError("NODE_NOT_FOUND") from exc

    def edges(self) -> tuple[GraphEdge, ...]:
        return tuple(sorted(
            self._edges,
            key=lambda e: (e.source_id, e.target_id, e.edge_type.value),
        ))

    def orphan_nodes(self) -> tuple[GraphNode, ...]:
        connected: set[str] = set()
        for edge in self._edges:
            connected.add(edge.source_id)
            connected.add(edge.target_id)
        return tuple(
            node for node_id, node in sorted(self._nodes.items())
            if node_id not in connected
        )

    def lineage_path(self, source_id: str, target_id: str) -> tuple[str, ...]:
        if source_id not in self._nodes or target_id not in self._nodes:
            raise ValueError("NODE_NOT_FOUND")

        adjacency: dict[str, list[str]] = {}
        for edge in self._edges:
            adjacency.setdefault(edge.source_id, []).append(edge.target_id)

        queue = deque([(source_id, (source_id,))])
        visited = {source_id}
        while queue:
            current, path = queue.popleft()
            if current == target_id:
                return path
            for nxt in sorted(adjacency.get(current, [])):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + (nxt,)))
        return ()

    def provenance_complete(
        self,
        target_id: str,
        *,
        required_types: tuple[GraphNodeType, ...],
    ) -> bool:
        if target_id not in self._nodes:
            raise ValueError("NODE_NOT_FOUND")

        reverse: dict[str, list[str]] = {}
        for edge in self._edges:
            reverse.setdefault(edge.target_id, []).append(edge.source_id)

        seen = {target_id}
        queue = deque([target_id])
        found = {self._nodes[target_id].node_type}
        while queue:
            current = queue.popleft()
            for prev in reverse.get(current, []):
                if prev not in seen:
                    seen.add(prev)
                    found.add(self._nodes[prev].node_type)
                    queue.append(prev)

        return all(t in found for t in required_types)


def build_core8_lineage(
    *,
    decision_id: str,
    experience_id: str,
    evs_id: str,
    candidate_id: str,
    certified_skill_id: str,
    audit_id: str | None = None,
) -> EvidenceGraph:
    graph = EvidenceGraph()

    nodes = [
        GraphNode(decision_id, GraphNodeType.DECISION, "Core8 Decision"),
        GraphNode(experience_id, GraphNodeType.EXPERIENCE, "Experience"),
        GraphNode(evs_id, GraphNodeType.EVIDENCE_SNAPSHOT, "Evidence Snapshot"),
        GraphNode(candidate_id, GraphNodeType.SKILL_CANDIDATE, "Skill Candidate"),
        GraphNode(certified_skill_id, GraphNodeType.CERTIFIED_SKILL, "Certified Skill"),
    ]
    if audit_id:
        nodes.append(GraphNode(audit_id, GraphNodeType.APPROVAL_AUDIT, "Approval Audit"))

    for node in nodes:
        graph.add_node(node)

    graph.add_edge(GraphEdge(decision_id, experience_id, GraphEdgeType.PRODUCED))
    graph.add_edge(GraphEdge(experience_id, evs_id, GraphEdgeType.SEALED_AS))
    graph.add_edge(GraphEdge(evs_id, candidate_id, GraphEdgeType.SUPPORTS))
    graph.add_edge(GraphEdge(candidate_id, certified_skill_id, GraphEdgeType.CERTIFIED_AS))
    if audit_id:
        graph.add_edge(GraphEdge(candidate_id, audit_id, GraphEdgeType.APPROVED_BY))
        graph.add_edge(GraphEdge(audit_id, certified_skill_id, GraphEdgeType.VALIDATED_BY))

    return graph
