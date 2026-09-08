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

- [x] Review correction: the branch-string figure published as a fact about this
  head is the one the quoted command prints on the committed tree — 28 files, not
  the 27 round 1 wrote — and the enumeration names all three files this pass adds
  (the ledger, the record and this card, which carries the literal in the
  commands it quotes). Proved by `git grep -l "codex/cleanup" | wc -l` on the
  committed tree, quoted with its output in the round-2 subsection beside the
  same command at `201849fc`, `7cbf9786` and `ab467228`.
- [x] Review correction: the sibling `/tmp` figure is the one its quoted command
  prints here — `grep -rno '/tmp/' tasks/work/ | wc -l` = 72 — with 64 scoped to
  `fd1f923c`, the commit the follow-up read, and the follow-up's wider `tasks/` +
  `docs/` headline (82 → 89) named as the different scope it is. "Unchanged from
  the follow-up's reading" is gone from both documents. Proved by the same
  command run at `fd1f923c`, `201849fc`, `ab467228` and this head, quoted below.
- [x] Review correction: the second check quoted for the pipe fix is one that can
  fail on the defect. The `<td>`-against-`<th>` render is withdrawn — GFM
  truncates a long row and pads a short one, so it is 3 against 3 either side of
  the fix — and is replaced by a link-survival scan that asserts every markdown
  link in a table row survives the GFM render. Planted proof: it prints the
  dropped `#section-11-workflow-recommendations` target and exits 1 on the
  `7cbf9786` documents, and exits 0 here.
- [x] Review correction: recommendation 2's reason states what the tree holds.
  `fresh-deduction-authorization.md` carries zero card-specific Validation
  commands, so the universal claim is replaced by the measured one — eight of the
  nine linked cards carry two to eight each — with that card named as a
  document-only exception. Proved by the per-card script quoted below, whose
  count for `accounts-channel-hardening.md` (8) matches the reviewer's own
  independent count.
- [x] Review correction: no id carries a fifth disposition word. The nine ids
  recorded as not reproducible at `fd1f923c` are labelled **Refuted** in that
  form, and the ledger's rule paragraph says not-reproducible is a form of
  refuted rather than a fifth word. Proved by a disposition-word scan over both
  documents' own sections, which prints the offending row and exits 1 on the
  committed bytes and exits 0 now.
- [x] Review correction: the unescaped `|` inside the code span of the retained
  `P-03` row no longer splits that row into four cells, so its Evidence link is
  rendered again. Proved by the cell-count scan quoted in full in the round-1
  subsection below, which fails on the committed defect (`:93 header=3 row=4`,
  exit 1) and passes now, and by the round-2 link-survival scan that replaces
  round 1's second check. (Round 2 rewrote this item's second half; the
  superseded sentence is quoted there.)
- [x] Review correction: the follow-up record's claim that
  `recorded-provenance-gaps` "names all six" is replaced by what that card holds
  at `origin/main` — five ids by name, `NG1-7` by mechanism. Proved by
  `git grep -c -E "\b<id>\b" origin/main -- tasks/work/<card>.md` per routed id,
  quoted below with both outcomes.
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
  fact about the tree the write produces. Both places carry the `git grep -l`
  command and both figures, and neither number is stated without the tree it
  belongs to. (Round 1 wrote "25 at `201849fc`, 27 at this head" and claimed the
  literal string was kept out of this card. Round 2 supersedes both halves: the
  head figure is 28 and this card is the third file. The superseded sentences are
  quoted in the round-2 subsection.)
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
`\|` in both places that carry a pipeline inside a table. Two checks over every
table in both changed documents — not only the repaired row — each of which fails
on the committed bytes and passes now. The first splits each row on an unescaped
pipe and compares its cell count with its header's:

```python
# scan.py — run as .venv/bin/python scan.py <file> ... ; exits 1 on a bad row
import pathlib, re, sys
SPLIT = re.compile(r"(?<!\\)\|")
def cells(line):
    parts = SPLIT.split(line.strip())
    return len(parts[1:-1]) if parts[0] == "" and parts[-1] == "" else len(parts)
bad = 0
for path in sys.argv[1:]:
    header = None
    for n, line in enumerate(pathlib.Path(path).read_text().splitlines(), 1):
        row = line.strip()
        if not row.startswith("|"):
            header = None
        elif header is None:
            header = cells(row)
        elif not set(row.replace("|", "").replace("\\", "").strip()) <= set("-: "):
            got = cells(row)
            if got != header:
                bad += 1
                print(f"{path}:{n} header={header} row={got}")
print(f"rows whose cell count differs from their header: {bad}")
sys.exit(1 if bad else 0)
```

```text
$ .venv/bin/python scan.py docs/cleanup-dispositions.md \
    audits/review-2026-09-06/followup-correction-record.md
audits/review-2026-09-06/followup-correction-record.md:93 header=3 row=4   # at 7cbf9786
rows whose cell count differs from their header: 1 ; exit=1

rows whose cell count differs from their header: 0 ; exit=0                # at this head
```

The second check round 1 quoted here — a `markdown_it` `gfm-like` render counting
`<td>` against `<th>` — is **withdrawn by round 2**, which found it could not
fail on the defect it was quoted as catching. Its replacement, a link-survival
scan that does fail on the committed bytes, is in the round-2 subsection below,
together with round 1's withdrawn wording and output block quoted verbatim.

**2. "which names all six" was false, and so was the routing rule.** Three
lenses filed this. The record said
[recorded provenance gaps](../../audits/review-2026-09-06/followup-correction-record.md#routed-to-a-queued-card)
"names all six"; that card at `origin/main` names five (`NC4-3`, `NC6-1`,
`NC6-2`, `NC3-1`, `FU-ORA-2`) and does not mention `NG1-7`. The Results claimed
more broadly that "only ids a card actually names were routed to it", which is
false for sixteen of the forty-eight routed ids. Each routed id was re-measured
against its card at `origin/main` with one command per id — a count when the card
names it, nothing and exit 1 when it does not:

```text
$ git grep -c -E "\bNC6-1\b" origin/main -- tasks/work/recorded-provenance-gaps.md
origin/main:tasks/work/recorded-provenance-gaps.md:2 ; exit=0
$ git grep -c -E "\bNG1-7\b" origin/main -- tasks/work/recorded-provenance-gaps.md
(no output) ; exit=1
```

Over all 48, per card — named by id, then the ids that are not named and are
therefore routed by mechanism:

```text
evidence-renderer-salience:        named=3   by-mechanism=2 -> FU-D1, GR-6
recorded-provenance-gaps:          named=5   by-mechanism=1 -> NG1-7
accounts-channel-hardening:        named=7   by-mechanism=2 -> GR-3, FU-ALIBI-8
fresh-deduction-instrument:        named=0   by-mechanism=4 -> GEV-1, GEV-7, GEV-9, NG2-6
nonblocking-followup-improvements: named=12  by-mechanism=4 -> FU-04, CONC-2, GC-3, GC-4
retire-temporal-evidence-v1:       named=5   by-mechanism=3 -> G1-02, M3-02, G4-2
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

**3. The branch-string count was the pre-write count.** *(**Superseded by round
2, item 1 below.** Quoting the two commands here put their literals into this
card, which moved both counts again: this item's head figures 27 and 64 are wrong
— they are 28 and 72 — and its closing claim that the literal string is absent
from this card is false of the bytes round 1 committed. Kept as filed, marked,
because the round-2 correction is a correction of it.)* Both documents said "25
files" in the present tense about a tree their own bytes were part of. At this
head there are 27, the two extra being the two documents themselves:

```text
$ git grep -l "codex/cleanup" | wc -l          #   27  (claimed for the round-1 head; superseded — it is 28)
$ git grep -l "codex/cleanup" 201849fc | wc -l #   25  (the tree the pass was written against; still 25)
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
$ .venv/bin/python <the inventory script quoted above> <a tree holding the 7cbf9786 documents>
report-only withdrawn ids: ['C7b-9', 'G4-9', 'P1-2']
inventory total: 416
dispositioned: 413
missing: ['C7b-9', 'G4-9', 'P1-2']

$ .venv/bin/python <the same script> .              # this head
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

### Review corrections, round 2 (2026-09-08)

Nine blocking findings from three independent lenses, converging on five defects
in what round 1 wrote: two counts that round 1's own repair falsified, a quoted
proof that could not fail, a recommendation reason a linked card contradicts, and
one row carrying a fifth disposition word. Documentation only again. No id
changed document, no routing was redone, the only disposition word that moved is
the not-reproducible row's label, and the four review inputs stay byte-identical.

**1. Round 1's repair of the branch-string count re-introduced the defect, and
took the sibling `/tmp` figure with it.** Round 1 quoted both commands in this
card so the proofs would be reproducible from the card alone; that put both
literals into a tracked file inside both counted sets, which moved both counts.
The superseded sentences, quoted as round 1 wrote them:

- this card: "At this head there are 27, the two extra being the two documents
  themselves"; "The literal string is deliberately kept out of this card so the
  published count stays exactly the two documents that carry it plus the 25
  inherited files"; "still prints 64 lines at this head, as the follow-up read
  it";
- `docs/cleanup-dispositions.md` and the follow-up record: "27 on this branch —
  the two added files being this document and the follow-up correction record",
  and "prints 64, unchanged from the follow-up's reading";
- `ab467228`'s pushed commit body: "it is 27 at this head", which was already 28
  at that commit. A pushed commit is not amended; this subsection is the
  correction of record.

Measured on the committed tree, `git status --porcelain` empty:

```text
$ git grep -l "codex/cleanup" | wc -l                       28   this head
$ git grep -l "codex/cleanup" 1aaae43e | wc -l              28   the round-2 base, where 27 was published
$ git grep -l "codex/cleanup" ab467228 | wc -l              28   the round-1 correction commit
$ git grep -l "codex/cleanup" 7cbf9786 | wc -l              27   round 0, the only tree where 27 held
$ git grep -l "codex/cleanup" 201849fc | wc -l              25   the tree the pass was written against
$ grep -rno '/tmp/' tasks/work/ | wc -l                     72   this head
$ git grep -o '/tmp/' 1aaae43e -- tasks/work/ | wc -l       66   the round-2 base, where 64 was published
$ git grep -o '/tmp/' ab467228 -- tasks/work/ | wc -l       66   the round-1 correction commit
$ git grep -o '/tmp/' fd1f923c -- tasks/work/ | wc -l       64   the commit the follow-up read
$ git grep -o '/tmp/' 201849fc -- tasks/work/ | wc -l       64   the tree the pass was written against
```

The three files carrying the branch string that the 25 at `201849fc` do not
include are named rather than counted, with a command that proves both halves:

```text
$ git grep -l "codex/cleanup" -- audits/review-2026-09-06/followup-correction-record.md \
    docs/cleanup-dispositions.md tasks/work/followup-review-dispositions.md
audits/review-2026-09-06/followup-correction-record.md
docs/cleanup-dispositions.md
tasks/work/followup-review-dispositions.md
$ git grep -l "codex/cleanup" 201849fc -- audits/review-2026-09-06/followup-correction-record.md \
    docs/cleanup-dispositions.md tasks/work/followup-review-dispositions.md
(no output) ; exit=1
```

Both published documents now name the tree each figure belongs to, enumerate
three added files, and drop "unchanged from the follow-up's reading". The
follow-up did read 64 for this scope — its appendix records
`57 (fu-prev), 64 (fu-head)` for the `tasks/work/` count at
`REVIEW_APPENDIX_FOLLOWUP.md:1337`, and `fu-head` is `fd1f923c`, which reproduces
above — while its report headline, "`/tmp` citations in cards and the ledger rose
from 82 to 89" (`REVIEW_REPORT_FOLLOWUP.md:82`), is the wider scope its own
appendix states as "tasks/ + docs/ /tmp citations rose 82 -> 89"
(`REVIEW_APPENDIX_FOLLOWUP.md:176`, row `M7-2`). Both documents now say which
scope they mean, so neither figure is attributed to a reading the review did not
publish.

The file count is stable from here: this card already carries the string, and
this round adds it to no fourth file. The occurrence count is not
self-stabilising in the same way, so it was measured on the final committed bytes
rather than predicted, and both documents say what the increase is — quoted grep
patterns inside a proof, not evidence cited from a host-local path, which is what
`P2-7` and the row carrying it are about.

**2. The `<td>`-against-`<th>` render check could not fail on the defect it was
quoted as catching.** Round 1 wrote, and this round withdraws: "The second
renders each row with `markdown_it` in `gfm-like` mode and counts `<td>` against
`<th>`, which is the property that actually matters — the row that had four cells
against a three-column header lost its third cell in the render, and now keeps
it", with the output block

```text
audits/review-2026-09-06/followup-correction-record.md:103 th=3 td=3
     P-03, P-09, FU-DISP-3, FU-DISP-4, NC5-07
     Retained. Process observations about the correction batch itself: ...
     <a href="../../docs/cleanup-dispositions.md#section-11-workflow-recommendations">The ledger's section 11 table</a>. ...
mismatched rows: 0
```

Both halves are wrong. GFM truncates a row with too many cells and pads one with
too few, so `<td>` equals `<th>` for every row on either side of the fix; and the
quoted line number matches no commit on this branch — the `P-03` row is at `:93`
at `7cbf9786` and at `:105` after round 1. With markdown-it-py 4.0.0 from this
checkout's `.venv`, a three-column header against one row each:

```python
# gfm_probe.py
import re
from markdown_it import MarkdownIt
MD = MarkdownIt("gfm-like").disable("linkify")
HDR = "| A | B | C |\n| --- | --- | --- |\n"
for name, row in {
    "3 cells (exact)": "| x | y | z |",
    "4 cells (the P-03 defect)": "| x | y | z | w |",
    "2 cells (short row)": "| x | y |",
}.items():
    html = MD.render(HDR + row + "\n")
    th = len(re.findall(r"<th[ >]", html))
    td = len(re.findall(r"<td[ >]", html))
    print(f"{name:28s} th={th} td={td}")
```

```text
$ .venv/bin/python gfm_probe.py
3 cells (exact)              th=3 td=3
4 cells (the P-03 defect)    th=3 td=3
2 cells (short row)          th=3 td=3
```

Its replacement asserts the property the defect actually destroyed: every
markdown link written in a table row must still be an `<a href>` after the GFM
render. Links inside a code span are excluded, so a documented pipeline cannot be
mistaken for one.

```python
# linkscan.py — .venv/bin/python linkscan.py <file> ... ; exits 1 on a lost link
import pathlib, re, sys
from markdown_it import MarkdownIt
MD = MarkdownIt("gfm-like").disable("linkify")
CODE = re.compile(r"`[^`]*`")
LINK = re.compile(r"\]\(([^)]+)\)")
HREF = re.compile(r'<a href="([^"]+)"')
bad = 0
for path in sys.argv[1:]:
    header = None
    for n, line in enumerate(pathlib.Path(path).read_text().splitlines(), 1):
        row = line.strip()
        if not row.startswith("|"):
            header = None
            continue
        if header is None:
            header = row
            continue
        if set(row.replace("|", "").replace("\\", "").strip()) <= set("-: "):
            continue
        want = LINK.findall(CODE.sub("`x`", row))
        if not want:
            continue
        dashes = "| " + " | ".join("---" for _ in header.split("|")[1:-1]) + " |"
        got = set(HREF.findall(MD.render(f"{header}\n{dashes}\n{row}\n")))
        lost = [t for t in want if t not in got]
        if lost:
            bad += 1
            print(f"{path}:{n} link dropped by the GFM render: {lost}")
print(f"rows whose links do not survive the render: {bad}")
sys.exit(1 if bad else 0)
```

Planted failure, against the two documents exactly as they stood at `7cbf9786`
written out to a scratch directory, then the same scan at this head:

```text
$ .venv/bin/python linkscan.py <the 7cbf9786 copies of both documents>
.../followup-correction-record.md:93 link dropped by the GFM render: ['../../docs/cleanup-dispositions.md#section-11-workflow-recommendations']
rows whose links do not survive the render: 1 ; exit=1

$ .venv/bin/python linkscan.py docs/cleanup-dispositions.md \
    audits/review-2026-09-06/followup-correction-record.md
rows whose links do not survive the render: 0 ; exit=0
```

The cell-count scan round 1 quoted in full is unaffected and was re-run
unchanged: `:93 header=3 row=4` and exit 1 on the `7cbf9786` documents,
`rows whose cell count differs from their header: 0` and exit 0 here.

**3. Recommendation 2's stated reason was falsified by a card the plan links.**
Round 1 wrote: "Every card the post-merge plan links already satisfies the
Validation half — the smallest carries one card-specific command and the largest
ten — so the practice is in force." Neither half reproduces.
`tasks/work/fresh-deduction-authorization.md`, linked at
`tasks/post-merge-plan.md:97`, has a Validation section that is the two global
gates and nothing else, and no card carries ten. Counted per card at
`origin/main`, where a command is a backticked span or a fenced-block line that
names a runner and is neither global gate:

```python
# valcmds.py — .venv/bin/python valcmds.py <repo-root> origin/main
import pathlib, re, subprocess, sys
ROOT, REF = pathlib.Path(sys.argv[1]), sys.argv[2]
GLOBAL = ("validate_task_docs.py", "scripts/check.sh")
SPAN = re.compile(r"`([^`]+)`")
RUNNER = re.compile(r"\b(uv run|\.venv/bin|bash |pytest|npm |python -m|scripts/)")
def text(rel):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{REF}:{rel}"],
                          capture_output=True, text=True, check=True).stdout
def commands(section):
    fenced = re.findall(r"^```[a-z]*\n(.*?)^```", section, re.S | re.M)
    body = re.sub(r"^```[a-z]*\n.*?^```", "", section, flags=re.S | re.M)
    found = []
    for cand in SPAN.findall(body) + [
        line.strip() for block in fenced for line in block.splitlines() if line.strip()
    ]:
        if any(g in cand for g in GLOBAL) or not RUNNER.search(cand) or cand in found:
            continue
        found.append(cand)
    return found
plan = text("tasks/post-merge-plan.md")
for card in sorted(set(re.findall(r"work/[a-z0-9-]+\.md", plan))):
    section = re.search(r"^## Validation\n(.*?)(?=^## |\Z)", text(f"tasks/{card}"), re.S | re.M)
    print(f"{len(commands(section.group(1)) if section else []):2d}  {card}")
```

```text
$ .venv/bin/python valcmds.py . origin/main
 8  work/accounts-channel-hardening.md
 6  work/evidence-renderer-salience.md
 2  work/followup-review-dispositions.md
 0  work/fresh-deduction-authorization.md
 3  work/fresh-deduction-instrument.md
 4  work/held-out-prefix-freeze.md
 2  work/nonblocking-followup-improvements.md
 7  work/recorded-provenance-gaps.md
 6  work/retire-temporal-evidence-v1.md
```

The counter is calibrated against an independent reading: the lens that filed
this counted eight card-specific commands in `accounts-channel-hardening.md` by
hand, which is what the script prints. The row now states the measured property —
eight of the nine linked cards carry two to eight each — and names the ninth as a
document-only authorization whose Validation is the two global gates because the
limits it authorizes are exercised by the instrument card, not by itself. That is
an exception stated, not a universal claim one card falsifies.

**4. Nine ids carried a fifth disposition word.** The row
`G2-11, G3-2, CMP-06, M3-04, M3-05, M7-3, P1-5, P1-8, P2-4` opened "Not
reproducible at `fd1f923c` ...", which is none of the four words both documents
declare, while the acceptance item requiring exactly one of the four was checked.
The row now opens **Refuted**, in the not-reproducible form, matching its own
section heading; and the ledger's rule paragraph now states that not reproducible
is a form of refuted rather than a fifth word — it says the trigger did not fire
for the lens that looked, never that the behaviour was repaired. No id moved, and
the row's evidence and reasoning are unchanged.

The property is now checked rather than asserted. The scan reads each id row of
this pass's own sections and requires its disposition cell to open with one of
the four words:

```python
# words.py — .venv/bin/python words.py <file>[::<anchor heading>] ... ; exits 1 on a fifth word
import pathlib, re, sys
WORDS = ("Repaired", "Routed", "Retained", "Refuted")
SPLIT = re.compile(r"(?<!\\)\|")
ID = re.compile(r"^[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+")
bad = 0
for arg in sys.argv[1:]:
    path, _, anchor = arg.partition("::")
    started = not anchor
    for n, line in enumerate(pathlib.Path(path).read_text().splitlines(), 1):
        started = started or line.strip() == anchor
        row = line.strip()
        if not started or not row.startswith("|"):
            continue
        cells = [c.strip() for c in SPLIT.split(row)[1:-1]]
        if len(cells) != 3 or not ID.match(cells[0].replace("`", "")):
            continue
        if not cells[1].startswith(WORDS):
            bad += 1
            print(f"{path}:{n} disposition opens {cells[1][:44]!r}")
print(f"rows whose disposition is not one of the four words: {bad}")
sys.exit(1 if bad else 0)
```

```text
$ .venv/bin/python words.py \
    '<the 1aaae43e ledger>::## The 2026-09-06 review: first-pass findings' \
    <the 1aaae43e record>
.../docs/cleanup-dispositions.md:247 disposition opens 'Not reproducible at `fd1f923c` by the dispos'
rows whose disposition is not one of the four words: 1 ; exit=1

$ .venv/bin/python words.py \
    'docs/cleanup-dispositions.md::## The 2026-09-06 review: first-pass findings' \
    audits/review-2026-09-06/followup-correction-record.md     # at this head
rows whose disposition is not one of the four words: 0 ; exit=0
```

The anchor argument scopes the ledger to this pass's own sections: the register
sections above that heading were written under an earlier convention and are not
this card's to relabel. The record needs no anchor because every id row in it
belongs to this pass.

**What did not change.** No id changed document, and the inventory script prints
what it printed in round 1 — 416 / 416, `missing: []`, `dispositioned twice: []`,
`dispositioned but in no register: []`. No routing was redone and no routed row's
card moved. `CARD-02` keeps the word round 1 gave it. The two reports, the two
appendices and `correction-record.md` stay byte-identical:
`git diff --stat 201849fc -- audits/review-2026-09-06/` lists exactly two files
across the whole pass — the new `followup-correction-record.md` and the eight
lines round 0 added to `README.md` so the index reaches it.

**Gates, re-run in full at this head.** `uv run python scripts/check_doc_facts.py`
— exit 0, including "every relative link in 11 front-door and published documents
resolves", which covers the record's new corrections section and its link back to
the pre-merge correction record.
`uv run python scripts/validate_task_docs.py` — exit 0: "390 historical phase
tasks and 390 prompts; 43 work cards". `uv run pytest
tests/scripts/test_check_doc_facts.py tests/scripts/test_verify_ml_evidence.py
-q` — 364 passed in 250.02s. `bash scripts/check.sh` — exit 0 on the committed
tree: ruff and format "All checks passed!", "Contracts: 4 kept, 0 broken",
"Success: no issues found in 469 source files", "7201 passed, 20 skipped, 3
xfailed", 514 frontend tests in 19 files, and the production build. Same counts
as rounds 0 and 1, which is the expected result of a documentation-only round.
Also re-run because the post-merge plan requires them of every card:
`bash scripts/verify_samples.sh` — "All 50 samples verified clean" twice, exit 0;
the four `scripts/build_sample_report.py --check` runs — four "is consistent with
its replays", four exit 0; `pytest tests/orchestrator/ --collect-only` in a fresh
interpreter — 583 collected, exit 0; `uv run python scripts/verify_ml_evidence.py`
— 60 checks, 48 OK, 0 FAIL, 7 ABSENT, 5 INFO, exit 0. `npm run e2e` was not run:
no served DTO, schema or component byte changed. No live provider was called in
this round, by any path.

**Record impact of this round.** `audits/` bytes moved again — the record's
`P-03` row and its new corrections section — so the `docs/artifacts.md` row moved
with them, recomputed with the change staged: `git ls-files audits | wc -l`
prints 203 and `git ls-files -z audits | xargs -0 wc -c | tail -1` prints
14880929, against round 1's 14,879,136. The planted failure for that row was
re-run at this head: reverting the row to `14,879,136 tracked bytes / 203 files`
makes `uv run python scripts/verify_ml_evidence.py` print `[ FAIL ] in-tree
family inventory` with the note "audits/: docs/artifacts.md promises 14,879,136
tracked bytes, the tracked files contain 14,880,929 bytes"; restoring the
recomputed row returns exit 0. No recording, report, metric or adoption verdict
changed; no provider was called; the frozen held-out manifest is untouched, and
this round edits no file in `GENERATOR_SOURCES`, so no restamp was due.
