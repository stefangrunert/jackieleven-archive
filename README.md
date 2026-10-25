# Jackie-Leven-Archiv: Daten

Strukturierte Daten über den schottischen Songwriter Jackie Leven (1950–2011): Personen, Orte, Ereignisse, Werke und Dokumente, jede Angabe mit Belegen. Das Repository ist die Datengrundlage der Website jackieleven.com.

Stand: Schema v0.2 mit den Daten des ersten Erschließungslaufs (89 Konzertberichte, 408 Entitäten). Das Repository ist nicht veröffentlicht.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `schema/jackieleven.yaml` | Schema in LinkML |
| `data/<type>/<key>.yaml` | eine Datei je Entität |
| `jobs/` | Erschließungsaufträge |
| `coverage/` | Abdeckungsregister: was wo durchgesehen wurde, auch ohne Ergebnis |
| `agents/AUFTRAG.md` | Vorlage für Erschließungssitzungen |
| `tools/validate.py` | Validierung, mit `--konflikte` Bericht über widersprüchliche Angaben |
| `tools/assign_ids.py` | vergibt fehlende Aussagekennungen |
| `tests/` | Tests der Validierung mit Beispieldaten |

## Werkzeuge

```sh
uv sync
uv run python tools/assign_ids.py   # fehlende Aussagekennungen ergänzen
uv run python tools/validate.py     # Daten, Aufträge und Register prüfen
uv run pytest -q                    # Tests der Validierung
```

Die Validierung prüft das Schema (geschlossen, unbekannte Felder sind Fehler), Kennungen und Dateinamen, auflösbare Verweise, Belege bei belegpflichtigen Eigenschaften, EDTF-Zeitangaben, den Ausschluss der Pastiche als Beleg, bestätigte externe Kennungen auf Eindeutigkeit, das Modell der Aufträge (Sonnet), eindeutige Aussagekennungen, Zyklen in `replaced_by`, `located_in` und `part_of`, Prüfangaben (eine nach der Prüfung geänderte Aussage wird gemeldet), Urheber von Behauptungen und Textstellen gegen `passages/manifest.txt`, sofern vorhanden. Gleiche Bezeichnungen derselben Klasse meldet sie als mögliche Doppelung.

## Lizenzen

- Daten, Schema und eigene Texte: [CC BY-NC 4.0](LICENSE-DATA.md). Wörtliche Zitate aus Quellen, Texte Jackie Levens und Bilder Dritter sind ausgenommen.
- Werkzeuge (`tools/`, `tests/`): [MIT](LICENSE).
