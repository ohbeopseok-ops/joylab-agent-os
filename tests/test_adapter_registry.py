import pytest

from joylab_agent_os.adapter_registry import (
    AdapterRegistry,
    DomainPlugin,
    DomainPluginRegistry,
    build_default_investment_adapter_registry,
)
from joylab_agent_os.adapters.core8 import Core8Decision
from joylab_agent_os.adapters.investment_domains import EPSRevisionSignal


def test_gold_053_default_registry_has_all_five_domains():
    registry = build_default_investment_adapter_registry()
    assert registry.domains() == (
        "ai_power",
        "core8",
        "eps_revision",
        "master_ranking",
        "nvda_event",
    )


def test_gold_054_core8_routes_automatically():
    registry = build_default_investment_adapter_registry()
    signal = Core8Decision(
        decision_id="CORE8-1",
        skill_id="CORE8_DECISION",
        skill_version="1.0.0",
        ticker="005930",
        action="HOLD",
        confidence=88,
        success=True,
    )
    result = registry.route("core8", signal)
    assert result.experience_id == "CORE8-1"


def test_gold_055_eps_routes_and_preserves_hard_gate():
    registry = build_default_investment_adapter_registry()
    signal = EPSRevisionSignal(
        "EPS-11","EPS_REVISION","1.0.0","005930",95,-11.0,-7.0
    )
    result = registry.route("eps_revision", signal)
    assert "hard_gate_violation" in result.tags
    assert "buy_block" in result.tags


def test_gold_056_unknown_domain_is_blocked():
    registry = build_default_investment_adapter_registry()
    with pytest.raises(ValueError, match="ADAPTER_NOT_FOUND"):
        registry.route("unknown", object())


def test_gold_057_wrong_signal_type_is_blocked():
    registry = build_default_investment_adapter_registry()
    with pytest.raises(TypeError, match="SIGNAL_TYPE_MISMATCH"):
        registry.route("core8", object())


def test_gold_058_duplicate_adapter_registration_is_blocked():
    registry = AdapterRegistry()
    registry.register("x", object, lambda _: None)
    with pytest.raises(ValueError, match="ADAPTER_ALREADY_REGISTERED"):
        registry.register("x", object, lambda _: None)


def test_gold_059_plugin_registry_tracks_enabled_domains():
    plugins = DomainPluginRegistry()
    plugins.register(DomainPlugin("p-core8","core8","1.0.0",True))
    plugins.register(DomainPlugin("p-nvda","nvda_event","1.0.0",False))
    assert plugins.enabled_domains() == ("core8",)
