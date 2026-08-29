from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .approval_audit import ApprovalAuditLog, ApprovalDecision
from .evidence_graph import build_core8_lineage
from .gold_registry import GoldCaseRegistry
from .graph_integrity import seal_graph, verify_graph_snapshot
from .models import EvidenceSnapshot
from .snapshot_integrity import seal_snapshot, verify_snapshot


@dataclass(frozen=True)
class V05CertificationInputs:
    python_ci_green: bool
    regression_green: bool
    gold_registry_path: str
    schema_paths: tuple[str, ...]
    required_certified_gold: int = 64


@dataclass(frozen=True)
class V05CertificationResult:
    passed: bool
    checks: dict[str, bool]
    reasons: tuple[str, ...]


class V05CertificationGate:
    """Unified release gate for JoyLab Agent OS V0.5.x."""

    def evaluate(self, inputs: V05CertificationInputs) -> V05CertificationResult:
        checks: dict[str, bool] = {}

        checks["python_ci"] = inputs.python_ci_green
        checks["regression"] = inputs.regression_green

        registry = GoldCaseRegistry.from_json(inputs.gold_registry_path)
        checks["gold_contiguous"] = registry.validate_contiguous()
        checks["gold_provenance"] = registry.provenance_complete()
        checks["gold_no_invalid"] = len(registry.by_status("INVALID")) == 0
        checks["gold_certified_minimum"] = (
            len(registry.certified_ids()) >= inputs.required_certified_gold
        )

        checks["schema"] = self._schemas_valid(inputs.schema_paths)
        checks["evs"] = self._evs_valid()
        checks["evg"] = self._evg_valid()
        checks["audit"] = self._audit_valid()

        reasons = tuple(
            f"{name.upper()}_FAILED"
            for name, ok in checks.items()
            if not ok
        )
        return V05CertificationResult(
            passed=not reasons,
            checks=checks,
            reasons=reasons,
        )

    @staticmethod
    def _schemas_valid(paths: tuple[str, ...]) -> bool:
        if not paths:
            return False
        for raw in paths:
            path = Path(raw)
            if not path.exists():
                return False
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return False
            if not isinstance(payload, dict) or not payload.get("$schema"):
                return False
        return True

    @staticmethod
    def _evs_valid() -> bool:
        snapshot = EvidenceSnapshot(
            skill_id="CERT_GATE",
            skill_version="0.5.3",
            samples=20,
            successful_samples=20,
            gold_cases=10,
            confidence=90.0,
            oos_pass=True,
            regression_pass=True,
            hard_gate_violations=0,
            source_experience_ids=("CERT-EXP-001",),
        )
        return verify_snapshot(seal_snapshot(snapshot))

    @staticmethod
    def _evg_valid() -> bool:
        graph = build_core8_lineage(
            decision_id="CERT-DEC-001",
            experience_id="CERT-EXP-001",
            evs_id="EVS-certification",
            candidate_id="SKC-certification",
            certified_skill_id="SKILL-CERT@0.5.3",
            audit_id="AUD-certification",
        )
        return verify_graph_snapshot(seal_graph(graph))

    @staticmethod
    def _audit_valid() -> bool:
        log = ApprovalAuditLog()
        try:
            record = log.build_record(
                candidate_id="SKC-certification",
                skill_id="SKILL-CERT",
                base_version="0.5.2",
                proposed_version="0.5.3",
                actor="ci-certification-gate",
                decision=ApprovalDecision.APPROVE,
                reason="EVS and EVG verification passed",
                evidence_refs=("EVS-certification", "EVG-certification"),
                diff_id="DIF-certification",
            )
            log.append(record)
        except ValueError:
            return False
        return len(log.all()) == 1
