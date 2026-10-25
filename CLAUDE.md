# jackieleven-archive

Daten und Werkzeuge des Jackie-Leven-Archivs. Das Schema steht in `schema/jackieleven.yaml`, die Entwürfe zu Ontologie, Suche und Erschließung im Website-Repository unter `/Users/stefan/www/jackieleven/.dev/`.

- Erschließungssitzungen lesen zuerst `agents/AUFTRAG.md` und laufen mit Sonnet.
- Nach jeder Änderung an Daten, Aufträgen oder Register: `uv run python tools/validate.py`.
- Nach Änderungen am Schema oder an der Validierung: `uv run pytest -q`.
- Bezeichner im Schema und in den Daten sind englisch, Erläuterungen deutsch.
- Nichts auf `main` committen, was nicht geprüft ist. Nichts veröffentlichen.
