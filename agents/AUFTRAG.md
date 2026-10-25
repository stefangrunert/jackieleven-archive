# Auftragsvorlage für Erschließungssitzungen

Diese Vorlage gilt für jede Sitzung, die einen Auftrag aus `jobs/` bearbeitet. Lies sie vollständig, bevor du anfängst, danach die Auftragsdatei, die dir die koordinierende Sitzung genannt hat.

## Rahmen

- **Modell:** Erschließungssitzungen laufen mit Sonnet (`claude-sonnet-5-5`). Das Modell steht in jeder Auftragsdatei und in `recorded_by` jedes Vorschlags.
- **Arbeitsort:** ein eigener Worktree des Datenrepositorys auf dem Branch `job/<schlüssel>`. Commits nur auf diesem Branch. Nie auf `main` committen, nie zusammenführen, nichts veröffentlichen.
- **Quellmaterial:** Pfade unter `materials` beziehen sich auf das Website-Repository unter `/Users/stefan/www/jackieleven`. Dort wird nur gelesen, nichts geändert.
- **Suchraum:** nur, was der Auftrag nennt. Was außerhalb liegt, aber auffällt, kommt als Hinweis in den Abschlussbericht.
- **Budget:** `budget` begrenzt Seitenabrufe, Websuchen und Teilaufgaben. Ist es erreicht, endet der Lauf mit einem Abschlussbericht über den erreichten Stand.

## Grundlage

- Datenmodell: `schema/jackieleven.yaml` und der Entwurf der Ontologie (Website-Repository, `.dev/ontologie.html`).
- Bestehende Daten unter `data/`. Vor jedem Anlegen prüfen, ob die Entität schon existiert: über Bezeichnung, Namensvarianten und externe Kennungen. Bei Treffern die bestehende Datei ergänzen statt eine neue anzulegen.

## Was du erzeugst

1. **Datendateien** unter `data/<type>/<key>.yaml`, eine Datei je Entität.
   - Schlüssel: Kleinbuchstaben, Ziffern, Bindestriche. Konzerte und andere datierte Ereignisse beginnen mit dem Datum, etwa `event/2004-03-26-bonn-harmonie`; Spielstätten mit Ort, etwa `place/bonn-harmonie`.
   - `label` in der Originalform. `type` entspricht dem Ordner.
   - Jede Aussage zu Zeit, Ort, Beteiligung, Mitgliedschaft und Durchführung trägt mindestens einen Beleg mit `document` und, wo möglich, `locator` und kurzem `quote`.
   - `evidence_type`: `self_statement` für Aussagen Levens über sich selbst, `third_party` für Angaben Dritter, `primary_document` für Kalender, Kataloge und Ähnliches, `inferred` für eigene Schlussfolgerungen (sparsam, mit `note`).
   - Zeitangaben als EDTF: `1975?` unsicher, `1975~` ungefähr, `[1976,1977]` eines von beiden, `2004-10/2004-11` Zeitraum, `198X` Jahrzehnt.
   - Widersprüchliche Angaben werden nicht aufgelöst. Jede wird eine eigene Aussage mit ihren Belegen; `rank` bleibt `normal`, außer der Auftrag sagt anderes.
   - Ein Konzertkalender belegt nur die Ankündigung (`announced`). `took_place` braucht einen Bericht, ein Foto, einen Mitschnitt oder eine spätere Erwähnung.
   - `recorded_by` an jeder Entität: `agent: claude-code`, `model`, `job`.
2. **Einen Eintrag im Abdeckungsregister** unter `coverage/<schlüssel>.yaml`: was durchgesehen wurde, mit welchem Verfahren, mit welchem Ergebnis, auch wenn nichts gefunden wurde. Nicht lesbare oder fehlende Teile unter `items_unavailable`.

## Was nicht erlaubt ist

- Volltexte Dritter übernehmen. Erlaubt sind Metadaten, eigene Zusammenfassungen und kurze wörtliche Zitate.
- Private Angaben über Angehörige oder nicht veröffentlichte Angaben über lebende Personen erfassen.
- Die Pastiche (`autobiografie/`) als Beleg verwenden.
- Externe Kennungen als `confirmed` markieren. Kandidaten tragen `match_status: proposed`.
- Daten erfinden. Was die Quelle nicht hergibt, bleibt leer.

## Prüfen und abschließen

1. `uv run python tools/validate.py` muss ohne Fehler durchlaufen. Hinweise auf mögliche Doppelungen klären oder im Bericht nennen.
2. Commit auf dem Auftragsbranch mit der Nachricht `<job-id>: <kurze Beschreibung>`.
3. Abschlussbericht an die koordinierende Sitzung: Zahl der neuen und ergänzten Entitäten je Klasse, Registereinträge, offene Fragen, Auffälligkeiten außerhalb des Suchraums, verbrauchtes Budget.
