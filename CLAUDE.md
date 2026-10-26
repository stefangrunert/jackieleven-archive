# jackieleven-archive

Data and tools of the Jackie Leven Archive. The schema is in `schema/jackieleven.yaml`; the drafts for ontology, search and extraction are in the website repository under `/Users/stefan/www/jackieleven/.dev/`.

- Extraction sessions read `agents/AUFTRAG.md` first and run with Sonnet.
- After every change to data, jobs or register: `uv run python tools/assign_ids.py`, then `uv run python tools/validate.py --konflikte`.
- After changes to the schema or the validation: `uv run pytest -q`.
- Identifiers in schema and data are English. Repository documents are English; notes in the data files and reports to Stefan are German.
- Commit nothing to `main` that has not been reviewed. The repository is public: push only with Stefan's approval.
