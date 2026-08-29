from joylab_agent_os import (
    CertificationGate,
    EvidenceBuilder,
    ExperienceRecord,
)


def rec(
    i: int,
    *,
    skill_id: str = "INV_ENTRY_001",
    version: str = "1.0.0",
    success: bool = True,
    tags=(),
    confidence: float | None = 85.0,
):
    metrics = {} if confidence is None else {"confidence": confidence}
    return ExperienceRecord(
        experience_id=f"EXP-{i:03d}",
        skill_id=skill_id,
        skill_version=version,
        success=success,
        metrics=metrics,
        tags=tuple(tags),
    )


def test_evidence_builder_gold_008_builds_snapshot_and_passes_gate():
    records = []
    for i in range(20):
        tags = []
        if i < 10:
            tags.append("gold_case")
        if i == 18:
            tags.append("oos_pass")
        if i == 19:
            tags.append("regression_pass")
        records.append(rec(i, tags=tags, confidence=85.0))

    builder = EvidenceBuilder()
    snapshot = builder.build("INV_ENTRY_001", "1.0.0", records)
    evidence = builder.to_certification_evidence(snapshot)
    result = CertificationGate().evaluate(evidence)

    assert snapshot.samples == 20
    assert snapshot.successful_samples == 20
    assert snapshot.gold_cases == 10
    assert snapshot.confidence == 85.0
    assert snapshot.oos_pass is True
    assert snapshot.regression_pass is True
    assert snapshot.hard_gate_violations == 0
    assert result.passed is True


def test_evidence_builder_gold_009_filters_other_skill_versions():
    records = [
        rec(1),
        rec(2, version="2.0.0"),
        rec(3, skill_id="CS_QA_001"),
    ]
    snapshot = EvidenceBuilder().build("INV_ENTRY_001", "1.0.0", records)
    assert snapshot.samples == 1
    assert snapshot.source_experience_ids == ("EXP-001",)


def test_evidence_builder_gold_010_oos_fail_overrides_pass():
    records = [
        rec(1, tags=("oos_pass",)),
        rec(2, tags=("oos_fail",)),
    ]
    snapshot = EvidenceBuilder().build("INV_ENTRY_001", "1.0.0", records)
    assert snapshot.oos_pass is False


def test_evidence_builder_gold_011_regression_fail_overrides_pass():
    records = [
        rec(1, tags=("regression_pass",)),
        rec(2, tags=("regression_fail",)),
    ]
    snapshot = EvidenceBuilder().build("INV_ENTRY_001", "1.0.0", records)
    assert snapshot.regression_pass is False


def test_evidence_builder_gold_012_counts_hard_gate_violations():
    records = [
        rec(1, tags=("hard_gate_violation",)),
        rec(2, tags=("hard_gate_violation",)),
        rec(3),
    ]
    snapshot = EvidenceBuilder().build("INV_ENTRY_001", "1.0.0", records)
    assert snapshot.hard_gate_violations == 2


def test_evidence_builder_gold_013_missing_confidence_is_zero():
    snapshot = EvidenceBuilder().build(
        "INV_ENTRY_001",
        "1.0.0",
        [rec(1, confidence=None)],
    )
    assert snapshot.confidence == 0.0
