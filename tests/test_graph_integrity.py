from dataclasses import replace

from joylab_agent_os.evidence_graph import build_core8_lineage
from joylab_agent_os.graph_integrity import seal_graph, verify_graph_snapshot


def graph():
    return build_core8_lineage(
        decision_id="DEC-001",
        experience_id="EXP-001",
        evs_id="EVS-11111111111111111111",
        candidate_id="SKC-001",
        certified_skill_id="SKILL-CORE8@1.0.1",
        audit_id="AUD-001",
    )


def test_gold_041_graph_snapshot_is_deterministic():
    a = seal_graph(graph())
    b = seal_graph(graph())
    assert a.graph_snapshot_id == b.graph_snapshot_id
    assert a.sha256 == b.sha256
    assert verify_graph_snapshot(a) is True


def test_gold_042_node_tampering_is_detected():
    artifact = seal_graph(graph())
    nodes = list(artifact.nodes)
    nodes[0] = {**nodes[0], "label": "tampered"}
    tampered = replace(artifact, nodes=tuple(nodes))
    assert verify_graph_snapshot(tampered) is False


def test_gold_043_edge_tampering_is_detected():
    artifact = seal_graph(graph())
    edges = list(artifact.edges)
    edges[0] = {**edges[0], "edge_type": "TAMPERED"}
    tampered = replace(artifact, edges=tuple(edges))
    assert verify_graph_snapshot(tampered) is False


def test_gold_044_hash_tampering_is_detected():
    artifact = seal_graph(graph())
    tampered = replace(artifact, sha256="0" * 64)
    assert verify_graph_snapshot(tampered) is False
