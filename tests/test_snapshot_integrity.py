from dataclasses import replace

from joylab_agent_os import EvidenceSnapshot
from joylab_agent_os.snapshot_integrity import seal_snapshot, verify_snapshot


def sample_snapshot():
    return EvidenceSnapshot(
        skill_id="INV_ENTRY_001",
        skill_version="1.0.0",
        samples=20,
        successful_samples=16,
        gold_cases=10,
        confidence=85.0,
        oos_pass=True,
        regression_pass=True,
        hard_gate_violations=0,
        source_experience_ids=("EXP-001", "EXP-002"),
    )


def test_gold_014_snapshot_id_and_hash_are_deterministic():
    a = seal_snapshot(sample_snapshot())
    b = seal_snapshot(sample_snapshot())
    assert a.snapshot_id == b.snapshot_id
    assert a.sha256 == b.sha256
    assert verify_snapshot(a) is True


def test_gold_015_tampered_snapshot_fails_verification():
    artifact = seal_snapshot(sample_snapshot())
    tampered = replace(
        artifact,
        snapshot=replace(artifact.snapshot, samples=21),
    )
    assert verify_snapshot(tampered) is False


def test_gold_016_tampered_hash_fails_verification():
    artifact = seal_snapshot(sample_snapshot())
    tampered = replace(artifact, sha256="0" * 64)
    assert verify_snapshot(tampered) is False
