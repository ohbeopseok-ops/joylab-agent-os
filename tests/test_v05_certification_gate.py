from pathlib import Path

from joylab_agent_os.v05_certification_gate import (
    V05CertificationGate,
    V05CertificationInputs,
)


SCHEMAS = (
    "schemas/evidence_snapshot.schema.json",
    "schemas/evidence_graph_snapshot.schema.json",
)
REGISTRY = "gold_registry/GOLD_CASE_REGISTRY_V0.5.2.json"


def base(**overrides):
    values = dict(
        python_ci_green=True,
        regression_green=True,
        gold_registry_path=REGISTRY,
        schema_paths=SCHEMAS,
        required_certified_gold=70,
    )
    values.update(overrides)
    return V05CertificationInputs(**values)


def test_gold_065_unified_gate_passes_with_green_baseline():
    result = V05CertificationGate().evaluate(base())
    assert result.passed is True
    assert all(result.checks.values())


def test_gold_066_python_ci_failure_blocks_release():
    result = V05CertificationGate().evaluate(base(python_ci_green=False))
    assert result.passed is False
    assert "PYTHON_CI_FAILED" in result.reasons


def test_gold_067_regression_failure_blocks_release():
    result = V05CertificationGate().evaluate(base(regression_green=False))
    assert result.passed is False
    assert "REGRESSION_FAILED" in result.reasons


def test_gold_068_missing_schema_blocks_release(tmp_path):
    result = V05CertificationGate().evaluate(
        base(schema_paths=(str(tmp_path / "missing.schema.json"),))
    )
    assert result.passed is False
    assert "SCHEMA_FAILED" in result.reasons


def test_gold_069_evs_evg_and_audit_checks_are_green():
    result = V05CertificationGate().evaluate(base())
    assert result.checks["evs"] is True
    assert result.checks["evg"] is True
    assert result.checks["audit"] is True


def test_gold_070_certified_gold_minimum_is_enforced():
    result = V05CertificationGate().evaluate(
        base(required_certified_gold=999)
    )
    assert result.passed is False
    assert "GOLD_CERTIFIED_MINIMUM_FAILED" in result.reasons
