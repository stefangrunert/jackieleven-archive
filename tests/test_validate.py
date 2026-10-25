import shutil
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from validate import validate  # noqa: E402

VALID = Path(__file__).parent / "fixtures" / "valid"


@pytest.fixture
def root(tmp_path):
    target = tmp_path / "repo"
    shutil.copytree(VALID, target)
    return target


def edit(root: Path, rel: str, change) -> None:
    path = root / rel
    data = yaml.safe_load(path.read_text())
    change(data)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def messages(report):
    return "\n".join(report.errors)


def test_valid_fixtures_pass():
    report = validate(VALID)
    assert report.errors == []
    assert report.warnings == []


def test_unknown_reference(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["took_place_at"][0].update(entity_value="place/nirgendwo"))
    assert "unbekannte Entität place/nirgendwo" in messages(validate(root))


def test_reference_required(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["took_place_at"][0].pop("references"))
    assert "took_place_at[0] braucht mindestens einen Beleg" in messages(validate(root))


def test_invalid_edtf(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["time"][0].update(edtf_value="um 1950"))
    assert "keine gültige EDTF-Angabe" in messages(validate(root))


def test_fiction_not_allowed_as_reference(root):
    edit(root, "data/document/beispiel-kolumne.yaml", lambda d: d.update(fiction=True))
    assert "ist Fiktion" in messages(validate(root))


def test_id_must_match_filename(root):
    edit(root, "data/place/kirkcaldy.yaml", lambda d: d.update(id="place/fife"))
    assert "id muss place/kirkcaldy lauten" in messages(validate(root))


def test_job_requires_sonnet(root):
    edit(root, "jobs/pilot-konzertberichte.yaml", lambda d: d.update(model="claude-opus-5-5"))
    assert "Agenten laufen mit Sonnet" in messages(validate(root))


def test_closed_schema_rejects_unknown_fields(root):
    edit(root, "data/place/kirkcaldy.yaml", lambda d: d.update(einwohner=50000))
    assert "Schema" in messages(validate(root))


def test_enum_values_checked(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["time"][0].update(rank="sicher"))
    assert "Schema" in messages(validate(root))


def test_duplicate_label_warns(root):
    shutil.copy(root / "data/place/kirkcaldy.yaml", root / "data/place/kirkcaldy-fife.yaml")
    edit(root, "data/place/kirkcaldy-fife.yaml", lambda d: d.update(id="place/kirkcaldy-fife"))
    report = validate(root)
    assert any("mögliche Doppelung" in w for w in report.warnings)


def test_duplicate_confirmed_identifier(root):
    def confirm(d):
        d["identifiers"][0]["match_status"] = "confirmed"
    edit(root, "data/place/kirkcaldy.yaml", confirm)
    shutil.copy(root / "data/place/kirkcaldy.yaml", root / "data/place/kirkcaldy-fife.yaml")
    edit(root, "data/place/kirkcaldy-fife.yaml",
         lambda d: d.update(id="place/kirkcaldy-fife", label="Kirkcaldy, Fife"))
    assert "bestätigte Kennung geonames" in messages(validate(root))


def test_coverage_needs_known_job(root):
    edit(root, "coverage/pilot-konzertberichte-1.yaml",
         lambda d: d["searched_by"].update(job="job/unbekannt"))
    assert "unbekannter Auftrag job/unbekannt" in messages(validate(root))


# ---------- Schema v0.2 ----------

from validate import conflicts, statement_hash  # noqa: E402
import subprocess  # noqa: E402


def load_entities(root):
    from validate import _Loader
    out = {}
    for path in sorted((root / "data").glob("*/*.yaml")):
        data = yaml.load(path.read_text(), Loader=_Loader)
        out[data["id"]] = (path, data)
    return out


def test_statement_id_required(root):
    edit(root, "data/event/birth-jackie-leven.yaml", lambda d: d["time"][0].pop("statement_id"))
    assert "statement_id" in messages(validate(root))


def test_statement_id_unique(root):
    def copy_id(d):
        d["time"][1]["statement_id"] = d["time"][0]["statement_id"]
    edit(root, "data/event/birth-jackie-leven.yaml", copy_id)
    assert "Aussagekennung" in messages(validate(root))


def test_assign_ids_fills_missing(root):
    edit(root, "data/event/birth-jackie-leven.yaml", lambda d: d["time"][0].pop("statement_id"))
    tool = Path(__file__).resolve().parent.parent / "tools" / "assign_ids.py"
    subprocess.run([sys.executable, str(tool), str(root)], check=True, capture_output=True)
    assert validate(root).errors == []


def test_cycle_in_located_in(root):
    shutil.copy(root / "data/place/kirkcaldy.yaml", root / "data/place/fife.yaml")
    edit(root, "data/place/fife.yaml", lambda d: d.update(
        id="place/fife", label="Fife", place_type="region",
        located_in=[{"statement_id": "st-aaaaaaaaaaaa", "entity_value": "place/kirkcaldy",
                     "references": [{"document": "document/beispiel-nachruf"}]}]))
    edit(root, "data/place/kirkcaldy.yaml", lambda d: d.update(
        located_in=[{"statement_id": "st-bbbbbbbbbbbb", "entity_value": "place/fife",
                     "references": [{"document": "document/beispiel-nachruf"}]}]))
    assert "Zyklus über located_in" in messages(validate(root))


def test_review_changed_after_review_warns(root):
    def review(d):
        st = d["time"][0]
        st.update(reviewed_by="stefan", reviewed_at="2026-10-26", review_hash=statement_hash(st))
        st["note"] = "nachträglich geändert"
    edit(root, "data/event/birth-jackie-leven.yaml", review)
    report = validate(root)
    assert report.errors == []
    assert any("nach der Prüfung geändert" in w for w in report.warnings)


def test_review_needs_all_fields(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["time"][0].update(reviewed_by="stefan"))
    assert "Prüfung braucht" in messages(validate(root))


def test_claimant_must_exist(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["time"][0]["references"][0].update(asserted_by="person/niemand"))
    assert "unbekannte Entität person/niemand" in messages(validate(root))


def test_claimant_unknown_allowed(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["time"][0]["references"][0].update(asserted_by="unknown"))
    assert validate(root).errors == []


def test_passage_needs_known_document(root):
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["time"][0]["references"][0].update(passage="document/unbekannt#p-3"))
    assert "gehört zu keinem bekannten Dokument" in messages(validate(root))


def test_passage_checked_against_manifest(root):
    (root / "passages").mkdir()
    (root / "passages" / "manifest.txt").write_text("document/beispiel-kolumne#p-1 abc\n")
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["time"][0]["references"][1].update(passage="document/beispiel-kolumne#p-2"))
    assert "fehlt im Verzeichnis" in messages(validate(root))


def test_conflicts_distinguish_disputed_and_deviating(root):
    found = {(e, p): k for e, p, k, _ in conflicts(load_entities(root))}
    # verworfene Aussage zählt nicht: kein Befund
    assert ("event/birth-jackie-leven", "time") not in found
    edit(root, "data/event/birth-jackie-leven.yaml", lambda d: d["time"][1].update(rank="normal"))
    found = {(e, p): k for e, p, k, _ in conflicts(load_entities(root))}
    assert found[("event/birth-jackie-leven", "time")] == "deviating"
    edit(root, "data/event/birth-jackie-leven.yaml", lambda d: d["time"][0].update(rank="normal"))
    found = {(e, p): k for e, p, k, _ in conflicts(load_entities(root))}
    assert found[("event/birth-jackie-leven", "time")] == "disputed"


def test_multiple_participants_are_no_conflict(root):
    def add(d):
        d["participants"].append({"statement_id": "st-cccccccccccc", "agent_ref": "persona/sir-vincent-lone",
                                  "roles": ["support_act"], "references": [{"document": "document/beispiel-nachruf"}]})
    edit(root, "data/event/birth-jackie-leven.yaml", add)
    assert not [c for c in conflicts(load_entities(root)) if c[1] == "participants"]


def test_coverage_completeness_enum(root):
    edit(root, "coverage/pilot-konzertberichte-1.yaml", lambda d: d.update(completeness="halb"))
    assert "Schema" in messages(validate(root))


def test_announced_and_took_place_are_compatible(root):
    def add_status(d):
        d["performance_status"] = [
            {"statement_id": "st-dddddddddddd", "status_value": "announced",
             "references": [{"document": "document/beispiel-nachruf"}]},
            {"statement_id": "st-eeeeeeeeeeee", "status_value": "took_place",
             "references": [{"document": "document/beispiel-kolumne"}]},
        ]
    edit(root, "data/event/birth-jackie-leven.yaml", add_status)
    assert not [c for c in conflicts(load_entities(root)) if c[1] == "performance_status"]
    edit(root, "data/event/birth-jackie-leven.yaml",
         lambda d: d["performance_status"][0].update(status_value="cancelled"))
    assert [c for c in conflicts(load_entities(root)) if c[1] == "performance_status"]
