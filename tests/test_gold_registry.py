import json
from pathlib import Path

import pytest

from joylab_agent_os.gold_registry import GoldCaseEntry, GoldCaseRegistry


REGISTRY = Path("gold_registry/GOLD_CASE_REGISTRY_V0.5.2.json")


def test_gold_060_registry_covers_001_through_059():
    registry = GoldCaseRegistry.from_json(REGISTRY)
    assert len(registry.entries()) == 59
    assert registry.entries()[0].id == "GOLD_001"
    assert registry.entries()[-1].id == "GOLD_059"
    assert registry.validate_contiguous() is True


def test_gold_061_all_current_cases_are_certified():
    registry = GoldCaseRegistry.from_json(REGISTRY)
    assert len(registry.certified_ids()) == 59


def test_gold_062_registry_provenance_is_complete():
    registry = GoldCaseRegistry.from_json(REGISTRY)
    assert registry.provenance_complete() is True


def test_gold_063_invalid_status_is_blocked():
    with pytest.raises(ValueError, match="INVALID_GOLD_STATUS"):
        GoldCaseRegistry([
            GoldCaseEntry(
                id="GOLD_999",
                status="BROKEN",
                component="x",
                source_test="x",
                provenance={"repository":"r","pull_request":1,"evidence_refs":["x"]},
            )
        ])


def test_gold_064_duplicate_gold_id_is_blocked():
    entry = GoldCaseEntry(
        id="GOLD_001",
        status="CERTIFIED",
        component="x",
        source_test="x",
        provenance={"repository":"r","pull_request":1,"evidence_refs":["x"]},
    )
    with pytest.raises(ValueError, match="DUPLICATE_GOLD_ID"):
        GoldCaseRegistry([entry, entry])
