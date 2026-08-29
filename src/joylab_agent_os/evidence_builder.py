from __future__ import annotations

from statistics import fmean

from .models import CertificationEvidence, EvidenceSnapshot, ExperienceRecord


class EvidenceBuilder:
    """Deterministically converts immutable experience logs into certification evidence."""

    GOLD_TAG = "gold_case"
    OOS_PASS_TAG = "oos_pass"
    OOS_FAIL_TAG = "oos_fail"
    REGRESSION_PASS_TAG = "regression_pass"
    REGRESSION_FAIL_TAG = "regression_fail"
    HARD_GATE_TAG = "hard_gate_violation"
    CONFIDENCE_METRIC = "confidence"

    def build(
        self,
        skill_id: str,
        skill_version: str,
        records: tuple[ExperienceRecord, ...] | list[ExperienceRecord],
    ) -> EvidenceSnapshot:
        selected = tuple(
            r for r in records
            if r.skill_id == skill_id and r.skill_version == skill_version
        )

        confidence_values = [
            float(r.metrics[self.CONFIDENCE_METRIC])
            for r in selected
            if self.CONFIDENCE_METRIC in r.metrics
        ]

        tags = [set(r.tags) for r in selected]
        oos_pass = any(self.OOS_PASS_TAG in t for t in tags) and not any(
            self.OOS_FAIL_TAG in t for t in tags
        )
        regression_pass = any(self.REGRESSION_PASS_TAG in t for t in tags) and not any(
            self.REGRESSION_FAIL_TAG in t for t in tags
        )

        return EvidenceSnapshot(
            skill_id=skill_id,
            skill_version=skill_version,
            samples=len(selected),
            successful_samples=sum(1 for r in selected if r.success),
            gold_cases=sum(1 for t in tags if self.GOLD_TAG in t),
            confidence=fmean(confidence_values) if confidence_values else 0.0,
            oos_pass=oos_pass,
            regression_pass=regression_pass,
            hard_gate_violations=sum(1 for t in tags if self.HARD_GATE_TAG in t),
            source_experience_ids=tuple(r.experience_id for r in selected),
        )

    @staticmethod
    def to_certification_evidence(snapshot: EvidenceSnapshot) -> CertificationEvidence:
        return CertificationEvidence(
            samples=snapshot.samples,
            gold_cases=snapshot.gold_cases,
            confidence=snapshot.confidence,
            oos_pass=snapshot.oos_pass,
            regression_pass=snapshot.regression_pass,
            hard_gate_violations=snapshot.hard_gate_violations,
        )
