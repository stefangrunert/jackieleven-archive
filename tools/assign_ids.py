"""Vergibt fehlende Aussagekennungen (statement_id) in den Datendateien.

Aufruf: uv run python tools/assign_ids.py [Wurzelverzeichnis] [--check]

Vorhandene Kennungen bleiben unverändert. Neue Kennungen werden aus Entität,
Eigenschaft und Inhalt der Aussage abgeleitet und danach nicht mehr geändert,
auch wenn sich der Inhalt ändert. Mit --check wird nur gemeldet, ob Kennungen
fehlen.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import ROOT, _Loader, is_statement, statement_hash  # noqa: E402


def assign(data: dict, used: set[str]) -> int:
    added = 0
    for prop, items in data.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not is_statement(item) or item.get("statement_id"):
                continue
            seed = f"{data['id']}|{prop}|{statement_hash(item)}"
            n = 0
            while True:
                sid = "st-" + hashlib.sha256(f"{seed}|{n}".encode()).hexdigest()[:12]
                if sid not in used:
                    break
                n += 1
            item_with_id = {"statement_id": sid, **item}
            item.clear()
            item.update(item_with_id)
            used.add(sid)
            added += 1
    return added


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    root = Path(args[0]).resolve() if args else ROOT
    files = sorted((root / "data").glob("*/*.yaml"))
    loaded = [(p, yaml.load(p.read_text(encoding="utf-8"), Loader=_Loader)) for p in files]
    used = {item["statement_id"] for _, d in loaded for items in d.values() if isinstance(items, list)
            for item in items if is_statement(item) and item.get("statement_id")}
    total = 0
    for path, data in loaded:
        added = assign(data, used)
        if added and not check:
            path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100),
                            encoding="utf-8")
        total += added
    print(f"{total} Aussagen ohne Kennung" + (" (nicht geschrieben)" if check else " ergänzt"))
    return 1 if check and total else 0


if __name__ == "__main__":
    sys.exit(main())
