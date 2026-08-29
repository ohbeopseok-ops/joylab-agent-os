from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..models import ExperienceRecord


class InvestmentSignal(Protocol):
    decision_id: str
    skill_id: str
    skill_version: str
    confidence: float


@dataclass(frozen=True)
class AIPowerSignal:
    decision_id: str
    skill_id: str
    skill_version: str
    ticker: str
    confidence: float
    power_bottleneck_exposure: float
    value_chain_proximity: float
    orders_backlog: float
    margin: float
    valuation: float
    semiconductor_direction: str
    power_infra_direction: str


@dataclass(frozen=True)
class NVDAEventSignal:
    decision_id: str
    skill_id: str
    skill_version: str
    ticker: str
    confidence: float
    revenue_exposure: float | None
    capex_sensitivity: float | None
    value_chain_proximity: float | None
    empirical_sensitivity: float | None
    data_confidence: float | None
    event_score: float | None
    transmission_direction: str


@dataclass(frozen=True)
class EPSRevisionSignal:
    decision_id: str
    skill_id: str
    skill_version: str
    ticker: str
    confidence: float
    revision_1m_pct: float | None
    revision_3m_pct: float | None


@dataclass(frozen=True)
class MasterRankingSignal:
    decision_id: str
    skill_id: str
    skill_version: str
    ticker: str
    confidence: float
    score: float
    rank: int
    thesis_gate: str
    execution_gate: str
    portfolio_gate: str
    human_approval: bool = False


class InvestmentDomainAdapters:
    @staticmethod
    def ai_power(signal: AIPowerSignal) -> ExperienceRecord:
        tags = ["domain:ai_power"]
        if signal.semiconductor_direction != signal.power_infra_direction:
            tags.append("dual_direction")
        return ExperienceRecord(
            experience_id=signal.decision_id,
            skill_id=signal.skill_id,
            skill_version=signal.skill_version,
            success=True,
            metrics={
                "confidence": signal.confidence,
                "power_bottleneck_exposure": signal.power_bottleneck_exposure,
                "value_chain_proximity": signal.value_chain_proximity,
                "orders_backlog": signal.orders_backlog,
                "margin": signal.margin,
                "valuation": signal.valuation,
            },
            tags=tuple(tags),
        )

    @staticmethod
    def nvda_event(signal: NVDAEventSignal) -> ExperienceRecord:
        tags = ["domain:nvda_event"]
        unknown = any(v is None for v in (
            signal.revenue_exposure,
            signal.capex_sensitivity,
            signal.value_chain_proximity,
            signal.empirical_sensitivity,
            signal.data_confidence,
            signal.event_score,
        ))
        if unknown:
            tags.append("unknown_critical")
        metrics = {"confidence": signal.confidence}
        for key, value in {
            "revenue_exposure": signal.revenue_exposure,
            "capex_sensitivity": signal.capex_sensitivity,
            "value_chain_proximity": signal.value_chain_proximity,
            "empirical_sensitivity": signal.empirical_sensitivity,
            "data_confidence": signal.data_confidence,
            "event_score": signal.event_score,
        }.items():
            if value is not None:
                metrics[key] = float(value)
        return ExperienceRecord(
            experience_id=signal.decision_id,
            skill_id=signal.skill_id,
            skill_version=signal.skill_version,
            success=not unknown,
            metrics=metrics,
            tags=tuple(tags),
        )

    @staticmethod
    def eps_revision(signal: EPSRevisionSignal) -> ExperienceRecord:
        tags = ["domain:eps_revision"]
        hard_block = signal.revision_1m_pct is not None and signal.revision_1m_pct <= -10.0
        if hard_block:
            tags.extend(("hard_gate_violation", "buy_block"))
        if signal.revision_1m_pct is None:
            tags.append("unknown_critical")
        metrics = {"confidence": signal.confidence}
        if signal.revision_1m_pct is not None:
            metrics["revision_1m_pct"] = signal.revision_1m_pct
        if signal.revision_3m_pct is not None:
            metrics["revision_3m_pct"] = signal.revision_3m_pct
        return ExperienceRecord(
            experience_id=signal.decision_id,
            skill_id=signal.skill_id,
            skill_version=signal.skill_version,
            success=not hard_block and signal.revision_1m_pct is not None,
            metrics=metrics,
            tags=tuple(tags),
        )

    @staticmethod
    def master_ranking(signal: MasterRankingSignal) -> ExperienceRecord:
        tags = ["domain:master_ranking", "ranking_not_buy"]
        gates_pass = (
            signal.thesis_gate == "PASS"
            and signal.execution_gate == "PASS"
            and signal.portfolio_gate == "PASS"
            and signal.human_approval
        )
        if signal.rank == 1 and not signal.human_approval:
            tags.append("top_rank_unapproved")
        return ExperienceRecord(
            experience_id=signal.decision_id,
            skill_id=signal.skill_id,
            skill_version=signal.skill_version,
            success=gates_pass,
            metrics={
                "confidence": signal.confidence,
                "score": signal.score,
                "rank": float(signal.rank),
            },
            tags=tuple(tags),
        )
