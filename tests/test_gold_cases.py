import pytest

from joylab_agent_os import (
    CertificationEvidence,
    CertificationGate,
    ExperienceLogger,
    ExperienceRecord,
    SkillRecord,
    SkillRegistry,
    SkillState,
)
from joylab_agent_os.skill_registry import SkillRegistryError


def passing_evidence(**overrides):
    base = dict(
        samples=20,
        gold_cases=10,
        confidence=80.0,
        oos_pass=True,
        regression_pass=True,
        hard_gate_violations=0,
    )
    base.update(overrides)
    return CertificationEvidence(**base)


def test_gold_001_valid_candidate_certifies():
    result = CertificationGate().evaluate(passing_evidence())
    assert result.passed is True
    assert result.reasons == ()


def test_gold_002_insufficient_samples_blocks():
    result = CertificationGate().evaluate(passing_evidence(samples=19))
    assert result.passed is False
    assert "INSUFFICIENT_SAMPLES" in result.reasons


def test_gold_003_oos_failure_blocks():
    result = CertificationGate().evaluate(passing_evidence(oos_pass=False))
    assert result.passed is False
    assert "OOS_FAILED" in result.reasons


def test_gold_004_regression_failure_blocks():
    result = CertificationGate().evaluate(passing_evidence(regression_pass=False))
    assert result.passed is False
    assert "REGRESSION_FAILED" in result.reasons


def test_gold_005_hard_gate_violation_blocks():
    result = CertificationGate().evaluate(
        passing_evidence(hard_gate_violations=1)
    )
    assert result.passed is False
    assert "HARD_GATE_VIOLATION" in result.reasons


def test_gold_006_certified_version_cannot_be_overwritten():
    registry = SkillRegistry()
    skill = SkillRecord(
        skill_id="INV_ENTRY_001",
        name="foreign-flow-entry",
        domain="investment",
        version="1.0.0",
    )
    registry.register(skill)
    registry.transition(skill.skill_id, skill.version, SkillState.CANDIDATE)
    registry.transition(skill.skill_id, skill.version, SkillState.TESTING)
    registry.transition(skill.skill_id, skill.version, SkillState.CERTIFIED)

    with pytest.raises(SkillRegistryError, match="CERTIFIED_SKILL_IMMUTABLE"):
        registry.register(skill)


def test_gold_007_invalid_lifecycle_jump_is_blocked():
    registry = SkillRegistry()
    skill = SkillRecord(
        skill_id="CS_QA_001",
        name="qa-coaching",
        domain="cs",
        version="0.1.0",
    )
    registry.register(skill)

    with pytest.raises(SkillRegistryError, match="INVALID_TRANSITION"):
        registry.transition(skill.skill_id, skill.version, SkillState.CERTIFIED)


def test_experience_logger_is_append_only_by_id():
    logger = ExperienceLogger()
    rec = ExperienceRecord(
        experience_id="EXP-001",
        skill_id="INV_ENTRY_001",
        skill_version="1.0.0",
        success=True,
    )
    logger.append(rec)
    assert logger.count("INV_ENTRY_001") == 1

    with pytest.raises(ValueError, match="EXPERIENCE_ID_ALREADY_EXISTS"):
        logger.append(rec)
