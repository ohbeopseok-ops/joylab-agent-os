import pytest

from joylab_agent_os import SkillRecord, SkillState
from joylab_agent_os.approval_audit import (
    ApprovalAuditLog,
    ApprovalDecision,
)
from joylab_agent_os.candidate_diff import CandidateDiffBuilder
from joylab_agent_os.skill_candidate import SkillCandidateGenerator


def base_skill():
    return SkillRecord(
        skill_id="CORE8_DECISION",
        name="core8-decision",
        domain="investment",
        version="1.0.0",
        state=SkillState.CERTIFIED,
        metadata={"owner": "joylab"},
    )


def candidate():
    return SkillCandidateGenerator().generate(
        base_skill(),
        rationale="Reduce false positives",
        change_summary="Add EVS-backed hard-gate precedence",
    )


def test_gold_030_candidate_diff_is_deterministic():
    builder = CandidateDiffBuilder()
    a = builder.build(base_skill(), candidate())
    b = builder.build(base_skill(), candidate())

    assert a.diff_id == b.diff_id
    assert a.sha256 == b.sha256
    assert a.proposed_version == "1.0.1"


def test_gold_031_diff_rejects_wrong_base_version():
    c = candidate()
    wrong = SkillRecord(
        skill_id=c.skill_id,
        name=c.name,
        domain=c.domain,
        version="0.9.0",
    )
    with pytest.raises(ValueError, match="BASE_VERSION_MISMATCH"):
        CandidateDiffBuilder().build(wrong, c)


def test_gold_032_approval_audit_captures_who_why_evidence_and_diff():
    c = candidate()
    diff = CandidateDiffBuilder().build(base_skill(), c)
    log = ApprovalAuditLog()

    record = log.build_record(
        candidate_id=c.candidate_id,
        skill_id=c.skill_id,
        base_version=c.base_version,
        proposed_version=c.proposed_version,
        actor="joylab-owner",
        decision=ApprovalDecision.APPROVE,
        reason="Gold/OOS/regression gates passed",
        evidence_refs=("EVS-11111111111111111111", "GOLD-023"),
        diff_id=diff.diff_id,
    )
    log.append(record)

    stored = log.for_candidate(c.candidate_id)
    assert len(stored) == 1
    assert stored[0].actor == "joylab-owner"
    assert stored[0].reason == "Gold/OOS/regression gates passed"
    assert stored[0].evidence_refs == ("EVS-11111111111111111111", "GOLD-023")
    assert stored[0].diff_id == diff.diff_id


def test_gold_033_approval_without_evidence_is_blocked():
    c = candidate()
    diff = CandidateDiffBuilder().build(base_skill(), c)

    with pytest.raises(ValueError, match="APPROVAL_REQUIRES_EVIDENCE"):
        ApprovalAuditLog.build_record(
            candidate_id=c.candidate_id,
            skill_id=c.skill_id,
            base_version=c.base_version,
            proposed_version=c.proposed_version,
            actor="joylab-owner",
            decision=ApprovalDecision.APPROVE,
            reason="approve",
            evidence_refs=(),
            diff_id=diff.diff_id,
        )


def test_gold_034_audit_log_is_append_only():
    c = candidate()
    diff = CandidateDiffBuilder().build(base_skill(), c)
    log = ApprovalAuditLog()
    record = log.build_record(
        candidate_id=c.candidate_id,
        skill_id=c.skill_id,
        base_version=c.base_version,
        proposed_version=c.proposed_version,
        actor="joylab-owner",
        decision=ApprovalDecision.REJECT,
        reason="Needs more OOS evidence",
        evidence_refs=(),
        diff_id=diff.diff_id,
    )
    log.append(record)

    with pytest.raises(ValueError, match="AUDIT_ID_ALREADY_EXISTS"):
        log.append(record)
