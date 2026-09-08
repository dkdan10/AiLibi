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

- [x] Review correction: the headline Verification paragraph publishes this
  head's `audits/` figures, not round 1's. The recomputed row is
  `14,883,359 tracked bytes / 203 files`, the planted-failure note reads "the
  tracked files contain 14,883,359 bytes", and the superseded values are kept as
  the dated record of the round that produced each. Proved by `factscan.py`'s
  check 5, which reads the row, the card's two quoted commands and the
  planted-failure note and compares all four against `git ls-files audits`; it
  printed the disagreement (`says 14,880,929, the tree says 14,883,359`) before
  the fix and exits 0 after it.
- [x] Review correction: `docs/cleanup-dispositions.md`'s routed section counts
  its own table. It said "the five ids below" and "The other four are routed by
  mechanism" against six ids of which five are by mechanism; it now says six and
  five and names the five (`G1-02`, `M3-02`, `G4-2`, `GC-3`, `GC-4`). Proved by
  `factscan.py`'s check 5, which parses that sentence and compares its two
  numbers and its id list against the table below it — against the committed
  `34a8b8be` bytes it prints `the sentence says 5 ids, the table holds 6` and
  `the sentence says 4 by mechanism, the table implies 5`, and exits 1.
- [x] Review correction: `NC4-5` is re-dispositioned as **repaired** by
  `29b7bb4a`, the commit the record's `FU-2` row already cited, and the
  `_serialize`-is-dead clause is gone from the retained row. Proved by re-running
  the finding's own trigger — `grep -n "_serialize" scripts/build_sample_report.py`
  prints the production call site at `:451` inside `write_report` beside the
  definition at `:256`, where the finding recorded "referenced from no production
  call site".
- [x] Review correction: the two round-subsection sentences that credited
  `scripts/check_doc_facts.py` with covering this card's own documents and their
  anchors now state what the code enforces — eleven documents in
  `_LINKED_DOCUMENTS + _PUBLISHED_DOCUMENTS` (`:230-255`), fragments stripped
  before resolution (`:4689-4699`), so neither `docs/cleanup-dispositions.md` nor
  the new record is gate-checked and no anchor is. Proved by the two planted
  failures in the closeout subsection: a broken relative link in each of those two
  documents leaves `check_doc_facts.py` at exit 0, while `factscan.py`'s check 2
  prints it and exits 1.
- [x] Review correction: `tasks/review-ledger.md`'s new section no longer claims
  the commits it lists are ones the register "had not yet listed by finding". It
  now partitions the thirteen into five already listed by finding in the
  2026-09-07 checkpoint, four already named there without a finding id, and four
  new to the register. Proved by `factscan.py`'s check 6, which resolves each
  group against `git show 201849fc:tasks/review-ledger.md`.
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
contain 14,883,359 bytes". Restoring the recomputed row returns exit 0. The row
was recomputed with the change staged: `git ls-files audits | wc -l` prints 203
and `git ls-files -z audits | xargs -0 wc -c | tail -1` prints 14883359. (The
figure moved with every round that wrote to the record: 14,876,233 at round 0,
14,879,136 after round 1, 14,880,929 after round 2. Each of those is the dated
record of its own head; this paragraph states the head's.)

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
  routing by mechanism; each row names the item so the check is cheap. The six
  cards are queued rather than dispatched — `tasks/README.md` records that no card
  is active, and `git branch -r --list 'origin/work/*'` shows a pushed branch for
  only `evidence-renderer-salience` and `recorded-provenance-gaps` — so a routed
  id is live until its card is dispatched, implemented and landed.
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
`:89` (a validation output in `tasks/work/temporal-observation-contract.md:173`
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
resolves". Those eleven are `_LINKED_DOCUMENTS + _PUBLISHED_DOCUMENTS`
(`scripts/check_doc_facts.py:230-255`); `audits/review-2026-09-06/README.md` is
among them, so the new record's **path** is resolved from the index, and the rule
strips the fragment before resolving (`relative_targets`, `:4689-4699`), so no
anchor is checked and neither document this card writes has its own links
gate-checked. The anchor link from the ledger's routed section into the record's
`## Routed to a queued card` is checked by this card's own resolver, quoted in
the closeout subsection below, not by a committed gate. *(Superseded wording,
round 1: "exit 0, including 'every relative link in 11 front-door and published
documents resolves', which covers the new anchor link from the ledger's routed
section into the record's `## Routed to a queued card`.")*
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
resolves". The record's new corrections section is not among those eleven, so its
link back to the pre-merge correction record is resolved by this card's own
resolver rather than by the gate; the eleven are enumerated in the round-1
paragraph above. *(Superseded wording, round 2: "which covers the record's new
corrections section and its link back to the pre-merge correction record.")*
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

### Review corrections, closeout round 1 (2026-09-08)

Five blocking findings from two independent lenses, every one of the class the
three earlier rounds were opened for: a sentence that does not reproduce against
the bytes it describes. One id changed disposition — `NC4-5`, retained to
repaired — and no other disposition word, no routing and no spot check moved. The
two reports, the two appendices and `correction-record.md` stay byte-identical.

**1. The headline Verification paragraph still published round 1's `audits/`
total.** It said, in the present tense about this head, that the planted failure
prints "the tracked files contain 14,879,136 bytes" and that
`git ls-files -z audits | xargs -0 wc -c | tail -1` prints 14879136 — while
`docs/artifacts.md`, the round-2 subsection and the PR body all carried
14,880,929. Round 2 corrected its own subsection and left the headline paragraph
alone. This round writes to the record again, so the figure moved again; both
places now carry the head's, recomputed with the change staged:

```text
$ git ls-files audits | wc -l
     203
$ git ls-files -z audits | xargs -0 wc -c | tail -1
 14883359 total
```

Planted failure, re-run at this head: reverting `docs/artifacts.md`'s `audits/`
row to the pre-card `14,850,288 tracked bytes / 202 files` makes
`.venv/bin/python scripts/verify_ml_evidence.py` print

```text
[ FAIL ] in-tree family inventory
          note     : audits/: docs/artifacts.md promises 202 files, the index tracks 203
          note     : audits/: docs/artifacts.md promises 14,850,288 tracked bytes, the tracked files contain 14,883,359 bytes
```

Restoring the recomputed row returns exit 0, and `git status --porcelain` is
empty after the restore. The superseded figures — 14,876,233 at round 0,
14,879,136 after round 1, 14,880,929 after round 2 — stay in the Verification
paragraph as the dated series they are, each named with the round that produced
it. The check that stops this recurring is now mechanical: `factscan.py` below
reads the row, the two commands the card quotes and the planted-failure note out
of the card's headline sections and compares all four with `git ls-files audits`.

**2. The ledger's routed section miscounted its own table.** It read "Of the five
ids below, only `CMP-01` is named by id … The other four are routed by
mechanism" over a table carrying six ids in three rows, five of them by
mechanism. Both figures were off by one, and they contradicted this card's own
verified tally (`retire-temporal-evidence-v1: by-mechanism=3 -> G1-02, M3-02,
G4-2` and `nonblocking-followup-improvements: … GC-3, GC-4`). The sentence now
says six and five and names the five, so it cannot drift from the table again;
`factscan.py`'s check 5 parses the sentence and compares its two numbers and its
id list against the ids it extracts from the rows below it. Against the committed
`34a8b8be` bytes of that document it prints both halves of the defect and exits
1:

```text
  routed sentence: total=5 named=CMP-01 by-mechanism=4 listed=[]
  routed table:    total=6 ids ['CMP-01', 'G1-02', 'G4-2', 'GC-3', 'GC-4', 'M3-02']
FAIL docs/cleanup-dispositions.md: the sentence says 5 ids, the table holds 6
FAIL docs/cleanup-dispositions.md: the sentence says 4 by mechanism, the table implies 5
```

**3. `NC4-5` was retained for a defect the commit in its own table had
repaired.** The retained row `FU-02, FU-05, FU-B-03, FU-D3, NC4-5, NC5-11` gave
as a standing limitation "`_serialize`'s sibling is dead production code the
docstring still describes". `NC4-5` was filed at `fd1f923c` as
"`build_sample_report --write` no longer emits the historical serialization
profile the module docstring still describes, and `_serialize` is now dead
production code", with the trigger "`grep -n "_serialize" scripts/*.py` shows the
function is referenced from no production call site". Re-run here:

```text
$ grep -n "_serialize\|historical_report_payload" scripts/build_sample_report.py
249:def historical_report_payload(report: TournamentEvalReport) -> dict[str, Any]:
256:def _serialize(report: TournamentEvalReport) -> str:
443:    commit the result, so the two must agree: ``_serialize`` projects the legacy
451:    (sample_dir / _REPORT_FILENAME).write_text(_serialize(report), encoding="utf-8")
539:        rebuilt = historical_report_payload(report)
```

`:451` is inside `write_report`, which `main` reaches, so the function is not
dead and the writer emits the documented profile. The repair is `29b7bb4a`, the
commit the same table's `FU-2` row already cites and the fix section 5 of the
follow-up report prescribed ("route `write_report` through `_serialize`");
`git show 29b7bb4a -- scripts/build_sample_report.py` is exactly that change, and
`git merge-base --is-ancestor 29b7bb4a fd1f923c` exits 1, so the finding was
validly filed and later repaired rather than mis-filed. `NC4-5` now sits in the
`FU-2` row as repaired, the quoted clause is gone from the retained row, and the
follow-up record's corrections section dates the move. The other five ids in that
row still reproduce and stay retained.

**4. Two round subsections credited `check_doc_facts.py` with coverage it does
not have.** Round 1 wrote that its link rule "covers the new anchor link from the
ledger's routed section into the record's `## Routed to a queued card`", and
round 2 that it "covers the record's new corrections section and its link back to
the pre-merge correction record". Neither is true of the code. The checked set is
`_LINKED_DOCUMENTS + _PUBLISHED_DOCUMENTS` (`scripts/check_doc_facts.py:230-255`)
— eleven documents, of which `audits/review-2026-09-06/README.md` is the only one
this pass touches — and `relative_targets` (`:4689-4699`) drops the fragment
before resolving, so no anchor is checked at all. Two planted failures on the
committed tree, each restored with `git status --porcelain` empty afterwards:

```text
$ sed -i '' 's|../tasks/work/retire-temporal-evidence-v1.md|../tasks/work/retire-temporal-evidence-vZ.md|' docs/cleanup-dispositions.md
$ .venv/bin/python scripts/check_doc_facts.py ; echo EXIT=$?
... every relative link in 11 front-door and published documents resolves ...
EXIT=0

$ sed -i '' 's|(correction-record.md)|(correctionXrecord.md)|g' audits/review-2026-09-06/followup-correction-record.md
$ .venv/bin/python scripts/check_doc_facts.py ; echo EXIT=$?
EXIT=0
```

The gate is silent with a broken relative link in each of the two documents this
card writes. Both subsections now say what the code enforces, with the round-1
and round-2 wordings quoted in place as superseded, and the property itself is
established by this card's own resolver rather than claimed for a gate:
`factscan.py`'s check 2 resolves every relative target in the four written
documents and, unlike the gate, also resolves the fragment against the target
file's headings under GitHub slug rules. It prints
`relative links checked: 168; anchored among them: 7` and exits 0 here, and on
each planted byte above it printed the broken target and exited 1. That is a
check of this card's output, not a committed gate — the durable-gate half of
recommendation 1 is declined in the ledger, and extending the gate's document set
would edit `scripts/check_doc_facts.py`, which this card does not own.

**5. The ledger's new section claimed the register had not listed commits it had
already listed.** It read "The commits those dispositions name … are the ones
this register had not yet listed by finding", then listed thirteen. Five of them
are listed by finding in the same file, in the "Follow-up correction checkpoint
(2026-09-07)" section that this PR does not touch — `29b7bb4a` (FU-2) and
`ad0f9b5a` (CONC-1) under exactly the same ids:

```text
$ git show 201849fc:tasks/review-ledger.md | sed -n '229,239p'
`14249a79` attests unresolved tournament usage instead of stranding the ledger
(NC4-1; `--attest-unknown-usage SEED`, refused with any cumulative cap, never
counts unknown usage as zero); `29b7bb4a` writes each sample report in the shape
`--check` compares (FU-2); `46e74f6d` shares one recording-filename pattern between
the fingerprint, the public completeness check, the loader, the verifier and the
manifest reader (FU-B-01; every committed fingerprint unchanged); `24a0fe6a` stamps
the agent-factory/substrate identity pair on the first tick row and the terminal
row only (FU-D2; state hashes identical to main on the checked seeds, tick rows
1..N byte-identical to main's, new recordings about 15% smaller than at
`fd1f923c`); `ad0f9b5a` binds the single-game cost read-back to the recorded game
identity (CONC-1). `241a5ca9` commit-qualifies the correction record's gate figures
```

The restrictive clause is gone. The section now partitions the thirteen into the
five already listed by finding, four more the register already names without a
finding id (`241a5ca9`, `e12b6180`, the merge `8161689a` and #436's `081aee15`),
and the four that enter it here (`cb3438ef`, `b79fc1b7`, `700c0671`,
`8dd0576c`). `factscan.py`'s check 6 parses that sentence and resolves every
group against `git show 201849fc:tasks/review-ledger.md`: a commit claimed as
already listed must appear there with its id, one claimed as already named must
appear there, and one claimed as new must not appear there at all. It prints the
three groups and confirms they partition the full index of thirteen.

**The systematic re-derivation.** Three rounds of this card were opened for prose
that does not reproduce, so this round recomputed every mechanical fact the four
written documents publish rather than re-reading them. One script does it, and it
is the proof quoted for findings 1, 2, 4 and 5 above: table shapes, relative
links and anchors, commit shas, ids per disposition table, and the prose numbers
that describe any of those. The two literals this pass itself counts — the
cleanup branch name and the host-local path prefix — are assembled at run time so
that quoting the script inside a counted file cannot move the numbers it
measures.

```python
#!/usr/bin/env python3
"""factscan.py — recompute every mechanical fact this pass publishes.

Run as: .venv/bin/python factscan.py <repo-root>   ; exits 1 on any disagreement.

  1. table shape   every GFM row's cell count equals its header's, splitting on
                   unescaped '|' (a '|' inside a code span must be written '\\|')
  2. links         every relative markdown target in the four written documents
                   resolves, and every '#fragment' names a heading that exists
                   in the target file (GitHub slug rules)
  3. commit shas   every backticked 8-hex token resolves to a commit, except an
                   all-digit one that does not — that is a byte count, and it is
                   reported rather than failed (an all-digit token that DOES
                   resolve, like `26386914`, is still checked as a commit)
  4. id inventory  ids per disposition table, per document and per section
  5. prose numbers the routed-section sentence, the artifacts row, the counts
                   the card publishes as facts about this head

The two literals this pass itself counts — the cleanup branch name and the
host-local path prefix — are assembled at run time so that quoting this script
inside a counted file cannot move the numbers it measures.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
DOCS = (
    "docs/cleanup-dispositions.md",
    "audits/review-2026-09-06/followup-correction-record.md",
    "tasks/review-ledger.md",
    "tasks/work/followup-review-dispositions.md",
)
SPLIT = re.compile(r"(?<!\\)\|")
ID = re.compile(r"^[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+$")
failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print("FAIL", msg)


def cells(line: str) -> list[str]:
    parts = SPLIT.split(line.strip())
    if parts[0] == "" and parts[-1] == "":
        parts = parts[1:-1]
    return [p.strip() for p in parts]


def is_divider(row: str) -> bool:
    return set(row.replace("|", "").replace("\\", "").strip()) <= set("-: ")


def rows(text: str):
    """(lineno, header cells, row cells) for every body row of every table."""
    header = None
    for n, line in enumerate(text.splitlines(), 1):
        row = line.strip()
        if not row.startswith("|"):
            header = None
            continue
        if header is None:
            header = cells(row)
            continue
        if is_divider(row):
            continue
        yield n, header, cells(row)


print("== 1. table shape ==")
for doc in DOCS:
    bad = [n for n, h, r in rows((ROOT / doc).read_text()) if len(r) != len(h)]
    print(f"  {doc}: rows whose cell count differs from their header: {len(bad)}")
    for n in bad:
        fail(f"{doc}:{n} cell count differs from header")


def slug(heading: str) -> str:
    text = re.sub(r"`|\*|_", "", heading.lstrip("#").strip())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.strip().lower().replace(" ", "-")


def headings(path: pathlib.Path) -> set[str]:
    return {
        slug(line)
        for line in path.read_text().splitlines()
        if re.match(r"^#{1,6} ", line)
    }


LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CODE = re.compile(r"```.*?```|`[^`]*`", re.S)
print("== 2. links ==")
checked = anchored = 0
for doc in DOCS:
    body = CODE.sub(" ", (ROOT / doc).read_text())
    base = (ROOT / doc).parent
    for target in LINK.findall(body):
        if target.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
            continue
        checked += 1
        path_part, _, frag = target.partition("#")
        dest = (base / path_part).resolve()
        if not dest.exists():
            fail(f"{doc}: relative link {target!r} does not resolve")
            continue
        if frag:
            anchored += 1
            if slug("# " + frag) not in headings(dest):
                fail(f"{doc}: anchor {target!r} names no heading in {path_part}")
print(f"  relative links checked: {checked}; anchored among them: {anchored}")

print("== 3. commit shas ==")
SHA = re.compile(r"`([0-9a-f]{8})`")
seen: dict[str, set[str]] = {}
for doc in DOCS:
    for sha in SHA.findall((ROOT / doc).read_text()):
        seen.setdefault(sha, set()).add(doc)
numeric: list[str] = []
for sha, where in sorted(seen.items()):
    found = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True,
    )
    if found.returncode == 0:
        continue
    if sha.isdigit():  # an eight-digit byte count quoted in prose, not a sha
        numeric.append(sha)
        continue
    fail(f"{sha} (in {', '.join(sorted(where))}) is not a commit in this repo")
print(f"  8-hex tokens seen: {len(seen)}; resolved as commits: "
      f"{len(seen) - len(numeric)}; all-digit non-commits (byte counts): {numeric}")

print("== 4. id inventory ==")


def table_ids(doc: str, want) -> dict[str, list[int]]:
    section, header = "", None
    out: dict[str, list[int]] = {}
    for n, line in enumerate((ROOT / doc).read_text().splitlines(), 1):
        if line.startswith("#"):
            section = line.strip()
        row = line.strip()
        if not row.startswith("|"):
            header = None
            continue
        if header is None:
            header = cells(row)
            continue
        if is_divider(row) or not want(section):
            continue
        for token in re.split(r"[,\s]+", cells(row)[0].replace("**", "")):
            if ID.match(token.strip("`")):
                out.setdefault(token.strip("`"), []).append(n)
    return out


LEDGER = "docs/cleanup-dispositions.md"
RECORD = "audits/review-2026-09-06/followup-correction-record.md"
for section in (
    "### First-pass findings repaired",
    "### First-pass findings routed to a card",
    "### First-pass findings refuted or not reproducible",
    "### First-pass findings retained",
):
    print(f"  {LEDGER} {section!r}: {len(table_ids(LEDGER, lambda s, w=section: s == w))} ids")
routed = table_ids(LEDGER, lambda s: s == "### First-pass findings routed to a card")
print(f"    routed ids: {sorted(routed)}")
for section in (
    "## Repaired",
    "## Routed to a queued card",
    "## Retained",
    "## Findings the review's own adversarial pass did not sustain",
):
    print(f"  {RECORD} {section!r}: {len(table_ids(RECORD, lambda s, w=section: s == w))} ids")

pass_ids = table_ids(LEDGER, lambda s: s.startswith("### First-pass findings"))
record_ids = table_ids(RECORD, lambda s: s.startswith("## "))
print(f"  {LEDGER}, this pass's sections: {len(pass_ids)} ids")
print(f"  {RECORD}, all sections: {len(record_ids)} ids")
print(f"  union: {len(set(pass_ids) | set(record_ids))} ids")
for name, table in ((LEDGER, pass_ids), (RECORD, record_ids)):
    for i, lines in sorted(table.items()):
        if len(lines) > 1:
            fail(f"{name}: {i} is dispositioned on lines {lines}")
both = set(pass_ids) & set(record_ids)
if both:
    fail(f"ids dispositioned in both documents: {sorted(both)}")
for doc, count, label in (
    (LEDGER, len(pass_ids), "That is (\\d+) ids, each appearing exactly once below"),
    (RECORD, len(record_ids), "All (\\d+) of them are\\s+dispositioned below"),
):
    said = re.search(label, (ROOT / doc).read_text())
    if not said:
        fail(f"{doc}: the id-total sentence {label!r} no longer parses")
    elif int(said.group(1)) != count:
        fail(f"{doc}: says {said.group(1)} ids, its tables hold {count}")
    else:
        print(f"  {doc}: id-total sentence says {said.group(1)}, tables hold {count}")

print("== 5. prose numbers ==")
WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
}
ledger_text = (ROOT / LEDGER).read_text()
sentence = re.search(
    r"Of the (\w+) ids below, only\s+`([A-Z0-9-]+)` is named by id.*?"
    r"The other\s+(\w+)\s*(?:—\s*(.*?)\s*—\s*)?are routed by mechanism",
    ledger_text,
    re.S,
)
if not sentence:
    fail(f"{LEDGER}: the routed-section sentence no longer parses")
else:
    total, named, rest = WORDS[sentence.group(1)], sentence.group(2), WORDS[sentence.group(3)]
    listed = {t.strip("`") for t in re.findall(r"`([A-Z0-9-]+)`", sentence.group(4) or "")}
    print(f"  routed sentence: total={total} named={named} by-mechanism={rest} listed={sorted(listed)}")
    print(f"  routed table:    total={len(routed)} ids {sorted(routed)}")
    if total != len(routed):
        fail(f"{LEDGER}: the sentence says {total} ids, the table holds {len(routed)}")
    if rest != len(routed) - 1:
        fail(f"{LEDGER}: the sentence says {rest} by mechanism, the table implies {len(routed) - 1}")
    if named not in routed:
        fail(f"{LEDGER}: the sentence names {named}, which is not in the table")
    if listed and listed != set(routed) - {named}:
        fail(f"{LEDGER}: the sentence lists {sorted(listed)}, the table implies "
             f"{sorted(set(routed) - {named})}")

tracked = subprocess.run(
    ["git", "-C", str(ROOT), "ls-files", "audits"],
    capture_output=True, text=True, check=True,
).stdout.split()
total_bytes = sum((ROOT / f).stat().st_size for f in tracked)
row = re.search(
    r"\| `audits/`[^|]*\|[^|]*\|[^|]*\| ([\d,]+) tracked bytes / (\d+) files \|",
    (ROOT / "docs/artifacts.md").read_text(),
)
if not row:
    fail("docs/artifacts.md: the audits inventory row no longer parses")
else:
    said = (int(row.group(1).replace(",", "")), int(row.group(2)))
    print(f"  artifacts row: {said[0]} bytes / {said[1]} files")
    print(f"  git ls-files:  {total_bytes} bytes / {len(tracked)} files")
    if said != (total_bytes, len(tracked)):
        fail("docs/artifacts.md: the audits row disagrees with the tracked bytes")

# Only the card's headline sections state facts about this head; the dated
# "Review corrections, round N" subsections quote the head each round produced.
card = re.split(
    r"^### Review corrections, ",
    (ROOT / "tasks/work/followup-review-dispositions.md").read_text(),
    flags=re.M,
)[0]
for pattern, actual, label in (
    (r"`git ls-files -z audits \| xargs -0 wc -c \| tail -1` prints\s+(\d+)",
     str(total_bytes), "audits byte total"),
    (r"`git ls-files audits \| wc -l` prints\s+(\d+)",
     str(len(tracked)), "audits file count"),
    (r"the tracked files\s+contain\s+([\d,]+) bytes", f"{total_bytes:,}",
     "planted-failure byte note"),
):
    found = re.findall(pattern, card)
    print(f"  card, {label}: {found} (tree says {actual})")
    if not found:
        fail(f"card: the headline sections no longer state the {label}")
    for value in found:
        if value != actual:
            fail(f"card: {label} says {value}, the tree says {actual}")

branch = subprocess.run(
    ["git", "-C", str(ROOT), "grep", "-l", "codex" + "/" + "cleanup"],
    capture_output=True, text=True,
).stdout.split()
tmp = subprocess.run(
    ["git", "-C", str(ROOT), "grep", "-o", "/" + "tmp" + "/", "--", "tasks/work/"],
    capture_output=True, text=True,
).stdout.splitlines()
print(f"  files carrying the branch string: {len(branch)}")
print(f"  host-local-path citations under tasks/work/: {len(tmp)}")
for doc in (LEDGER, RECORD):
    for said_head in re.findall(r"and (\d+) at this branch's head", (ROOT / doc).read_text()):
        if said_head not in {str(len(branch)), str(len(tmp))}:
            fail(f"{doc}: publishes {said_head} at this head, which is neither "
                 f"{len(branch)} nor {len(tmp)}")

print("== 6. the register's own prior state ==")
BASE = "201849fc"
base = subprocess.run(
    ["git", "-C", str(ROOT), "show", f"{BASE}:tasks/review-ledger.md"],
    capture_output=True, text=True, check=True,
).stdout
section = (ROOT / "tasks/review-ledger.md").read_text().split(
    "## Review disposition pass (2026-09-08)"
)[-1]
claim = re.search(
    r"Five are already listed by finding.*?—\s*(?P<listed>.*?)\s*—\s*and are\s*\n?"
    r".*?without a finding id:\s*(?P<named>.*?)\.\s*The remaining four\s*—\s*"
    r"(?P<new>.*?)\s*—\s*enter this register here\. In full:\s*(?P<full>.*?)"
    r"This is\s*\na finding-to-commit index",
    section,
    re.S,
)
if not claim:
    fail("tasks/review-ledger.md: the three-group sentence no longer parses")
else:
    def shas(text):
        return [s for s in re.findall(r"`([0-9a-f]{8})`", text)]

    listed = shas(claim.group("listed"))
    named = shas(claim.group("named"))
    fresh = shas(claim.group("new"))
    full = list(dict.fromkeys(shas(claim.group("full"))))
    ids = dict(re.findall(r"`([0-9a-f]{8})`\s*\(([A-Z][A-Za-z0-9-]*)\)", claim.group("listed")))
    print(f"  listed by finding already: {listed}")
    print(f"  named without a finding id: {named}")
    print(f"  new to the register: {fresh}")
    print(f"  the full index names {len(full)} commits")
    if sorted(listed + named + fresh) != sorted(full):
        fail("tasks/review-ledger.md: the three groups do not partition the full index")
    for sha in listed:
        if sha not in base:
            fail(f"{sha} is claimed as already listed, but is absent from {BASE}'s register")
        elif ids.get(sha) and ids[sha] not in base:
            fail(f"{sha} is claimed as listed by finding, but {ids[sha]} is absent from {BASE}")
    for sha in named:
        if sha not in base:
            fail(f"{sha} is claimed as already named, but is absent from {BASE}'s register")
    for sha in fresh:
        if sha in base:
            fail(f"{sha} is claimed as new to the register, but {BASE}'s register names it")
    print(f"  checked against `git show {BASE}:tasks/review-ledger.md`")

print()
print(f"disagreements: {len(failures)}")
sys.exit(1 if failures else 0)
```

```text
$ .venv/bin/python factscan.py .
== 1. table shape ==
  docs/cleanup-dispositions.md: rows whose cell count differs from their header: 0
  audits/review-2026-09-06/followup-correction-record.md: rows whose cell count differs from their header: 0
  tasks/review-ledger.md: rows whose cell count differs from their header: 0
  tasks/work/followup-review-dispositions.md: rows whose cell count differs from their header: 0
== 2. links ==
  relative links checked: 168; anchored among them: 7
== 3. commit shas ==
  8-hex tokens seen: 58; resolved as commits: 56; all-digit non-commits (byte counts): ['14880929', '14883359']
== 4. id inventory ==
  docs/cleanup-dispositions.md '### First-pass findings repaired': 37 ids
  docs/cleanup-dispositions.md '### First-pass findings routed to a card': 6 ids
  docs/cleanup-dispositions.md '### First-pass findings refuted or not reproducible': 14 ids
  docs/cleanup-dispositions.md '### First-pass findings retained': 178 ids
    routed ids: ['CMP-01', 'G1-02', 'G4-2', 'GC-3', 'GC-4', 'M3-02']
  audits/review-2026-09-06/followup-correction-record.md '## Repaired': 15 ids
  audits/review-2026-09-06/followup-correction-record.md '## Routed to a queued card': 42 ids
  audits/review-2026-09-06/followup-correction-record.md '## Retained': 89 ids
  audits/review-2026-09-06/followup-correction-record.md "## Findings the review's own adversarial pass did not sustain": 35 ids
  docs/cleanup-dispositions.md, this pass's sections: 235 ids
  audits/review-2026-09-06/followup-correction-record.md, all sections: 181 ids
  union: 416 ids
  docs/cleanup-dispositions.md: id-total sentence says 235, tables hold 235
  audits/review-2026-09-06/followup-correction-record.md: id-total sentence says 181, tables hold 181
== 5. prose numbers ==
  routed sentence: total=6 named=CMP-01 by-mechanism=5 listed=['G1-02', 'G4-2', 'GC-3', 'GC-4', 'M3-02']
  routed table:    total=6 ids ['CMP-01', 'G1-02', 'G4-2', 'GC-3', 'GC-4', 'M3-02']
  artifacts row: 14883359 bytes / 203 files
  git ls-files:  14883359 bytes / 203 files
  card, audits byte total: ['14883359'] (tree says 14883359)
  card, audits file count: ['203'] (tree says 203)
  card, planted-failure byte note: ['14,883,359'] (tree says 14,883,359)
  files carrying the branch string: 28
  host-local-path citations under tasks/work/: 72
== 6. the register's own prior state ==
  listed by finding already: ['14249a79', '29b7bb4a', '46e74f6d', '24a0fe6a', 'ad0f9b5a']
  named without a finding id: ['241a5ca9', 'e12b6180', '8161689a', '081aee15']
  new to the register: ['cb3438ef', 'b79fc1b7', '700c0671', '8dd0576c']
  the full index names 13 commits
  checked against `git show 201849fc:tasks/review-ledger.md`

disagreements: 0
```

Perturbed proof that the card-figure half is not vacuous: with the head's
`14883359` / `14,883,359` replaced by round 2's `14880929` / `14,880,929` in the
card's headline sections and nothing else changed, the same command prints

```text
FAIL card: audits byte total says 14880929, the tree says 14883359
FAIL card: planted-failure byte note says 14,880,929, the tree says 14,883,359
disagreements: 2
```

and exits 1; restoring the card returns exit 0. The scan reads only the card's
headline sections — it splits at the first `### Review corrections, ` heading —
because the dated round subsections quote the head each round produced and must
not be dragged forward.

**Nonblocking findings, all of them answered.** Eight were cheap and correct to
fix and are fixed here.

- The record's Repaired preamble read "The four merge blockers of section 5 and
  the correction-record accuracy item", which counts section 5's fourth blocker
  twice: `REVIEW_REPORT_FOLLOWUP.md:195-203` lists four, and item 4 *is*
  "Correction-record accuracy (P-02, FU-3)". It now says so.
- The ledger's multi-filing note named `CARD-01` and `CARD-02` but not `CARD-04`,
  which the appendix also files twice (`REVIEW_APPENDIX_findings.md:91`,
  unsupported-claim, and `:173`, process). `CARD-04` is now named, with both
  filings and the single retained row that carries them.
- `CARD-02`'s second filing was cited at
  `tasks/work/temporal-observation-contract.md:172` in the ledger and in round
  1's subsection here; the quoted line
  `# 390 historical tasks/prompts and 23 work cards valid.` is at `:173` at
  `201849fc`, at `fd1f923c` and at this head, which is also where the review's own
  appendix cites it. Both citations now say `:173`. No disposition depended on it.
- Recommendation 1 was quoted with only half its scope. As filed
  (`REVIEW_REPORT.md:198`) it asks for card count and state in `tasks/README.md`
  **and the ledger** to equal `tasks/work/*.md`; the adopted item covers
  `tasks/README.md` only. The row now carries the full quote and decides the
  ledger half explicitly — declined, because `tasks/review-ledger.md` states no
  live card count to derive: its one card-count sentence is the dated `9b333a76`
  handoff figure at `:153`.
- Recommendation 2's reason measured only the Validation half of the rule it
  answers. The Results half cannot be measured across the same nine cards — eight
  are `Status: ready` at `origin/main` with an unwritten Results — so the row now
  says that, and names the one `done` card, `held-out-prefix-freeze.md`, whose
  Results carries sixteen card-specific commands by the same counter:
  `.venv/bin/python valcmds.py . origin/main Results` prints `16` for it and `0`
  for the other eight.
- Both documents said every added host-local-path citation was "this same
  command". Of the eight added matches, all in this card, four are that
  `grep -rno` pattern and four are the `git grep -o` form used to scope the same
  count to an earlier commit. Both rows now say that. The substantive claim — a
  quoted pattern rather than evidence cited from a host-local path — holds for
  all eight.
- The record and this card's Limitations described the six routed cards as "in
  flight on their own branches". `tasks/README.md:17-21` says no card is active,
  and `git branch -r --list 'origin/work/*'` shows a pushed branch for two of the
  six. Both now say queued, with that evidence.
- Section 11's row 7 inferred a uniform trailer convention from mixed history.
  Measured over the 21 commits in `8161689a..origin/main`: 8 carry `Card:`, 7
  carry the plural `Cards:`, 6 carry neither, 19 carry the co-author line and 2
  do not. The row now states the convention as adopted practice and publishes the
  mix rather than claiming the landed commits already evidence it.

Two are left standing, deliberately, and both are declared rather than silenced.

- **Two writers are queued for `tasks/review-ledger.md`.**
  `tasks/post-merge-plan.md:85` assigns that file to the Maintenance worker while
  this card (Documentation worker 1) is given only the two disposition documents,
  and the nonblocking card's `P-06 / P-10` item adds per-commit rows to the same
  file. This card's Expected scope at `201849fc` explicitly grants it "where a
  disposition names a commit", its new section says the per-commit register stays
  with the nonblocking card, and the PR body raises the collision as a question.
  Reconciling the plan's ownership table with a committed card contract is an
  owner decision, not something this card may take.
- **`audits/review-2026-09-06/README.md` is written but not named in Expected
  scope.** The eight added lines are what makes the new record reachable from the
  review index, which an acceptance item requires; the edit is disclosed in
  Results and reproduced by
  `git diff --stat 201849fc -- audits/review-2026-09-06/`, which lists exactly two
  files. Editing the Expected scope now would rewrite a committed contract after
  the fact rather than record the deviation, so it stays recorded here as a
  declared deviation.

**Codex review.** One Codex review exists on this PR (state COMMENTED, on round
0's `7cbf9786`), with seven inline comments; re-polling
`gh api repos/dkdan10/AiLibi/pulls/439/comments` at this head returns the same
seven and no new activity. All seven are now addressed at this head. Five were
fixed in earlier rounds, each with a check that fails on the bytes Codex flagged:
3954475665 (`CARD-02`'s second filing kept unresolved) — the id now appears once,
in the retained drifted-Results row; 3954475670 (recompute the branch-reference
count) — both documents now name the tree per figure and enumerate three added
files; 3954475676 (assign an allowed disposition to the unreproduced findings) —
the row opens **Refuted** in the not-reproducible form, proved by the
disposition-word scan; 3954475681 (account for the card without a specific
validation command) — `fresh-deduction-authorization.md` is named as a
document-only exception, proved by `valcmds.py`; 3954475692 (add the prose-only
`G4-9` disposition) — the refuted row for `P1-2`, `C7b-9` and `G4-9`, proved by
the perturbed inventory run. The remaining two are fixed in this round:
3954475672 (describe the routed cards as queued rather than in flight) is
adopted in full; 3954475687 (do not infer a uniform trailer convention from mixed
history) is adopted in substance while its example is refuted on the bytes —
`b6a4c3d6` does carry `Card: tasks/work/held-out-prefix-freeze.md`, so that half
of the comment is wrong, but `3eb49dfc` carries no card trailer and seven
commits use `Cards:`, so the generalisation it objected to was loose and the row
now publishes the measured mix.

**Gates, re-run in full at this head.**
`uv run python scripts/check_doc_facts.py` — exit 0.
`uv run python scripts/validate_task_docs.py` — exit 0: "390 historical phase
tasks and 390 prompts; 43 work cards".
`uv run pytest tests/scripts/test_check_doc_facts.py
tests/scripts/test_verify_ml_evidence.py -q` — 364 passed in 241.01s.
`bash scripts/check.sh` — exit 0 on the committed tree: ruff and format
"All checks passed!", "Contracts: 4 kept, 0 broken", "Success: no issues found in
469 source files", "7201 passed, 20 skipped, 3 xfailed", 514 frontend tests in 19
files, and the production build. Same counts as rounds 0, 1 and 2, which is the
expected result of a documentation-only round. An earlier run of the same gate,
sharing the machine with two other gate runs, hit one flake —
`tests/orchestrator/test_run_limits.py::test_wall_deadline_cancels_meeting_and_retains_success`,
whose assertion depends on a 0.25-second wall deadline being reached inside a
loaded xdist worker. It passes in isolation and passed in the unloaded run above;
nothing in this round touches that path, and the flake is recorded here rather
than dropped. Also re-run because the post-merge
plan requires them of every card: `bash scripts/verify_samples.sh` — "All 50
samples verified clean" twice, exit 0; the four
`scripts/build_sample_report.py --check` runs — four "is consistent with its
replays", four exit 0; `pytest tests/orchestrator/ --collect-only` in a fresh
interpreter — 583 collected, exit 0; `uv run python scripts/verify_ml_evidence.py`
— 60 checks, 48 OK, 0 FAIL, 7 ABSENT, 5 INFO, exit 0. The scan above exits 0 on
this head, and its quoted output is the output it prints on the bytes that quote
it. `npm run e2e` was not run: no served DTO, schema or component byte changed.
No live provider was called in this round, by any path.

**Record impact of this round.** `audits/` bytes moved once more — `NC4-5`'s row
move, four corrected wordings and the record's new dated correction entry — so
the `docs/artifacts.md` row moved with them, to
`14,883,359 tracked bytes / 203 files`, recomputed with the change staged and
proved by the planted failure quoted under finding 1. No recording, report,
metric, fitted weight or adoption verdict changed; no candidate was adopted; no
provider was called by any path. The frozen held-out manifest is untouched: this
round edits no file in `experiments/held_out_prefixes.py`'s `GENERATOR_SOURCES`,
so no restamp was due, `tests/experiments/test_held_out_prefixes.py` passes
inside the full gate, and no band prefix was printed or opened.
