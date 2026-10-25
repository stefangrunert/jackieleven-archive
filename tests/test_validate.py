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
