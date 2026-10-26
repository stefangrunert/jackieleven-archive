# Coordinating extraction runs

These instructions apply to the coordinating session. It does not process sources itself; it assigns jobs, monitors them and prepares the review.

## Before the start

1. Read `CLAUDE.md`, `agents/AUFTRAG.md`, the job file and section 7 of the extraction draft (`/Users/stefan/www/jackieleven/.dev/erschliessung.html`).
2. Check with `uv run python tools/validate.py` that `main` is free of errors.
3. Read the usage limits of the subscription. If the 5-hour window is above 70 % or the weekly quota above 80 %, start no job and report the state.

## Starting a job

- Set the job to `running` in the job file and commit this to `main`.
- Start a separate session for the job: in the data repository, in its own worktree on the branch `job/<key>`, with **Sonnet** as the model.
- The brief to the session names only: the job file, the obligation to read `agents/AUFTRAG.md` first, and that it reports at the end.
- Start a further job only if the scopes do not overlap and the usage limits allow it.

## During the run

- Do not interfere with the job session's work unless it asks or exceeds its scope.
- Check the usage limits before answering questions with new work.

## After the run

1. Check the report against the branch: do the reported numbers match the files? Does the validation pass on the branch?
2. Read a sample of at least ten proposals against their source files. Check all quotations of the branch automatically against the source files.
3. Write a summary for Stefan, in German: new entities per class, register entry, sample result with concrete errors, open questions, quota used.
4. Set the job to `review`. Merge into `main` only with Stefan's approval.

Push only with Stefan's approval; the repository is public.
