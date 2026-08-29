from __future__ import annotations

from .models import (
    CertificationEvidence,
    CertificationPolicy,
    CertificationResult,
)


class CertificationGate:
    def __init__(self, policy: CertificationPolicy | None = None) -> None:
        self.policy = policy or CertificationPolicy()

    def evaluate(self, evidence: CertificationEvidence) -> CertificationResult:
        p = self.policy
        reasons: list[str] = []

        if evidence.samples < p.min_samples:
            reasons.append("INSUFFICIENT_SAMPLES")
        if evidence.gold_cases < p.min_gold_cases:
            reasons.append("INSUFFICIENT_GOLD_CASES")
        if evidence.confidence < p.min_confidence:
            reasons.append("LOW_CONFIDENCE")
        if p.require_oos_pass and not evidence.oos_pass:
            reasons.append("OOS_FAILED")
        if p.require_regression_pass and not evidence.regression_pass:
            reasons.append("REGRESSION_FAILED")
        if evidence.hard_gate_violations > p.max_hard_gate_violations:
            reasons.append("HARD_GATE_VIOLATION")

        return CertificationResult(
            passed=not reasons,
            reasons=tuple(reasons),
            evaluated_policy=p.version,
        )
