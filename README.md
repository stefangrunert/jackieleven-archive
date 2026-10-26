# Jackie Leven Archive: data

Structured data on the Scottish songwriter Jackie Leven (1950–2011): people, places, events, works and documents, each statement backed by sources. The repository is the data foundation of the website jackieleven.com.

Status: schema v0.2 with the data of the first two extraction runs (89 concert reviews, 99 news items; 965 entities). Notes inside the data files, the schema descriptions and the validation messages are in German.

## Layout

| Path | Content |
|---|---|
| `schema/jackieleven.yaml` | schema in LinkML |
| `data/<type>/<key>.yaml` | one file per entity |
| `jobs/` | extraction jobs |
| `coverage/` | coverage register: what was searched where, including searches without results |
| `agents/AUFTRAG.md` | brief for extraction sessions |
| `agents/KOORDINATION.md` | instructions for the coordinating session |
| `tools/validate.py` | validation; `--konflikte` adds a report on conflicting statements |
| `tools/assign_ids.py` | assigns missing statement IDs |
| `tests/` | tests of the validation with sample data |

## Tools

```sh
uv sync
uv run python tools/assign_ids.py   # add missing statement IDs
uv run python tools/validate.py     # check data, jobs and register
uv run pytest -q                    # tests of the validation
```

The validation checks the schema (closed: unknown fields are errors), IDs and file names, resolvable references, sources on properties that require them, EDTF dates, the exclusion of the pastiche as a source, uniqueness of confirmed external IDs, the model of each job (Sonnet), unique statement IDs, cycles in `replaced_by`, `located_in` and `part_of`, review data (a statement changed after review is reported), claimants, and passages against `passages/manifest.txt` where it exists. Identical labels within a class are reported as possible duplicates.

## Licences

- Data, schema and original texts: [CC BY-NC 4.0](LICENSE-DATA.md). Verbatim quotations from sources, texts by Jackie Leven and third-party images are excluded.
- Tools (`tools/`, `tests/`): [MIT](LICENSE).
