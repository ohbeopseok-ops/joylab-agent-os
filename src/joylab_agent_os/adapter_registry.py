from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .models import ExperienceRecord


AdapterFn = Callable[[Any], ExperienceRecord]


@dataclass(frozen=True)
class AdapterRegistration:
    domain: str
    signal_type: type
    adapter: AdapterFn


class AdapterRegistry:
    """Routes normalized domain signals to ExperienceRecord adapters."""

    def __init__(self) -> None:
        self._by_domain: dict[str, AdapterRegistration] = {}

    def register(self, domain: str, signal_type: type, adapter: AdapterFn) -> None:
        key = domain.strip().lower()
        if not key:
            raise ValueError("DOMAIN_REQUIRED")
        if key in self._by_domain:
            raise ValueError(f"ADAPTER_ALREADY_REGISTERED:{key}")
        self._by_domain[key] = AdapterRegistration(key, signal_type, adapter)

    def domains(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_domain))

    def route(self, domain: str, signal: Any) -> ExperienceRecord:
        key = domain.strip().lower()
        try:
            reg = self._by_domain[key]
        except KeyError as exc:
            raise ValueError(f"ADAPTER_NOT_FOUND:{key}") from exc
        if not isinstance(signal, reg.signal_type):
            raise TypeError(
                f"SIGNAL_TYPE_MISMATCH:{key}:{reg.signal_type.__name__}"
            )
        return reg.adapter(signal)


@dataclass(frozen=True)
class DomainPlugin:
    plugin_id: str
    domain: str
    version: str
    enabled: bool = True


class DomainPluginRegistry:
    """Governed registry of available domain plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, DomainPlugin] = {}

    def register(self, plugin: DomainPlugin) -> None:
        if plugin.plugin_id in self._plugins:
            raise ValueError(f"PLUGIN_ALREADY_REGISTERED:{plugin.plugin_id}")
        if not plugin.domain.strip():
            raise ValueError("PLUGIN_DOMAIN_REQUIRED")
        self._plugins[plugin.plugin_id] = plugin

    def get(self, plugin_id: str) -> DomainPlugin:
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise ValueError("PLUGIN_NOT_FOUND") from exc

    def enabled_domains(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                p.domain.lower()
                for p in self._plugins.values()
                if p.enabled
            )
        )


def build_default_investment_adapter_registry() -> AdapterRegistry:
    from .adapters.core8 import Core8Adapter, Core8Decision
    from .adapters.investment_domains import (
        AIPowerSignal,
        EPSRevisionSignal,
        InvestmentDomainAdapters,
        MasterRankingSignal,
        NVDAEventSignal,
    )

    registry = AdapterRegistry()
    registry.register("core8", Core8Decision, Core8Adapter.to_experience)
    registry.register("ai_power", AIPowerSignal, InvestmentDomainAdapters.ai_power)
    registry.register("nvda_event", NVDAEventSignal, InvestmentDomainAdapters.nvda_event)
    registry.register("eps_revision", EPSRevisionSignal, InvestmentDomainAdapters.eps_revision)
    registry.register("master_ranking", MasterRankingSignal, InvestmentDomainAdapters.master_ranking)
    return registry
