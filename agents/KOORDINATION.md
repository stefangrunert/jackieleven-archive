# Koordination von Erschließungsläufen

Diese Anweisung gilt für die koordinierende Sitzung. Sie bearbeitet selbst keine Quellen, sondern vergibt Aufträge, überwacht sie und bereitet die Prüfung vor.

## Vor dem Start

1. Lies `CLAUDE.md`, `agents/AUFTRAG.md`, die Auftragsdatei und Abschnitt 7 des Erschließungsentwurfs (`/Users/stefan/www/jackieleven/.dev/erschliessung.html`).
2. Prüfe mit `uv run python tools/validate.py`, dass `main` fehlerfrei ist.
3. Lies die Nutzungsgrenzen des Abonnements. Liegt das 5-Stunden-Fenster über 70 % oder das Wochenkontingent über 80 %, starte keinen Auftrag und melde den Stand.

## Start eines Auftrags

- Setze den Auftrag in der Auftragsdatei auf `running` und committe das auf `main`.
- Starte eine eigene Sitzung für den Auftrag: im Datenrepository, in einem eigenen Worktree auf dem Branch `job/<schlüssel>`, mit **Sonnet** als Modell.
- Der Auftrag an die Sitzung nennt nur: die Auftragsdatei, die Pflicht, zuerst `agents/AUFTRAG.md` zu lesen, und dass sie am Ende berichtet.
- Starte einen weiteren Auftrag nur, wenn sich die Suchräume nicht überschneiden und die Nutzungsgrenzen es zulassen.

## Während des Laufs

- Nicht in die Arbeit der Auftragssitzung eingreifen, außer sie fragt oder überschreitet den Suchraum.
- Prüfe die Nutzungsgrenzen, bevor du auf Fragen mit neuer Arbeit antwortest.

## Nach dem Lauf

1. Prüfe den Bericht gegen den Branch: Stimmen die gemeldeten Zahlen mit den Dateien überein? Läuft die Validierung auf dem Branch fehlerfrei?
2. Lies eine Stichprobe von mindestens zehn Vorschlägen gegen ihre Quelldateien.
3. Schreibe eine Zusammenfassung für Stefan: neue Entitäten je Klasse, Registereintrag, Ergebnis der Stichprobe mit konkreten Fehlern, offene Fragen, Verbrauch an Kontingent.
4. Setze den Auftrag auf `review`. Zusammenführen auf `main` nur nach Stefans Zustimmung.

Nichts veröffentlichen, keine Pushes.
