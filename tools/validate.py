"""Prüft Datendateien, Aufträge und Abdeckungsregister gegen Schema und Regeln.

Aufruf: uv run python tools/validate.py [Wurzelverzeichnis]

Fehler brechen ab (Exit-Code 1), Hinweise nicht.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from edtf import parse_edtf
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "jackieleven.yaml"

# Ordner unter data/ → Klasse im Schema
CLASSES = {
    "person": "Person",
    "persona": "Persona",
    "group": "Group",
    "organization": "Organization",
    "place": "Place",
    "event": "Event",
    "work": "Work",
    "document": "Document",
    "publication": "Publication",
}

# Felder, deren Werte Kennungen von Entitäten sind
REF_KEYS = {"entity_value", "agent_ref", "document", "birth", "death",
            "replaced_by", "work_performed", "about", "reviews", "person",
            "derived_from", "asserted_by"}
EDTF_KEYS = {"edtf_value", "valid_time", "period"}

# Belegpflichtige Eigenschaften je Klasse (Ontologie, Abschnitt 6)
REFERENCE_REQUIRED = {
    "Event": ["time", "took_place_at", "performance_status", "participants"],
    "Group": ["members"],
    "Person": ["performs_as"],
    "Place": ["located_in"],
}

AGENT_MODEL_PREFIX = "claude-sonnet"

# Eigenschaften mit höchstens einem gültigen Wert je Zeitraum; mehrere
# unvereinbare Werte ergeben einen Konflikt (Ontologie, Abschnitt 6).
SINGLE_VALUED = {
    "Event": ["time", "took_place_at", "performance_status"],
    "Document": ["published"],
}

# Aussagen erkennt man an ihrem Wertfeld.
VALUE_KEYS = {"edtf_value", "entity_value", "status_value", "text_value", "agent_ref"}
REVIEW_KEYS = {"statement_id", "reviewed_by", "reviewed_at", "review_hash"}


def is_statement(item) -> bool:
    return isinstance(item, dict) and bool(VALUE_KEYS & item.keys())


def statements(data: dict):
    """Liefert (Eigenschaft, Aussage) für alle Aussagen einer Entität."""
    for prop, items in data.items():
        if isinstance(items, list):
            for item in items:
                if is_statement(item):
                    yield prop, item


def statement_hash(statement: dict) -> str:
    """Prüfsumme des Aussageinhalts ohne Kennung und Prüfangaben."""
    content = {k: v for k, v in statement.items() if k not in REVIEW_KEYS}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def statement_value(statement: dict):
    for key in VALUE_KEYS:
        if key in statement:
            return statement[key]
    return None


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, path: Path, msg: str) -> None:
        self.errors.append(f"{path}: {msg}")

    def warn(self, path: Path, msg: str) -> None:
        self.warnings.append(f"{path}: {msg}")


def walk(node, key=None):
    """Liefert (Schlüssel, Wert) für alle Blätter einer YAML-Struktur."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v, key)
    else:
        yield key, node


def normalize(label: str) -> str:
    s = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode()
    return "".join(c for c in s.casefold() if c.isalnum())


class _Loader(yaml.SafeLoader):
    """Liest Datumsangaben als Zeichenketten; EDTF und das Schema erwarten Text."""


_Loader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load(path: Path, report: Report):
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_Loader)
    except yaml.YAMLError as e:
        report.error(path, f"kein gültiges YAML: {e}")
        return None
    if not isinstance(data, dict):
        report.error(path, "Datei enthält kein Objekt")
        return None
    return data


def check_schema(validator: Validator, path: Path, data: dict, target: str, report: Report) -> None:
    for result in validator.validate(data, target).results:
        report.error(path, f"Schema: {result.message}")


def check_edtf(path: Path, data: dict, report: Report) -> None:
    for key, value in walk(data):
        if key in EDTF_KEYS and value is not None:
            try:
                parse_edtf(str(value))
            except Exception:
                report.error(path, f"keine gültige EDTF-Angabe in {key}: {value!r}")


def validate(root: Path) -> Report:
    report = Report()
    validator = Validator(str(SCHEMA), validation_plugins=[JsonschemaValidationPlugin(closed=True)])

    entities: dict[str, tuple[Path, dict]] = {}
    for path in sorted((root / "data").glob("*/*.yaml")):
        folder, key = path.parent.name, path.stem
        if folder not in CLASSES:
            report.error(path, f"unbekannter Ordner data/{folder}")
            continue
        data = load(path, report)
        if data is None:
            continue
        expected_id = f"{folder}/{key}"
        if data.get("id") != expected_id:
            report.error(path, f"id muss {expected_id} lauten, ist {data.get('id')!r}")
        if data.get("type") != CLASSES[folder]:
            report.error(path, f"type muss {CLASSES[folder]} lauten, ist {data.get('type')!r}")
            continue
        check_schema(validator, path, data, CLASSES[folder], report)
        check_edtf(path, data, report)
        entities[expected_id] = (path, data)

    jobs: dict[str, Path] = {}
    for path in sorted((root / "jobs").glob("*.yaml")):
        data = load(path, report)
        if data is None:
            continue
        expected_id = f"job/{path.stem}"
        if data.get("job_id") != expected_id:
            report.error(path, f"job_id muss {expected_id} lauten")
        check_schema(validator, path, data, "Job", report)
        check_edtf(path, data, report)
        if not str(data.get("model", "")).startswith(AGENT_MODEL_PREFIX):
            report.error(path, f"Agenten laufen mit Sonnet; model ist {data.get('model')!r}")
        jobs[expected_id] = path

    for path in sorted((root / "coverage").glob("**/*.yaml")):
        data = load(path, report)
        if data is None:
            continue
        expected_id = f"coverage/{path.stem}"
        if data.get("coverage_id") != expected_id:
            report.error(path, f"coverage_id muss {expected_id} lauten")
        check_schema(validator, path, data, "CoverageEntry", report)
        check_edtf(path, data, report)
        job = (data.get("searched_by") or {}).get("job")
        if job and job not in jobs:
            report.error(path, f"unbekannter Auftrag {job}")

    check_references(entities, jobs, report)
    check_required_references(entities, report)
    check_fiction(entities, report)
    check_duplicates(entities, report)
    check_statement_ids(entities, report)
    check_cycles(entities, report)
    check_reviews(entities, report)
    check_claimants(entities, report)
    check_passages(root, entities, report)
    return report


def check_statement_ids(entities, report: Report) -> None:
    seen: dict[str, str] = {}
    for eid, (path, data) in entities.items():
        for prop, st in statements(data):
            sid = st.get("statement_id")
            if not sid:
                continue  # fehlt: meldet das Schema; tools/assign_ids.py ergänzt
            if sid in seen:
                report.error(path, f"Aussagekennung {sid} auch in {seen[sid]}")
            else:
                seen[sid] = eid


def check_cycles(entities, report: Report) -> None:
    """replaced_by, located_in und part_of dürfen keine Zyklen bilden."""
    def targets(data, prop):
        value = data.get(prop)
        if prop == "replaced_by":
            return [value] if value else []
        return [st.get("entity_value") for st in value or [] if st.get("rank") != "deprecated"]

    for prop in ("replaced_by", "located_in", "part_of"):
        for start, (path, _) in entities.items():
            stack, seen = [start], set()
            while stack:
                current = stack.pop()
                for nxt in targets(entities.get(current, (None, {}))[1], prop):
                    if nxt == start:
                        report.error(path, f"Zyklus über {prop} zurück zu {start}")
                        stack = []
                        break
                    if nxt not in seen and nxt in entities:
                        seen.add(nxt)
                        stack.append(nxt)


def check_reviews(entities, report: Report) -> None:
    for eid, (path, data) in entities.items():
        for prop, st in statements(data):
            if st.get("reviewed_by") or st.get("review_hash"):
                if not (st.get("reviewed_by") and st.get("reviewed_at") and st.get("review_hash")):
                    report.error(path, f"{st.get('statement_id', prop)}: Prüfung braucht reviewed_by, reviewed_at und review_hash")
                elif st["review_hash"] != statement_hash(st):
                    report.warn(path, f"{st.get('statement_id', prop)} wurde nach der Prüfung geändert; erneut prüfen")


def check_claimants(entities, report: Report) -> None:
    for eid, (path, data) in entities.items():
        for prop, st in statements(data):
            for ref in st.get("references") or []:
                claimant = ref.get("asserted_by")
                if ref.get("evidence_type") == "self_statement" and claimant not in (None, "person/jackie-leven", "unknown"):
                    report.warn(path, f"{st.get('statement_id', prop)}: Selbstaussage, aber asserted_by ist {claimant}")


def check_passages(root: Path, entities, report: Report) -> None:
    """Textstellen müssen zu einem bekannten Dokument gehören und, sofern ein
    Verzeichnis passages/manifest.txt besteht, darin verzeichnet sein."""
    manifest_path = root / "passages" / "manifest.txt"
    manifest = None
    if manifest_path.exists():
        manifest = {line.split()[0] for line in manifest_path.read_text().splitlines()
                    if line.strip() and not line.startswith("#")}
    for eid, (path, data) in entities.items():
        for key, value in walk(data):
            if key != "passage" or not isinstance(value, str):
                continue
            doc = value.split("#", 1)[0]
            if doc not in entities:
                report.error(path, f"Textstelle {value} gehört zu keinem bekannten Dokument")
            elif manifest is not None and value not in manifest:
                report.error(path, f"Textstelle {value} fehlt im Verzeichnis der Textstellen")


def conflicts(entities):
    """Befund je einwertiger Eigenschaft: disputed (unvereinbare Werte ohne
    bevorzugten), deviating (bevorzugter Wert mit abweichenden) oder nichts."""
    found = []
    for eid, (path, data) in entities.items():
        for prop in SINGLE_VALUED.get(data["type"], []):
            active = [st for st in data.get(prop) or [] if st.get("rank") != "deprecated"]
            if prop == "performance_status":
                # announced und unknown widersprechen keinem anderen Status:
                # ein Konzert, das stattfand, war in der Regel auch angekündigt.
                active = [st for st in active if st.get("status_value") not in ("announced", "unknown")]
            values = {json.dumps(statement_value(st), sort_keys=True) for st in active}
            if len(values) < 2:
                continue
            preferred = [st for st in active if st.get("rank") == "preferred"]
            found.append((eid, prop, "deviating" if preferred else "disputed", sorted(values)))
    return found


def check_references(entities, jobs, report: Report) -> None:
    for eid, (path, data) in entities.items():
        for key, value in walk(data):
            if key in REF_KEYS and isinstance(value, str) and value != "unknown" and value not in entities:
                report.error(path, f"Verweis auf unbekannte Entität {value} ({key})")
            if key == "job" and isinstance(value, str) and value not in jobs:
                report.error(path, f"Verweis auf unbekannten Auftrag {value}")


def check_required_references(entities, report: Report) -> None:
    for eid, (path, data) in entities.items():
        for prop in REFERENCE_REQUIRED.get(data["type"], []):
            for i, statement in enumerate(data.get(prop) or []):
                if not statement.get("references"):
                    report.error(path, f"{prop}[{i}] braucht mindestens einen Beleg")


def check_fiction(entities, report: Report) -> None:
    fiction = {eid for eid, (_, d) in entities.items() if d["type"] == "Document" and d.get("fiction")}
    for eid, (path, data) in entities.items():
        for key, value in walk(data):
            if key == "document" and value in fiction:
                report.error(path, f"{value} ist Fiktion und kann nicht als Beleg dienen")


def check_duplicates(entities, report: Report) -> None:
    seen: dict[tuple[str, str], str] = {}
    confirmed: dict[tuple[str, str], str] = {}
    for eid, (path, data) in entities.items():
        sig = (data["type"], normalize(data.get("label", "")))
        if sig in seen:
            report.warn(path, f"mögliche Doppelung mit {seen[sig]} (gleiche Bezeichnung)")
        else:
            seen[sig] = eid
        for ext in data.get("identifiers") or []:
            if ext.get("match_status") == "confirmed":
                k = (ext["scheme"], str(ext["external_value"]))
                if k in confirmed:
                    report.error(path, f"bestätigte Kennung {k[0]}:{k[1]} auch bei {confirmed[k]}")
                else:
                    confirmed[k] = eid


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]).resolve() if args else ROOT
    report = validate(root)
    if "--konflikte" in sys.argv:
        entities = {}
        for path in sorted((root / "data").glob("*/*.yaml")):
            data = yaml.load(path.read_text(encoding="utf-8"), Loader=_Loader)
            entities[data["id"]] = (path, data)
        for eid, prop, kind, values in conflicts(entities):
            print(f"Konflikt {eid} {prop}: {kind} {', '.join(values)}")
    for w in report.warnings:
        print(f"Hinweis  {w}")
    for e in report.errors:
        print(f"Fehler   {e}")
    print(f"{len(report.errors)} Fehler, {len(report.warnings)} Hinweise")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
