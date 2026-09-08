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

- [x] Review correction: the unescaped `|` inside the code span of the retained
  `P-03` row no longer splits that row into four cells, so its Evidence link is
  rendered again. Proved by a cell-count scan and by a GFM render of both changed
  documents — `cells.py` and `render.py` in the round-1 subsection below; the scan
  fails on the committed defect and passes now.
- [x] Review correction: the follow-up record's claim that
  `recorded-provenance-gaps` "names all six" is replaced by what that card holds
  at `origin/main` — five ids by name, `NG1-7` by mechanism. Proved by
  `scratchpad/routes.py` over the six cards exported with
  `git show origin/main:tasks/work/<card>.md`, quoted below.
- [x] Review correction: the Results' routing rule now states the rule that was
  actually applied — routed when the target card names the id **or** carries an
  acceptance item repairing the same defect — and every routed row says which of
  the two applies per id. Proved by the same per-id, per-card scan below (32
  named, 16 by mechanism, of 48 routed); the retained `NC5-05` / `NC5-06` row now
  states the same test, so routed and retained are decided by one rule.
- [x] Review correction: the PR body's "routed only where a card names the id"
  bullet is replaced by the same corrected rule, so the head and the PR agree.
- [x] Review correction: the cleanup-branch-string count in
  `docs/cleanup-dispositions.md` is no longer the pre-write count published as a
  fact about the tree the write produces. Both places now carry the `git grep -l`
  command and both figures — 25 at `201849fc`, 27 at this head — and this card
  states neither number without naming the tree it belongs to. The literal string
  is deliberately kept out of this card so the published count stays exactly the
  two documents that carry it plus the 25 inherited files.
- [x] Review correction: the same count in the follow-up record's retained
  `P-03` row carries the same command and both figures.
- [x] Review correction: `CARD-02`'s two filings are no longer collapsed into one
  repaired row. Its source-pin filing stays repaired under `M5-02`; its
  stale-validation filing is retained in the drifted-Results row, which is the
  word its one row now carries, and `tasks/review-ledger.md` says the same.
- [x] Review correction: `P1-2`, `C7b-9` and `G4-9` — withdrawn by the first
  review's own section 9 and never filed in an appendix — have a refuted row, and
  the inventory now derives them from that section rather than omitting them.
  Perturbed proof: the same script against the documents at `7cbf9786` prints
  `missing: ['C7b-9', 'G4-9', 'P1-2']`.
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
  re-read at `origin/main` (`201849fc`) before routing. An id is routed when that
  card **names it by id** or when the card carries an **acceptance item that
  repairs the same defect**; each routed row says which of the two applies to
  each id it carries, and the sixteen by-mechanism ids are listed with their
  items in the round-1 subsection below. An id that is neither named nor covered
  is retained with the adjacent card named as its reconsideration trigger, even
  where that card edits the same module — the accounts placement tests
  `NC5-05`/`NC5-06`, the viewer copy `NG4-1`–`NG4-10` and `GC-6`. (Round 1
  correction: this bullet first claimed that only ids a card names were routed,
  which was false for sixteen of them; the routing itself did not change.)
- **`FU-DISP-3`(b) and `NC5-10` are repaired, not retained.** The branch policy
  the first review's recommendation 6 asked for was decided in #436
  (`081aee15`, content `e9c47c76`): `AGENTS.md`, `docs/workflow.md` and
  `.github/workflows/ci.yml` no longer encode the cleanup branch. Every file that
  still contains its name is a historical record naming a real branch; both
  disposition documents give the `git grep -l` count with the tree it was
  measured on, rather than a bare number.
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
appendices, the first review's report and both disposition documents (the
report-only ids were added in round 1; the figures below are this head's):

```text
$ .venv/bin/python <the inventory script quoted below> .
first-pass appendix ids: 232
follow-up new-finding ids: 181
report-only withdrawn ids: ['C7b-9', 'G4-9', 'P1-2']
inventory total: 416
dispositioned: 416
missing: []
dispositioned twice: []
dispositioned but in no register: []
```

The script reads the first column of every table row in
`REVIEW_APPENDIX_findings.md`, of section A and section B.6 of
`REVIEW_APPENDIX_FOLLOWUP.md`, and of every `#### <id>` finding heading in that
appendix; it adds the ids at the head of each bullet in `REVIEW_REPORT.md`'s
section 9, the review's own withdrawals, which is where the three report-only ids
come from. It then reads the first column of every table row in the new record
and in `docs/cleanup-dispositions.md` after its `## The 2026-09-06 review:
first-pass findings` heading. It fails on a missing id, an id dispositioned in
both documents, and a dispositioned id that is in neither register. It is a check
of this card's own output, not a committed gate — recommendation 1's third rule
is declined above.

```python
# saved to a scratch file and run with .venv/bin/python <file> .
import re, pathlib, sys
ID = re.compile(r"([A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)")
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
A = "audits/review-2026-09-06/"
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
def withdrawn(path):  # the report-only ids of section 9, from its bullet heads
    out, section = set(), ""
    for line in (ROOT / path).read_text().splitlines():
        if line.startswith("## "):
            section = line
        if section.startswith("## 9.") and line.startswith("- "):
            head = re.split(r"[(:]", line[2:])[0]
            out |= {t for t in re.split(r"[,/]| and ", head) if ID.fullmatch(t.strip())}
    return {t.strip() for t in out}
appendix = A + "REVIEW_APPENDIX_FOLLOWUP.md"
first = rows(A + "REVIEW_APPENDIX_findings.md", lambda s: True)
first |= rows(appendix, lambda s: s.startswith("## A."))
new = rows(appendix, lambda s: s.startswith("### B.6") or s.startswith("#### "))
report_only = withdrawn(A + "REVIEW_REPORT.md") - first - new
placed = {}
for doc, anchor in (
    ("docs/cleanup-dispositions.md", "## The 2026-09-06 review: first-pass findings"),
    (A + "followup-correction-record.md", None),
):
    started = anchor is None
    for line in (ROOT / doc).read_text().splitlines():
        started = started or line.strip() == anchor
        if started and line.startswith("| "):
            for token in re.split(r"[,\s]+", line.split("|")[1].strip().replace("**", "")):
                if ID.fullmatch(token.strip("`")):
                    placed.setdefault(token.strip("`"), []).append(doc)
every = first | new | report_only
print("first-pass appendix ids:", len(first))
print("follow-up new-finding ids:", len(new))
print("report-only withdrawn ids:", sorted(report_only))
print("inventory total:", len(every))
print("dispositioned:", len(placed))
print("missing:", sorted(i for i in every if i not in placed))
print("dispositioned twice:", sorted(i for i, d in placed.items() if len(d) > 1))
print("dispositioned but in no register:", sorted(i for i in placed if i not in every))
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
changes), re-run at this head: reverting `docs/artifacts.md`'s `audits/` row to
the pre-card `14,850,288 tracked bytes / 202 files` makes
`uv run python scripts/verify_ml_evidence.py` print
`[ FAIL ] in-tree family inventory` with both notes — "promises 202 files, the
index tracks 203" and "promises 14,850,288 tracked bytes, the tracked files
contain 14,879,136 bytes". Restoring the recomputed row returns exit 0. The row
was recomputed with the change staged: `git ls-files audits | wc -l` prints 203
and `git ls-files -z audits | xargs -0 wc -c | tail -1` prints 14879136. (Round 0
recorded 14,876,233 here; the round-1 corrections added bytes to the record, and
the row moved with them.)

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
- Routed rows are ownership statements, and sixteen of the forty-eight routed ids
  are owned by mechanism rather than by name: the target card carries an
  acceptance item that repairs the same defect but does not print the id. Whoever
  implements that card can drop the id without noticing, which is the cost of
  routing by mechanism; each row names the item so the check is cheap. Six cards
  are in flight on their own branches and none is finished; a routed id is still
  live until its card lands.
  `retire-temporal-evidence-v1` is additionally blocked on an adopting record for
  evidence v2, so the four v1 defects routed to it stay live indefinitely.
- Retained rows are judgments about scope and cost, not proofs that a finding is
  harmless. Each states the trigger that should reopen it; nothing enforces those
  triggers, which is the durable-gate half of recommendation 1 that this card
  declined and recommendation 2 that it routed to the owner.
- Two of the seven recommendations are adopted as practice with their gate change
  routed to the owner (2 and 7), and two are split adopt/decline (1 and 4). Each
  half is stated; none is left silent.
- The id inventory is defined by the extraction rule quoted above: appendix table
  rows, appendix finding headings, and the ids at the head of each bullet in the
  first review's section 9. An id that appears only in prose — never as a row, a
  heading or a section 9 bullet head — is outside it. Round 1 found three ids in
  exactly that gap (`P1-2`, `C7b-9`, `G4-9`, withdrawn in the report and never
  filed in an appendix); they are dispositioned now, and the extraction rule was
  widened to derive them rather than to hard-code them. The prose sweep behind
  that widening is quoted in the round-1 subsection: what it leaves outside the
  inventory is section slugs and hyphenated prose, plus `CONC-2b` and
  `CARD-02-temporal`, which are shorthand for ids dispositioned under their own
  rows.

### Review corrections, round 1 (2026-09-08)

Eight blocking findings from three independent lenses, all of them about what
this card *claimed* rather than about where a finding was sent. No id changed
document, no disposition word changed except `CARD-02`'s, and no routing was
redone. The four review inputs stay byte-identical.

**1. A pipe inside a code span broke the retained `P-03` row.** The row carried
the literal `grep -rno '/tmp/' tasks/work/ | wc -l`; GFM ends a cell at an
unescaped `|` even inside a code span, so the row rendered four cells against a
three-column header, dropping the Evidence cell — the link to the section 11
table — and truncating the disposition mid-sentence. The pipe is now written
`\|` in both places that carry a pipeline inside a table. Two checks, each of
which fails on the committed bytes and passes now:

```text
$ .venv/bin/python scratchpad/cells.py docs/cleanup-dispositions.md \
    audits/review-2026-09-06/followup-correction-record.md
audits/review-2026-09-06/followup-correction-record.md:93 header=3 row=4   # at 7cbf9786
rows whose cell count differs from their header: 1 ; exit=1

rows whose cell count differs from their header: 0 ; exit=0                # at this head

$ .venv/bin/python scratchpad/render.py <both documents>                   # markdown-it, gfm-like
audits/review-2026-09-06/followup-correction-record.md:103 th=3 td=3
     P-03, P-09, FU-DISP-3, FU-DISP-4, NC5-07
     Retained. Process observations about the correction batch itself: ...
     <a href="../../docs/cleanup-dispositions.md#section-11-workflow-recommendations">The ledger's section 11 table</a>. ...
mismatched rows: 0
```

`cells.py` splits on `(?<!\\)\|` and compares each row's cell count with its
header's; `render.py` renders each row with `markdown_it` in `gfm-like` mode and
counts `<td>` against `<th>`. Both cover every table in both changed documents,
not only the repaired row.

**2. "which names all six" was false, and so was the routing rule.** Three
lenses filed this. The record said
[recorded provenance gaps](../../audits/review-2026-09-06/followup-correction-record.md#routed-to-a-queued-card)
"names all six"; that card at `origin/main` names five (`NC4-3`, `NC6-1`,
`NC6-2`, `NC3-1`, `FU-ORA-2`) and does not mention `NG1-7`. The Results claimed
more broadly that "only ids a card actually names were routed to it", which is
false for sixteen of the forty-eight routed ids. Re-measured against the six
cards as exported from `origin/main`:

```text
$ .venv/bin/python scratchpad/routes.py <cards exported with git show origin/main:...>
evidence-renderer-salience: named=3 by-mechanism=2 -> ['FU-D1', 'GR-6']
recorded-provenance-gaps: named=5 by-mechanism=1 -> ['NG1-7']
accounts-channel-hardening: named=7 by-mechanism=2 -> ['GR-3', 'FU-ALIBI-8']
fresh-deduction-instrument: named=0 by-mechanism=4 -> ['GEV-1', 'GEV-7', 'GEV-9', 'NG2-6']
nonblocking-followup-improvements: named=12 by-mechanism=4 -> ['FU-04', 'CONC-2', 'GC-3', 'GC-4']
retire-temporal-evidence-v1: named=5 by-mechanism=3 -> ['G1-02', 'M3-02', 'G4-2']
routed ids: 32 named by id, 16 by mechanism
```

The rule is now stated as it was applied — routed when the card names the id, or
when it carries an acceptance item that repairs the same defect — in the record's
routed section, in the ledger's routed section, in the "What was decided" bullet
above and in the PR body. Every routed row names which ids are by mechanism and
through which item: `FU-D1` and `GR-6` against the renderer card's eviction
fixture and its `N further subjects not shown` line; `NG1-7` against the
provenance card's "`view.json` is written without the mtime-derived `created_at`
before it is hashed"; `GR-3` and `FU-ALIBI-8` against the hardening card's
vent-certificate checkpoint sentence; the four `GEV`/`NG2-6` ids against the
instrument card's design, manifest and proof-free-prefix items; `FU-04`,
`CONC-2`, `GC-3` and `GC-4` against the nonblocking card's probe-descriptor item,
which names "the peer-unlink race the zero-byte rollback at `:60-67` opened";
`G1-02`, `M3-02` and `G4-2` against the retire card, which names their
re-filings. The retained `NC5-05`/`NC5-06` row now states the same test, so the
routed and retained sides are decided by one rule: those two are neither named
nor covered — no card carries an adverse-suite item for the destination-only
movement rule or the overlap guard — while the accounts card is only the adjacent
writer in those modules.

**3. The branch-string count was the pre-write count.** Both documents said "25
files" in the present tense about a tree their own bytes were part of. At this
head there are 27, the two extra being the two documents themselves:

```text
$ git grep -l "codex/cleanup" | wc -l          #   27  (this head)
$ git grep -l "codex/cleanup" 201849fc | wc -l #   25  (the tree the pass was written against)
```

Both places now carry the command and both figures with the tree each belongs to.
The literal string is deliberately absent from this card, so the published figure
stays the 25 inherited files plus those two documents. The sibling figure in the
same sentence was checked rather than assumed: `grep -rno '/tmp/' tasks/work/`
still prints 64 lines at this head, as the follow-up read it.

**4. `CARD-02` had two filings and one repaired row.** The appendix files
`CARD-02` twice — `REVIEW_APPENDIX_findings.md:88` (the published source pin) and
`:89` (a validation output in `tasks/work/temporal-observation-contract.md:172`
that no longer reproduces) — and the follow-up filed both as unresolved,
labelling the second `CARD-02(temporal)`. Only the pin half was dispositioned.
The pin half stays repaired and now sits in the `M5-02` row, which names it; the
stale-output half is retained in the drifted-Results row
(`C6-4, C6-8, CARD-02, CARD-03, ...`), whose rule is to label rather than to edit
a closed card's numbers. Retained is therefore the one word `CARD-02`'s one row
carries, on the `C2-2` precedent already in that document. The "each has one row
that covers both filings" sentence and `tasks/review-ledger.md`'s attribution of
`CARD-02` to the merge are corrected to match.

**5. Three ids had no disposition anywhere.** `P1-2`, `C7b-9` and `G4-9` are
withdrawn in the first review's own section 9 and never entered an appendix, so
the appendix-driven inventory never saw them while the Outcome claimed every id
was dispositioned. They now have a refuted row that quotes section 9 as filed,
and the inventory derives them from that section's bullet heads rather than
hard-coding them. The perturbed proof is the same script against the two
documents as they stood at `7cbf9786`:

```text
$ .venv/bin/python scratchpad/inventory.py <7cbf9786 documents + the four inputs>
report-only withdrawn ids: ['C7b-9', 'G4-9', 'P1-2']
inventory total: 416
dispositioned: 413
missing: ['C7b-9', 'G4-9', 'P1-2']

$ .venv/bin/python scratchpad/inventory.py .        # this head
inventory total: 416
dispositioned: 416
missing: []
dispositioned twice: []
dispositioned but in no register: []
```

A wider sweep over all four review inputs — every id-shaped token, not only rows
and headings — returns no further undispositioned finding id. What it does return
is `CONC-2b` (prose shorthand inside `CONC-2`'s own narrative),
`CARD-02-temporal` (the report's name for `CARD-02`'s second filing, now
dispositioned), `GAP-MLEV` without a number, and hyphenated prose and section
slugs such as `Pre-existing` or `NG1-investigation-runs`.

**Gates, re-run in full at this head.** `uv run python scripts/check_doc_facts.py`
— exit 0, including "every relative link in 11 front-door and published documents
resolves", which covers the new anchor link from the ledger's routed section into
the record's `## Routed to a queued card`.
`uv run python scripts/validate_task_docs.py` — exit 0: "390 historical phase
tasks and 390 prompts; 43 work cards".
`uv run pytest tests/scripts/test_check_doc_facts.py
tests/scripts/test_verify_ml_evidence.py -q` — 364 passed in 288.77s.
`bash scripts/check.sh` — exit 0 on the committed tree: ruff and format clean,
"Contracts: 4 kept, 0 broken", "Success: no issues found in 469 source files",
"7201 passed, 20 skipped, 3 xfailed", 514 frontend tests in 19 files, and the
production build. Same counts as round 0, which is the expected result of a
documentation-only round. Also re-run because the post-merge plan requires them of every
card: `bash scripts/verify_samples.sh` — "All 50 samples verified clean" twice,
exit 0; the four `scripts/build_sample_report.py --check` runs — four "is
consistent with its replays", four exit 0; `pytest tests/orchestrator/
--collect-only` in a fresh interpreter — 583 collected;
`uv run python scripts/verify_ml_evidence.py` — 60 checks, 48 OK, 0 FAIL, 7
ABSENT, 5 INFO, exit 0. `npm run e2e` was again not run: no served DTO, schema or
component byte changed. No live provider was called in this round, by any path.

**Record impact of this round.** `audits/` bytes moved again — 14,879,136 across
203 files — so the `docs/artifacts.md` row moved with them, with the planted
failure above re-run at this head. No recording, report, metric or adoption
verdict changed; no provider was called; the frozen held-out manifest is
untouched, and this round edits no file in `GENERATOR_SOURCES`, so no restamp was
due.
