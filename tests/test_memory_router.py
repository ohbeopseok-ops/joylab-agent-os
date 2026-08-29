import time

from joylab_agent_os import (
    MemoryRouter,
    MemoryTier,
    MemoryWriteProposal,
)


class FakeProvider:
    def __init__(self, name, tier, *, recall_text="", delay=0.0, fail=False):
        self.name = name
        self.tier = tier
        self.recall_text = recall_text
        self.delay = delay
        self.fail = fail
        self.writes = []

    def recall(self, query):
        if self.delay:
            time.sleep(self.delay)
        if self.fail:
            raise RuntimeError("boom")
        return self.recall_text

    def write(self, proposal):
        if self.fail:
            raise RuntimeError("boom")
        self.writes.append(proposal)


def test_gold_017_recall_is_sanitized_and_labeled():
    router = MemoryRouter()
    router.register_provider(
        FakeProvider(
            "ops",
            MemoryTier.OPERATIONAL,
            recall_text="<memory-context>certified rule</memory-context>",
        )
    )
    result = router.recall("query")
    assert "certified rule" in result
    assert "<memory-context>" not in result
    assert "[OPERATIONAL:ops]" in result


def test_gold_018_provider_failure_does_not_break_other_provider():
    router = MemoryRouter()
    router.register_provider(FakeProvider("bad", MemoryTier.WORKING, fail=True))
    router.register_provider(
        FakeProvider("good", MemoryTier.OPERATIONAL, recall_text="usable")
    )
    assert "usable" in router.recall("query")


def test_gold_019_recall_timeout_is_fail_open_for_agent_runtime():
    router = MemoryRouter(recall_timeout_seconds=0.01)
    router.register_provider(
        FakeProvider("slow", MemoryTier.WORKING, recall_text="late", delay=0.05)
    )
    assert router.recall("query") == ""


def test_gold_020_operational_write_requires_governance():
    provider = FakeProvider("ops", MemoryTier.OPERATIONAL)
    router = MemoryRouter()
    router.register_provider(provider)

    denied = router.propose_write(
        MemoryWriteProposal(
            tier=MemoryTier.OPERATIONAL,
            key="rule",
            value="do this",
        )
    )
    assert denied.approved is False
    assert provider.writes == []

    approved = router.propose_write(
        MemoryWriteProposal(
            tier=MemoryTier.OPERATIONAL,
            key="rule",
            value="do this",
            user_approved=True,
        )
    )
    assert approved.approved is True
    assert len(provider.writes) == 1


def test_gold_021_evidence_write_requires_immutable_source():
    provider = FakeProvider("evidence", MemoryTier.EVIDENCE)
    router = MemoryRouter()
    router.register_provider(provider)

    denied = router.propose_write(
        MemoryWriteProposal(
            tier=MemoryTier.EVIDENCE,
            key="snapshot",
            value="payload",
            immutable=False,
            source_ref="EVS-abc",
        )
    )
    assert denied.approved is False

    approved = router.propose_write(
        MemoryWriteProposal(
            tier=MemoryTier.EVIDENCE,
            key="snapshot",
            value="payload",
            immutable=True,
            source_ref="EVS-abc",
        )
    )
    assert approved.approved is True
