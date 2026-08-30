from joylab_agent_os.knowledge_compound import (
    ClaimCandidate,
    ClaimStatus,
    Evidence,
    EvidenceRelation,
    can_verify_page,
    canonicalize_text,
    render_obsidian_page,
    sha256_text,
    verify_claim,
)


def test_fingerprint_is_stable_across_whitespace():
    assert sha256_text("hello   world") == sha256_text(" hello world ")
    assert canonicalize_text("a\n\tb") == "a b"


def test_verified_claim_passes_gate():
    candidate = ClaimCandidate(
        text="Persistent memory must retain evidence lineage.",
        confidence=92,
        source_id="src-1",
        evidence=(Evidence("src-1", EvidenceRelation.SUPPORTS),),
    )
    result = verify_claim(candidate)
    assert result.status is ClaimStatus.VERIFIED
    assert result.promotable


def test_low_confidence_blocks_promotion():
    candidate = ClaimCandidate(
        text="Uncertain claim",
        confidence=70,
        source_id="src-1",
        evidence=(Evidence("src-1", EvidenceRelation.SUPPORTS),),
    )
    result = verify_claim(candidate)
    assert result.status is ClaimStatus.REJECTED
    assert "LOW_CONFIDENCE" in result.reason_codes


def test_contradiction_blocks_promotion():
    candidate = ClaimCandidate(
        text="Conflicted claim",
        confidence=95,
        source_id="src-1",
        evidence=(
            Evidence("src-1", EvidenceRelation.SUPPORTS),
            Evidence("src-2", EvidenceRelation.CONTRADICTS),
        ),
    )
    result = verify_claim(candidate)
    assert result.status is ClaimStatus.CONFLICT
    assert "UNRESOLVED_CONTRADICTION" in result.reason_codes


def test_page_requires_all_verified_claims():
    good = verify_claim(
        ClaimCandidate(
            text="good",
            confidence=90,
            source_id="s1",
            evidence=(Evidence("s1", EvidenceRelation.SUPPORTS),),
        )
    )
    bad = verify_claim(
        ClaimCandidate(
            text="bad",
            confidence=10,
            source_id="s2",
            evidence=(Evidence("s2", EvidenceRelation.SUPPORTS),),
        )
    )
    assert can_verify_page([good])
    assert not can_verify_page([good, bad])


def test_obsidian_renderer_carries_lineage():
    page = render_obsidian_page(
        title="Knowledge Engine",
        domain="ai",
        body_md="# Body",
        source_ids=["s1"],
        claim_ids=["c1"],
        confidence=91.5,
    )
    assert "status: VERIFIED" in page
    assert 'source_ids: "s1"' in page
    assert 'claim_ids: "c1"' in page
