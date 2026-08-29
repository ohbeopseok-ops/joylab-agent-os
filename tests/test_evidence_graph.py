import pytest

from joylab_agent_os.evidence_graph import (
    EvidenceGraph,
    GraphEdge,
    GraphEdgeType,
    GraphNode,
    GraphNodeType,
    build_core8_lineage,
)


def test_gold_035_core8_full_lineage_path_is_available():
    graph = build_core8_lineage(
        decision_id="DEC-001",
        experience_id="EXP-001",
        evs_id="EVS-11111111111111111111",
        candidate_id="SKC-001",
        certified_skill_id="SKILL-CORE8@1.0.1",
        audit_id="AUD-001",
    )

    assert graph.lineage_path(
        "DEC-001",
        "SKILL-CORE8@1.0.1",
    ) == (
        "DEC-001",
        "EXP-001",
        "EVS-11111111111111111111",
        "SKC-001",
        "SKILL-CORE8@1.0.1",
    )


def test_gold_036_certified_skill_provenance_is_complete():
    graph = build_core8_lineage(
        decision_id="DEC-001",
        experience_id="EXP-001",
        evs_id="EVS-11111111111111111111",
        candidate_id="SKC-001",
        certified_skill_id="SKILL-CORE8@1.0.1",
        audit_id="AUD-001",
    )
    assert graph.provenance_complete(
        "SKILL-CORE8@1.0.1",
        required_types=(
            GraphNodeType.DECISION,
            GraphNodeType.EXPERIENCE,
            GraphNodeType.EVIDENCE_SNAPSHOT,
            GraphNodeType.SKILL_CANDIDATE,
            GraphNodeType.APPROVAL_AUDIT,
        ),
    ) is True


def test_gold_037_missing_audit_makes_strict_provenance_incomplete():
    graph = build_core8_lineage(
        decision_id="DEC-001",
        experience_id="EXP-001",
        evs_id="EVS-11111111111111111111",
        candidate_id="SKC-001",
        certified_skill_id="SKILL-CORE8@1.0.1",
    )
    assert graph.provenance_complete(
        "SKILL-CORE8@1.0.1",
        required_types=(GraphNodeType.APPROVAL_AUDIT,),
    ) is False


def test_gold_038_orphan_nodes_are_detected():
    graph = EvidenceGraph()
    graph.add_node(GraphNode("EXP-1", GraphNodeType.EXPERIENCE))
    graph.add_node(GraphNode("EVS-1", GraphNodeType.EVIDENCE_SNAPSHOT))
    graph.add_node(GraphNode("ORPHAN", GraphNodeType.SKILL_CANDIDATE))
    graph.add_edge(GraphEdge("EXP-1", "EVS-1", GraphEdgeType.SEALED_AS))

    assert tuple(n.node_id for n in graph.orphan_nodes()) == ("ORPHAN",)


def test_gold_039_edge_with_missing_endpoint_is_blocked():
    graph = EvidenceGraph()
    graph.add_node(GraphNode("EXP-1", GraphNodeType.EXPERIENCE))

    with pytest.raises(ValueError, match="TARGET_NODE_NOT_FOUND"):
        graph.add_edge(
            GraphEdge("EXP-1", "EVS-MISSING", GraphEdgeType.SEALED_AS)
        )


def test_gold_040_duplicate_edge_is_blocked():
    graph = EvidenceGraph()
    graph.add_node(GraphNode("EXP-1", GraphNodeType.EXPERIENCE))
    graph.add_node(GraphNode("EVS-1", GraphNodeType.EVIDENCE_SNAPSHOT))
    edge = GraphEdge("EXP-1", "EVS-1", GraphEdgeType.SEALED_AS)
    graph.add_edge(edge)

    with pytest.raises(ValueError, match="EDGE_ALREADY_EXISTS"):
        graph.add_edge(edge)
