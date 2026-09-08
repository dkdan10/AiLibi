# Disposition the 2026-09-06 review and its follow-up by id

**Status:** done

## Outcome

Every finding id from the 2026-09-06 review and its follow-up has exactly one
stated disposition somewhere a reader can find it, and each of the first
review's seven workflow recommendations has an explicit adopt-or-decline with a
reason. A reader can go from any id to what was done about it without
reconstructing it from commit messages.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce a disposition
claim against the code before writing "repaired"; a green test is not by itself
a repair of the filed defect.

The id inventories are `audits/review-2026-09-06/REVIEW_APPENDIX_findings.md`
and the follow-up appendix
[`audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md`](../../audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md),
alongside [the follow-up report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md).
The follow-up's findings FU-DISP-1 and FU-DISP-2 are the gap this card closes:
most appendix ids have no disposition anywhere in the tree, and the first
review's section 11 recommendations were declined by omission rather than by
decision. `docs/cleanup-dispositions.md` is the existing shape — grouped id
rows, a current disposition, and the evidence or owner for each — and its
opening rules already state the distinctions this card must preserve: a retained
limitation is not a repaired defect, and an implemented experimental candidate is
not an adopted behaviour.

## Acceptance

- [x] Every id in `REVIEW_APPENDIX_findings.md` and every id in
  `REVIEW_APPENDIX_FOLLOWUP.md` appears exactly once, with one of: **repaired**
  (naming the commit or card that repaired it), **retained** (with the reason and
  an explicit reconsideration trigger), **refuted** (with the reasoning), or
  **routed** to a named card. No id appears twice and none is left out.
- [x] Each of the seven workflow recommendations in section 11 of
  `audits/review-2026-09-06/REVIEW_REPORT.md` gets adopt or decline with a
  one-line reason. Declining is a legitimate outcome; declining silently is not.
- [x] The shape follows `docs/cleanup-dispositions.md`: grouped id rows, current
  disposition, evidence or owner. A reader can go id to disposition to evidence
  without opening a commit log.
- [x] A new additive record at
  `audits/review-2026-09-06/followup-correction-record.md` carries the follow-up
  dispositions. It is additive: `correction-record.md` and both review reports
  are not edited to agree with it.
- [x] No historical severity label, refuter vote or verdict is rewritten. Where
  this tree disagrees with a filed severity, the disagreement is stated as a new
  note beside the original, which stays as filed.
- [x] No review count is republished as a current measurement of this tree. A
  finding count describes the bytes reviewed then; a claim about now needs its
  own reproduction.
- [x] A spot check proves the table is not decorative: pick three ids marked
  repaired, reproduce their original triggers, and record that they no longer
  fire.

## Constraints

Documentation only — no runtime, test or recording change, no provider calls, no
new gate. This card can run in parallel with every other card in the batch
because it shares no source file with any of them; it does read their Results, so
re-read a card before writing its disposition rather than writing from the plan.
Historical review bytes are preserved verbatim: the two reports and two
appendices are inputs, never edited. Any `audits/` byte change requires
refreshing the `audits/` row of `docs/artifacts.md` — `verify_ml_evidence.py`
compares that row's exact tracked-byte total and file count against disk.

## Expected scope

`docs/cleanup-dispositions.md`, a new
`audits/review-2026-09-06/followup-correction-record.md`, the `docs/artifacts.md`
audits row, and `tasks/review-ledger.md` where a disposition names a commit.
`audits/review-2026-09-06/REVIEW_REPORT.md`,
`REVIEW_APPENDIX_findings.md`, `REVIEW_REPORT_FOLLOWUP.md` and
`REVIEW_APPENDIX_FOLLOWUP.md` are read-only inputs.

## Record impact

No recorded, rendered or served bytes change; no committed recording, report or
measurement is touched. A disposition table is an account of decisions, not
evidence that a defect is gone: a row saying "repaired" points at the commit and
the reproduction that establishes it. `audits/` tracked bytes move when the new
record lands, so the `docs/artifacts.md` registry row moves with them. Adoption
status of every experiment is unchanged by anything written here.

## Validation

`uv run python scripts/check_doc_facts.py` (link resolution and the audits
index), then `uv run python scripts/validate_task_docs.py`, then
`uv run pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_verify_ml_evidence.py -q`,
then `bash scripts/check.sh`.

## Results

Documentation only. No runtime, test or recording byte changed; no provider was
called. Files written: `docs/cleanup-dispositions.md` (new final section),
`audits/review-2026-09-06/followup-correction-record.md` (new), the
`audits/` row of `docs/artifacts.md`, one paragraph in
`audits/review-2026-09-06/README.md` so the new record is reachable from the
review index, and one dated section in `tasks/review-ledger.md` indexing the
commits the dispositions name. The two reports, the two appendices and
`correction-record.md` are byte-unchanged.

### What was decided

- **Where each half lives.** The first review's ids — the 215 in
  `REVIEW_APPENDIX_findings.md` plus the 17 further original ids only the
  follow-up's section A carries — are dispositioned in
  `docs/cleanup-dispositions.md`, extending its existing grouped-row shape
  (`| IDs | Current disposition | Evidence / owner |`). The follow-up's own 181
  new ids are dispositioned in the new additive record. Each document points at
  the other, so a reader entering from either finds every id.
- **One disposition word per id**, from the card's four: repaired (naming the
  commit), routed (naming the card), retained (reason plus reconsideration
  trigger), refuted (reasoning). Where a finding was repaired in part, the id
  keeps the single word that describes it now and the row names the residual id
  and where that one is dispositioned — `C2-4` is repaired and its residue is
  `NC4-2`/`FU-5`; `C2-2` is retained for the half no oracle covers and its ballot
  half is `C1-01`/`G5-2`, repaired.
- **Routed rows claim ownership, not completion.** All six concurrent cards were
  re-read at `origin/main` before routing, and only ids a card actually names
  were routed to it. Findings the review listed as nonblocking that no queued
  card names (the accounts placement tests `NC5-05`/`NC5-06`, the viewer copy
  `NG4-1`–`NG4-10`, `GC-6`) are retained with the adjacent card named as the
  trigger, rather than routed to a card that does not own them.
- **`FU-DISP-3`(b) and `NC5-10` are repaired, not retained.** The branch policy
  the first review's recommendation 6 asked for was decided in #436
  (`081aee15`, content `e9c47c76`): `AGENTS.md`, `docs/workflow.md` and
  `.github/workflows/ci.yml` no longer encode the cleanup branch. The 25 files
  that still contain the string are historical records naming a real branch.
- **Recommendation 1's disposition-id rule is declined as a gate** and answered as
  a document. A gate pinning "disposition ids equal the union of the registers"
  would have to be rewritten for every future review; the equivalent property is
  checked here by the command below and stated in both documents.
- **`tasks/review-ledger.md` gets a finding-to-commit index only.** The per-commit
  register `P-10` asks for belongs to the nonblocking card, which owns that file
  in the post-merge plan's ownership table; this card's section says so
  explicitly to keep the two writers from colliding.

### Verification

Contract sections this follows: `docs/workflow.md` "One card per change" (card
shape and the reopen convention), "Records and experiments" (a later experiment
never changes an earlier verdict), `AGENTS.md` craft rules 5 and 7 (claims name
their enforcing mechanism; declared record impact), and
`tasks/post-merge-plan.md` outcome 1 and its ownership table.

Id coverage, the acceptance property, computed from the committed bytes of both
appendices and both disposition documents:

```text
$ .venv/bin/python <the inventory script quoted below>
first-pass ids (both appendices): 232
follow-up new-finding ids: 181
inventory total: 413
dispositioned: 413
missing: 0
dispositioned twice: 0
id in no appendix: 0
exit=0
```

The script reads the first column of every table row in
`REVIEW_APPENDIX_findings.md`, of section A and section B.6 of
`REVIEW_APPENDIX_FOLLOWUP.md`, and of every `#### <id>` finding heading in that
appendix; then the first column of every table row in the new record and in
`docs/cleanup-dispositions.md` after its `## The 2026-09-06 review: first-pass
findings` heading. It fails on a missing id, an id dispositioned in both
documents, and an id in neither appendix. It is a check of this card's own
output, not a committed gate — recommendation 1's third rule is declined above.

```python
# saved to a scratch file and run with .venv/bin/python <file> .
import re, pathlib
ID = re.compile(r"([A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)")
ROOT = pathlib.Path(".")
def rows(path, keep):
    out, section = set(), ""
    for line in (ROOT / path).read_text().splitlines():
        if line.startswith("#"):
            section = line
        if keep(section) and line.startswith("| "):
            m = ID.match(line.split("|")[1].strip().replace("**", ""))
            if m:
                out.add(m.group(1))
        if keep(section) and line.startswith("#### "):
            m = ID.match(line[5:])
            if m:
                out.add(m.group(1))
    return out
appendix = "audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md"
first = rows("audits/review-2026-09-06/REVIEW_APPENDIX_findings.md", lambda s: True)
first |= rows(appendix, lambda s: s.startswith("## A."))
new = rows(appendix, lambda s: s.startswith("### B.6") or s.startswith("#### "))
placed = {}
for doc, anchor in (
    ("docs/cleanup-dispositions.md", "## The 2026-09-06 review: first-pass findings"),
    ("audits/review-2026-09-06/followup-correction-record.md", None),
):
    started = anchor is None
    for line in (ROOT / doc).read_text().splitlines():
        started = started or line.strip() == anchor
        if started and line.startswith("| "):
            for token in re.split(r"[,\s]+", line.split("|")[1].strip().replace("**", "")):
                if ID.fullmatch(token.strip("`")):
                    placed.setdefault(token.strip("`"), []).append(doc)
every = first | new
print("missing:", sorted(i for i in every if i not in placed))
print("twice:", sorted(i for i, d in placed.items() if len(d) > 1))
print("in no appendix:", sorted(i for i in placed if i not in every))
```

Spot check (acceptance item 7), in full in
`audits/review-2026-09-06/followup-correction-record.md`: three ids marked
repaired, each original trigger re-run on this tree with the fake provider and
each paired with an adverse control.

1. `G5-1`/`GM-1`: all four `build_sample_report.py --sample-dir <set> --check`
   runs print "is consistent with its replays" and exit 0; on a scratch copy of
   `replays/samples/4p1i` with one game's `seed` changed from 0 to 999 the same
   command prints STALE and exits 1.
2. `C2-6`/`CARD-01`: `.venv/bin/python -m pytest tests/orchestrator/
   --collect-only -q -p no:cacheprovider` collects 583 tests, exit 0. Removing
   the two-line `sys.path` bootstrap from
   `tests/orchestrator/test_aborted_meeting_records.py` reproduces the filed
   failure ("Interrupted: 1 error during collection", 567 collected); restoring
   it returns 583 collected, exit 0, and `git status` shows the file unchanged.
3. `FU-2`: regenerating `replays/samples/4p1i` into a scratch copy reproduces the
   committed report byte for byte (`cmp` silent). Adverse control in one process
   on the same rebuilt report: the pre-correction serialization
   (`report.model_dump_json(indent=2)`, taken from `29b7bb4a`'s diff) produces
   2,878,097 bytes against the committed 2,816,272, while the current writer
   produces exactly 2,816,272.

Planted failure for the artifacts row (the only machine-checked number this card
changes): reverting `docs/artifacts.md`'s `audits/` row to `14,850,288 tracked
bytes / 202 files` makes `uv run python scripts/verify_ml_evidence.py` print
`[ FAIL ] in-tree family inventory` with both notes — "promises 202 files, the
index tracks 203" and "promises 14,850,288 tracked bytes, the tracked files
contain 14,876,233 bytes". Restoring the recomputed row returns exit 0. The row
was recomputed with the change staged: `git ls-files audits | wc -l` prints 203
and `git ls-files -z audits | xargs -0 wc -c | tail -1` prints 14876233.

The card's Validation section, in order:

- `uv run python scripts/check_doc_facts.py` — exit 0. Its published-document
  link rule covers `audits/review-2026-09-06/README.md`, so the new record's path
  is resolved from the index; every relative link in 11 front-door and published
  documents resolves.
- `uv run python scripts/validate_task_docs.py` — exit 0: "390 historical phase
  tasks and 390 prompts; 43 work cards."
- `uv run pytest tests/scripts/test_check_doc_facts.py
  tests/scripts/test_verify_ml_evidence.py -q` — 364 passed in 302.63s.
- `bash scripts/check.sh` — exit 0: ruff and format clean, "Contracts: 4 kept, 0
  broken", document and generated-type checks green, "Success: no issues found in
  469 source files", "7201 passed, 20 skipped, 3 xfailed" in 214.67s, 514
  frontend tests in 19 files, and the production build.

Also run, because the post-merge plan requires them of every card:
`bash scripts/verify_samples.sh` — all 100 canonical recordings verified clean
(50 + 50), exit 0; the four `scripts/build_sample_report.py --check` runs — four
exit 0; `pytest tests/orchestrator/ --collect-only` in a fresh interpreter — 583
collected, exit 0; `uv run python scripts/verify_ml_evidence.py` — 60 checks, 48
OK, 0 FAIL, 7 ABSENT (evidence-branch bytes, the expected state of this
checkout), 5 INFO. `cd frontend && npm run e2e` was not run: no served DTO,
schema or component byte changes here.

The frozen held-out manifest is untouched. This card edits no file in
`experiments/held_out_prefixes.py`'s `GENERATOR_SOURCES`, so no restamp was due;
`tests/experiments/test_held_out_prefixes.py` passes inside the full gate, and no
prefix was printed or opened.

### Limitations

- A disposition table is an account of decisions. Three repaired rows were
  reproduced here; the other repaired rows rest on the commit each names and on
  that commit's own adverse controls, not on a fresh reproduction.
- Routed rows are ownership statements. Six cards are in flight on their own
  branches and none is finished; a routed id is still live until its card lands.
  `retire-temporal-evidence-v1` is additionally blocked on an adopting record for
  evidence v2, so the four v1 defects routed to it stay live indefinitely.
- Retained rows are judgments about scope and cost, not proofs that a finding is
  harmless. Each states the trigger that should reopen it; nothing enforces those
  triggers, which is the durable-gate half of recommendation 1 that this card
  declined and recommendation 2 that it routed to the owner.
- Two of the seven recommendations are adopted as practice with their gate change
  routed to the owner (2 and 7), and two are split adopt/decline (1 and 4). Each
  half is stated; none is left silent.
- The id inventory is defined by the extraction rule quoted above. An id that
  appears only in the appendices' prose — never as a table row or a finding
  heading — is outside it; every such mention encountered while writing was an
  id already dispositioned under its own row.
