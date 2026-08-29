from joylab_agent_os import SkillRecord, SkillRegistry, SkillState
from joylab_agent_os.skill_candidate import SkillCandidateGenerator
from joylab_agent_os.skill_curator import SkillCurator


def certified_skill(registry: SkillRegistry) -> SkillRecord:
    skill = SkillRecord(
        skill_id="CORE8_DECISION",
        name="core8-decision",
        domain="investment",
        version="1.0.0",
    )
    registry.register(skill)
    registry.transition(skill.skill_id, skill.version, SkillState.CANDIDATE)
    registry.transition(skill.skill_id, skill.version, SkillState.TESTING)
    return registry.transition(skill.skill_id, skill.version, SkillState.CERTIFIED)


def test_gold_025_candidate_generation_is_deterministic_and_versioned():
    base = SkillRecord(
        skill_id="CORE8_DECISION",
        name="core8-decision",
        domain="investment",
        version="1.0.0",
        state=SkillState.CERTIFIED,
    )
    generator = SkillCandidateGenerator()

    a = generator.generate(
        base,
        rationale="Improve false-positive handling",
        change_summary="Add hard-gate precedence",
    )
    b = generator.generate(
        base,
        rationale="Improve false-positive handling",
        change_summary="Add hard-gate precedence",
    )

    assert a.candidate_id == b.candidate_id
    assert a.proposed_version == "1.0.1"
    assert a.base_version == "1.0.0"


def test_gold_026_submitting_candidate_never_mutates_certified_base():
    registry = SkillRegistry()
    base = certified_skill(registry)
    curator = SkillCurator()

    candidate = curator.propose_improvement(
        base,
        rationale="Improve evidence routing",
        change_summary="Route EVS lineage explicitly",
    )
    submitted = curator.submit_candidate(registry, candidate)

    assert registry.get(base.skill_id, base.version).state is SkillState.CERTIFIED
    assert submitted.version == "1.0.1"
    assert submitted.state is SkillState.CANDIDATE


def test_gold_027_curator_only_recommends_deprecation_for_certified_skill():
    registry = SkillRegistry()
    base = certified_skill(registry)
    curator = SkillCurator(stale_after_days=30, archive_after_days=90)

    recommendation = curator.review_activity(
        base,
        days_since_last_use=120,
    )

    assert recommendation.action == "PROPOSE_DEPRECATE"
    assert registry.get(base.skill_id, base.version).state is SkillState.CERTIFIED


def test_gold_028_pinned_skill_bypasses_stale_transition():
    skill = SkillRecord(
        skill_id="CS_QA_001",
        name="qa-coaching",
        domain="cs",
        version="1.0.0",
    )
    recommendation = SkillCurator().review_activity(
        skill,
        days_since_last_use=999,
        pinned=True,
    )
    assert recommendation.action == "KEEP"
    assert recommendation.reason == "PINNED"


def test_gold_029_same_version_candidate_is_blocked():
    base = SkillRecord(
        skill_id="CORE8_DECISION",
        name="core8-decision",
        domain="investment",
        version="1.0.0",
        state=SkillState.CERTIFIED,
    )
    generator = SkillCandidateGenerator()

    try:
        generator.generate(
            base,
            rationale="Change",
            change_summary="Change",
            proposed_version="1.0.0",
        )
    except ValueError as exc:
        assert str(exc) == "CANDIDATE_VERSION_MUST_DIFFER"
    else:
        raise AssertionError("same-version candidate must be blocked")
