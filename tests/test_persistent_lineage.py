import json

import pytest

from joylab_agent_os.evidence_builder import EvidenceBuilder
from joylab_agent_os.models import ExperienceRecord
from joylab_agent_os.persistent_lineage import (
    PersistentEvidenceStore,
    PersistentExperienceStore,
    PersistentLineageJournal,
)
from joylab_agent_os.snapshot_integrity import seal_snapshot, verify_snapshot


def experience(exp_id="EXP-001", *, confidence=88.0):
    return ExperienceRecord(
        experience_id=exp_id,
        skill_id="CORE8_DECISION",
        skill_version="1.0.0",
        success=True,
        metrics={"confidence": confidence},
        tags=("gold_case", "oos_pass", "regression_pass"),
    )


def stores(tmp_path):
    journal = PersistentLineageJournal(tmp_path / "lineage.jsonl")
    return (
        journal,
        PersistentExperienceStore(journal),
        PersistentEvidenceStore(journal),
    )


def test_gold_093_experience_survives_restart(tmp_path):
    path = tmp_path / "lineage.jsonl"
    PersistentExperienceStore(path).append(experience())

    restarted = PersistentExperienceStore(path)
    assert restarted.all()[0].experience_id == "EXP-001"
    assert restarted.count("CORE8_DECISION") == 1


def test_gold_094_evidence_survives_restart_and_verifies(tmp_path):
    path = tmp_path / "lineage.jsonl"
    experiences = PersistentExperienceStore(path)
    experiences.append(experience())
    snapshot = EvidenceBuilder().build(
        "CORE8_DECISION", "1.0.0", experiences.all()
    )
    artifact = seal_snapshot(snapshot)
    PersistentEvidenceStore(path).append(artifact)

    recovered = PersistentEvidenceStore(path).all()
    assert len(recovered) == 1
    assert recovered[0].snapshot_id == artifact.snapshot_id
    assert verify_snapshot(recovered[0]) is True


def test_gold_095_experience_and_evidence_share_one_hash_chain(tmp_path):
    journal, experiences, evidence = stores(tmp_path)
    experiences.append(experience())
    artifact = seal_snapshot(
        EvidenceBuilder().build("CORE8_DECISION", "1.0.0", experiences.all())
    )
    evidence.append(artifact)

    entries = journal.recover_entries()
    assert [e.sequence for e in entries] == [1, 2]
    assert entries[1].prev_hash == entries[0].entry_hash


def test_gold_096_tampered_middle_entry_is_detected(tmp_path):
    path = tmp_path / "lineage.jsonl"
    experiences = PersistentExperienceStore(path)
    experiences.append(experience("EXP-001"))
    experiences.append(experience("EXP-002"))

    lines = path.read_text(encoding="utf-8").splitlines()
    row = json.loads(lines[0])
    row["payload"]["metrics"]["confidence"] = 1.0
    lines[0] = json.dumps(row, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="LINEAGE_ENTRY_HASH_MISMATCH"):
        PersistentLineageJournal(path).recover_entries()


def test_gold_097_truncated_tail_is_blocked(tmp_path):
    path = tmp_path / "lineage.jsonl"
    PersistentExperienceStore(path).append(experience())
    content = path.read_text(encoding="utf-8")
    path.write_text(content[:-1], encoding="utf-8")

    with pytest.raises(ValueError, match="LINEAGE_JOURNAL_TRUNCATED_TAIL"):
        PersistentLineageJournal(path).recover_entries()


def test_gold_098_duplicate_experience_id_is_blocked_after_restart(tmp_path):
    path = tmp_path / "lineage.jsonl"
    PersistentExperienceStore(path).append(experience("EXP-SAME"))

    restarted = PersistentExperienceStore(path)
    with pytest.raises(ValueError, match="EXPERIENCE_ID_ALREADY_EXISTS"):
        restarted.append(experience("EXP-SAME"))


def test_gold_099_duplicate_evs_id_is_blocked(tmp_path):
    _, experiences, evidence = stores(tmp_path)
    experiences.append(experience())
    artifact = seal_snapshot(
        EvidenceBuilder().build("CORE8_DECISION", "1.0.0", experiences.all())
    )
    evidence.append(artifact)

    with pytest.raises(ValueError, match="EVIDENCE_SNAPSHOT_ALREADY_EXISTS"):
        evidence.append(artifact)


def test_gold_100_restart_rebuilds_same_experience_to_evidence_lineage(tmp_path):
    path = tmp_path / "lineage.jsonl"
    experiences = PersistentExperienceStore(path)
    experiences.append(experience("EXP-001", confidence=80.0))
    experiences.append(experience("EXP-002", confidence=100.0))

    restarted_experiences = PersistentExperienceStore(path)
    evidence = PersistentEvidenceStore(path)
    rebuilt = evidence.rebuild_latest_from_experiences(
        skill_id="CORE8_DECISION",
        skill_version="1.0.0",
        experiences=restarted_experiences,
        evidence_builder=EvidenceBuilder(),
    )

    assert rebuilt.snapshot.samples == 2
    assert rebuilt.snapshot.confidence == 90.0
    assert rebuilt.snapshot.source_experience_ids == ("EXP-001", "EXP-002")
    assert verify_snapshot(rebuilt) is True
