# Brief for extraction sessions

This brief applies to every session that works on a job from `jobs/`. Read it in full before you start, then read the job file the coordinating session named.

## Frame

- **Model:** extraction sessions run with Sonnet (`claude-sonnet-5-5`). The model is stated in every job file and in `recorded_by` of every proposal.
- **Workspace:** a separate worktree of the data repository on the branch `job/<key>`. Commit only to this branch. Never commit to `main`, never merge, never push or publish anything.
- **Source material:** paths under `materials` refer to the website repository at `/Users/stefan/www/jackieleven`. Read only; change nothing there.
- **Scope:** only what the job names. Anything outside the scope that stands out goes into the final report as a note.
- **Budget:** `budget` limits page fetches, web searches and subtasks. When it is reached, the run ends with a final report on the state reached.
- **Language:** notes in the data files and the final report are in German.

## Basis

- Data model: `schema/jackieleven.yaml` and the ontology draft (website repository, `.dev/ontologie.html`).
- Existing data under `data/`. Before creating an entity, check whether it already exists: by label, name variants and external IDs. On a match, extend the existing file instead of creating a new one.

## What you produce

1. **Data files** under `data/<type>/<key>.yaml`, one file per entity.
   - Keys: lower-case letters, digits, hyphens. Concerts and other dated events start with the date, e.g. `event/2004-03-26-bonn-harmonie`; venues start with the place, e.g. `place/bonn-harmonie`.
   - `label` in the original form. `type` matches the folder.
   - Every statement on time, place, participation, membership and performance status carries at least one reference with `document` and, where possible, `locator` and a short `quote`.
   - `quote` only verbatim from the source file (section „Zitate“ or original text quoted verbatim). No back-translation from the German summary and no rewording; without a suitable quotation `quote` stays empty, and an own summary goes into `scope`.
   - `evidence_type`: `self_statement` for Leven's statements about himself, `third_party` for statements by others, `primary_document` for calendars, catalogues and the like, `inferred` for own conclusions (sparingly, with `note`).
   - Dates as EDTF: `1975?` uncertain, `1975~` approximate, `[1976,1977]` one of these, `2004-10/2004-11` interval, `198X` decade.
   - Conflicting statements are not resolved. Each becomes a separate statement with its own references; `rank` stays `normal` unless the job says otherwise.
   - A concert calendar only supports the announcement (`announced`). `took_place` requires a review, a photo, a recording or a later mention.
   - Events known only from announcements or previews are recorded, but carry only `announced` and the note „Nur angekündigt; Durchführung nicht belegt.“
   - Author of a document: if the text names a person while the header of the source file says „anonym“, the name in the text applies. If the source file says the name probably belongs to a different article, the author stays empty.
   - `recorded_by` on every entity: `agent: claude-code`, `model`, `job`.
   - **Whose claim:** `asserted_by` on the reference names who makes the statement when that is not the author of the document, e.g. `person/jackie-leven` for a quotation by Leven in an interview. If unclear, `unknown`.
   - **Dependent sources:** if a document is evidently based on another one, such as a press release, that one goes under `derived_from`. Such documents do not count as independent confirmation.
   - **Certainty:** `rank` only controls display. If a statement is uncertain, even when it is the only one, set `certainty: uncertain` or `probable` with `note`.
   - **Review data** (`reviewed_by`, `reviewed_at`, `review_hash`) is never set by an agent; it is created when Stefan reviews.
   - **Statement IDs** (`statement_id`) are not assigned by hand; `tools/assign_ids.py` adds them.
2. **One entry in the coverage register** under `coverage/<key>.yaml`: what was searched, by which method, with which result, also when nothing was found. Unreadable or missing parts go under `items_unavailable`. `completeness` states how far the scope was actually seen: `attempted`, `fetched`, `readable`, `fully_checked` or `aborted`. A full-text search without hits is `readable`, not `fully_checked`: it does not prove that a name is absent from the collection.

## Not allowed

- Copying full texts by third parties. Metadata, own summaries and short verbatim quotations are allowed.
- Recording private details about relatives or unpublished details about living persons.
- Using the pastiche (`autobiografie/`) as a source.
- Marking external IDs as `confirmed`. Candidates carry `match_status: proposed`.
- Inventing data. What the source does not provide stays empty.

## Check and finish

1. `uv run python tools/assign_ids.py`, then `uv run python tools/validate.py --konflikte`; the validation must pass without errors. Reported conflicts are not errors but belong in the report. Resolve notes on possible duplicates or name them in the report.
2. Commit on the job branch with the message `<job-id>: <short description>`.
3. Final report to the coordinating session, in German: number of new and extended entities per class, register entries, open questions, observations outside the scope, budget used.
