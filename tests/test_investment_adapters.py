from joylab_agent_os.adapters.investment_domains import (
    AIPowerSignal,
    EPSRevisionSignal,
    InvestmentDomainAdapters,
    MasterRankingSignal,
    NVDAEventSignal,
)


def test_gold_045_ai_power_preserves_dual_direction():
    r = InvestmentDomainAdapters.ai_power(AIPowerSignal(
        "AI-1","AI_POWER","1.0.0","010120",90,90,95,80,70,60,"MIXED","POSITIVE"
    ))
    assert "dual_direction" in r.tags


def test_gold_046_nvda_unknown_is_not_coerced_to_zero():
    r = InvestmentDomainAdapters.nvda_event(NVDAEventSignal(
        "NVDA-1","NVDA_EVENT","1.0.0","005930",80,None,90,80,70,90,75,"POSITIVE"
    ))
    assert "unknown_critical" in r.tags
    assert "revenue_exposure" not in r.metrics
    assert r.success is False


def test_gold_047_nvda_complete_signal_is_valid():
    r = InvestmentDomainAdapters.nvda_event(NVDAEventSignal(
        "NVDA-2","NVDA_EVENT","1.0.0","000660",88,90,95,90,85,90,82,"POSITIVE"
    ))
    assert "unknown_critical" not in r.tags
    assert r.success is True


def test_gold_048_eps_minus_10_is_buy_block():
    r = InvestmentDomainAdapters.eps_revision(EPSRevisionSignal(
        "EPS-1","EPS_REVISION","1.0.0","005930",95,-10.0,-5.0
    ))
    assert "hard_gate_violation" in r.tags
    assert "buy_block" in r.tags
    assert r.success is False


def test_gold_049_eps_unknown_stays_unknown():
    r = InvestmentDomainAdapters.eps_revision(EPSRevisionSignal(
        "EPS-2","EPS_REVISION","1.0.0","005930",70,None,None
    ))
    assert "unknown_critical" in r.tags
    assert "revision_1m_pct" not in r.metrics


def test_gold_050_rank_one_is_not_auto_buy():
    r = InvestmentDomainAdapters.master_ranking(MasterRankingSignal(
        "MR-1","MASTER_RANKING","1.0.0","000660",90,92,1,"PASS","PASS","PASS",False
    ))
    assert "ranking_not_buy" in r.tags
    assert "top_rank_unapproved" in r.tags
    assert r.success is False


def test_gold_051_rank_one_can_only_succeed_after_all_gates_and_approval():
    r = InvestmentDomainAdapters.master_ranking(MasterRankingSignal(
        "MR-2","MASTER_RANKING","1.0.0","000660",90,92,1,"PASS","PASS","PASS",True
    ))
    assert r.success is True


def test_gold_052_portfolio_gate_blocks_top_rank_even_with_approval():
    r = InvestmentDomainAdapters.master_ranking(MasterRankingSignal(
        "MR-3","MASTER_RANKING","1.0.0","000660",90,92,1,"PASS","PASS","BLOCK",True
    ))
    assert r.success is False
