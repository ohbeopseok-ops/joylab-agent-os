from joylab_agent_os import (
    CertificationGate,
    EvidenceBuilder,
    ExperienceLogger,
    MemoryRouter,
    MemoryTier,
)
from joylab_agent_os.adapters.core8 import Core8Adapter, Core8Decision
from joylab_agent_os.snapshot_integrity import verify_snapshot


class EvidenceMemoryProvider:
    name = "evidence-memory"
    tier = MemoryTier.EVIDENCE

    def __init__(self):
        self.writes = []

    def recall(self, query):
        return ""

    def write(self, proposal):
        self.writes.append(proposal)


def decision(i: int, **overrides):
    base = dict(
        decision_id=f"CORE8-{i:03d}",
        skill_id="CORE8_DECISION",
        skill_version="0.5.0",
        ticker="005930",
        action="HOLD",
        confidence=85.0,
        success=True,
        is_gold_case=i <= 10,
        oos_pass=i == 19,
        regression_pass=i == 20,
    )
    base.update(overrides)
    return Core8Decision(**base)


def test_gold_022_single_core8_decision_flows_end_to_end_without_fake_certification():
    logger = ExperienceLogger()
    provider = EvidenceMemoryProvider()
    memory = MemoryRouter()
    memory.register_provider(provider)

    Core8Adapter.ingest([decision(1)], logger)
    result = Core8Adapter.run_e2e(
        skill_id="CORE8_DECISION",
        skill_version="0.5.0",
        logger=logger,
        builder=EvidenceBuilder(),
        gate=CertificationGate(),
        memory=memory,
    )

    assert result.artifact.snapshot.samples == 1
    assert verify_snapshot(result.artifact) is True
    assert result.certification.passed is False
    assert "INSUFFICIENT_SAMPLES" in result.certification.reasons
    assert result.memory_write.approved is True
    assert provider.writes[0].source_ref == result.artifact.snapshot_id


def test_gold_023_frozen_core8_batch_can_certify_and_persist_evidence():
    logger = ExperienceLogger()
    provider = EvidenceMemoryProvider()
    memory = MemoryRouter()
    memory.register_provider(provider)

    Core8Adapter.ingest([decision(i) for i in range(1, 21)], logger)
    result = Core8Adapter.run_e2e(
        skill_id="CORE8_DECISION",
        skill_version="0.5.0",
        logger=logger,
        builder=EvidenceBuilder(),
        gate=CertificationGate(),
        memory=memory,
    )

    assert result.artifact.snapshot.samples == 20
    assert result.artifact.snapshot.gold_cases == 10
    assert result.artifact.snapshot.oos_pass is True
    assert result.artifact.snapshot.regression_pass is True
    assert result.certification.passed is True
    assert result.memory_write.approved is True
    assert len(provider.writes) == 1


def test_gold_024_core8_hard_gate_violation_blocks_certification_but_preserves_evidence():
    logger = ExperienceLogger()
    provider = EvidenceMemoryProvider()
    memory = MemoryRouter()
    memory.register_provider(provider)

    decisions = [decision(i) for i in range(1, 21)]
    decisions[-1] = decision(
        20,
        regression_pass=True,
        hard_gate_violation=True,
    )
    Core8Adapter.ingest(decisions, logger)
    result = Core8Adapter.run_e2e(
        skill_id="CORE8_DECISION",
        skill_version="0.5.0",
        logger=logger,
        builder=EvidenceBuilder(),
        gate=CertificationGate(),
        memory=memory,
    )

    assert result.certification.passed is False
    assert "HARD_GATE_VIOLATION" in result.certification.reasons
    assert result.memory_write.approved is True
