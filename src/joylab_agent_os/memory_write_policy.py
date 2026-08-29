from __future__ import annotations

from .models import MemoryTier, MemoryWriteDecision, MemoryWriteProposal


class MemoryWritePolicy:
    """Governed write policy.

    - WORKING: ephemeral writes may be automatic.
    - OPERATIONAL: requires explicit user approval or certified source.
    - EVIDENCE: requires immutable evidence plus a source reference.
    """

    def evaluate(self, proposal: MemoryWriteProposal) -> MemoryWriteDecision:
        if not proposal.key.strip():
            return MemoryWriteDecision(False, "EMPTY_KEY")
        if not proposal.value.strip():
            return MemoryWriteDecision(False, "EMPTY_VALUE")

        if proposal.tier is MemoryTier.WORKING:
            return MemoryWriteDecision(True, "WORKING_AUTO_APPROVED")

        if proposal.tier is MemoryTier.OPERATIONAL:
            if proposal.user_approved or proposal.certified_source:
                return MemoryWriteDecision(True, "OPERATIONAL_APPROVED")
            return MemoryWriteDecision(False, "OPERATIONAL_REQUIRES_APPROVAL")

        if proposal.tier is MemoryTier.EVIDENCE:
            if not proposal.immutable:
                return MemoryWriteDecision(False, "EVIDENCE_MUST_BE_IMMUTABLE")
            if not proposal.source_ref.strip():
                return MemoryWriteDecision(False, "EVIDENCE_REQUIRES_SOURCE_REF")
            return MemoryWriteDecision(True, "EVIDENCE_APPROVED")

        return MemoryWriteDecision(False, "UNKNOWN_TIER")
