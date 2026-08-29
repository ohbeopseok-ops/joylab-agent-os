from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Protocol

from .models import (
    MemoryTier,
    MemoryWriteDecision,
    MemoryWriteProposal,
)
from .memory_write_policy import MemoryWritePolicy


_MEMORY_FENCE_RE = re.compile(r"</?\s*memory-context\s*>", re.IGNORECASE)


def sanitize_memory_context(text: str) -> str:
    return _MEMORY_FENCE_RE.sub("", text or "").strip()


class MemoryProvider(Protocol):
    name: str
    tier: MemoryTier

    def recall(self, query: str) -> str:
        ...

    def write(self, proposal: MemoryWriteProposal) -> None:
        ...


class MemoryRouter:
    """Failure-isolated memory provider router inspired by Hermes MemoryManager.

    V0.3 intentionally allows one provider per tier to prevent ambiguous writes.
    """

    def __init__(
        self,
        *,
        policy: MemoryWritePolicy | None = None,
        recall_timeout_seconds: float = 1.0,
    ) -> None:
        if recall_timeout_seconds <= 0:
            raise ValueError("recall_timeout_seconds must be positive")
        self.policy = policy or MemoryWritePolicy()
        self.recall_timeout_seconds = recall_timeout_seconds
        self._providers: dict[MemoryTier, MemoryProvider] = {}

    def register_provider(self, provider: MemoryProvider) -> None:
        if provider.tier in self._providers:
            raise ValueError(f"MEMORY_PROVIDER_ALREADY_REGISTERED:{provider.tier.value}")
        self._providers[provider.tier] = provider

    def recall(
        self,
        query: str,
        *,
        tiers: tuple[MemoryTier, ...] | None = None,
    ) -> str:
        selected = tiers or tuple(MemoryTier)
        parts: list[str] = []

        for tier in selected:
            provider = self._providers.get(tier)
            if provider is None:
                continue

            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(provider.recall, query)
            try:
                raw = future.result(timeout=self.recall_timeout_seconds)
            except FutureTimeout:
                future.cancel()
                executor.shutdown(wait=False, cancel_futures=True)
                continue
            except Exception:
                executor.shutdown(wait=False, cancel_futures=True)
                continue
            else:
                executor.shutdown(wait=False, cancel_futures=True)

            clean = sanitize_memory_context(raw)
            if clean:
                parts.append(f"[{tier.value}:{provider.name}]\n{clean}")

        return "\n\n".join(parts)

    def propose_write(self, proposal: MemoryWriteProposal) -> MemoryWriteDecision:
        decision = self.policy.evaluate(proposal)
        if not decision.approved:
            return decision

        provider = self._providers.get(proposal.tier)
        if provider is None:
            return MemoryWriteDecision(
                approved=False,
                reason="NO_PROVIDER_FOR_TIER",
            )

        try:
            provider.write(proposal)
        except Exception:
            return MemoryWriteDecision(
                approved=False,
                reason="PROVIDER_WRITE_FAILED",
            )

        return MemoryWriteDecision(
            approved=True,
            reason="WRITE_COMMITTED",
        )
