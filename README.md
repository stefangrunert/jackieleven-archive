# Jackie-Leven-Archiv: Daten

Strukturierte Daten über den schottischen Songwriter Jackie Leven (1950–2011): Personen, Orte, Ereignisse, Werke und Dokumente, jede Angabe mit Belegen. Das Repository ist die Datengrundlage der Website jackieleven.com.

Stand: Schema v0, noch ohne Daten. Das Repository ist nicht veröffentlicht.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `schema/jackieleven.yaml` | Schema in LinkML |
| `data/<type>/<key>.yaml` | eine Datei je Entität |
| `jobs/` | Erschließungsaufträge |
| `coverage/` | Abdeckungsregister: was wo durchgesehen wurde, auch ohne Ergebnis |
| `agents/AUFTRAG.md` | Vorlage für Erschließungssitzungen |
| `tools/validate.py` | Validierung |
| `tests/` | Tests der Validierung mit Beispieldaten |

## Werkzeuge

```sh
uv sync
uv run python tools/validate.py     # Daten, Aufträge und Register prüfen
uv run pytest -q                    # Tests der Validierung
```

Die Validierung prüft das Schema (geschlossen, unbekannte Felder sind Fehler), Kennungen und Dateinamen, auflösbare Verweise, Belege bei belegpflichtigen Eigenschaften, EDTF-Zeitangaben, den Ausschluss der Pastiche als Beleg, bestätigte externe Kennungen auf Eindeutigkeit und das Modell der Aufträge (Sonnet). Gleiche Bezeichnungen derselben Klasse meldet sie als mögliche Doppelung.

## Lizenzen

- Daten, Schema und eigene Texte: [CC BY-NC 4.0](LICENSE-DATA.md). Wörtliche Zitate aus Quellen, Texte Jackie Levens und Bilder Dritter sind ausgenommen.
- Werkzeuge (`tools/`, `tests/`): [MIT](LICENSE).
