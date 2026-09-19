# Close the accuracy-gated deduction evaluation and shelve its candidate

**Status:** done

## Outcome

The fresh-model deduction evaluation is closed in its own documents, dated
2026-09-19, by the owner's ruling. Its preregistered primary outcome stays the
record of what was measured and stops being the project's gate. No live run can
start from this tree: the gate refuses by construction and the fifth band's
freeze record is marked development. That record becomes a verified ARCHIVE,
checked against the bytes it was frozen with rather than against a moving tree,
so the substrate wave can edit `orchestrator/game.py` without re-stamping a
retired band. One unexecuted card is retired and one blocked card re-assessed.
No agent behaviour, prompt byte, recording byte or published figure moves.

## Evidence

The direction is
[the memo of 2026-09-19](../direction-2026-09-19-process-over-outcome.md),
whose decisions D1 to D8 the owner accepted as a set that date, rulings in its
section 12. Three are this card: D1 (demote role-correctness, write the
demotion down and date it), D2 (retire the proof-free held-out band as the
arena, keep 2100-2999 unseen) and D8 (shelve `combined_accounts`, harvest its
SKIP register). The owner's goal is the test for every choice below: reasons
grounded in the data the agent holds, a wrong call on believable data preferred
to a right call on invalid data, and a state that can be shown to people.

**What stops being the gate.** `PRIMARY_OUTCOME`
(`experiments/fresh_deduction_instrument.py:762`) is
`supported_correct_ejection`; its rubric (`:764-772`) scores 1 only when the
ejected player's role is IMPOSTOR and every ballot naming them cited something
present and relevant. A wrong ejection on good evidence scores 0, the same as a
meeting where nobody reasoned. `DECISION_RULE` (`:780`) and
`WRONGFUL_EJECTION_TRADEOFF` (`:796`) are counts of who was ejected. No
constant is deleted here: they stay the frozen record of what the fifth run
measured. That run (`audits/deduction-candidate/run-2026-09-16/RESULTS.md`) is
the only complete one of five: `b = 2`, `c = 0`, exact McNemar p 0.5 against a
bar of 0.05, net paired difference 2 against 10, and +7 wrongful ejections
against a permitted 2. All three clauses failed, so the candidate neither
advanced nor was rejected, and the three calibrations graded nothing
(`audits/deduction-candidate/README.md:52-98`). Four bands are already
development data because a stopped run rendered a prefix of theirs: 3000-3999
since 2026-09-10, 5000-5999 and 6000-6999 since 2026-09-13, 7000-7999 since
2026-09-15. The fifth run rendered ALL FIFTY of band 8000-8999 on 2026-09-16,
and that conversion is the one still unrecorded.

**The live gate as it stands**, all in
`experiments/fresh_deduction_instrument.py`. A call needs a `LiveRunInvocation`
(`:1258`) plus `assert_live_run_is_authorized` (`:1323`), which
`assert_ready_for_a_live_run` calls before any client exists (`:2097-2135`);
`fake` returns at `:1353` and is the offline mechanics path. `verify_frozen_set`
(`:3470`) already refuses a set marked anything but `held_out` (`:3495`), so the
conversion below is itself a refusal. The document-level idiom exists here too:
`RESUMPTION_CLAUSE` (`:1607`) is a string the execution manifest must carry,
read at `:1958`, and each calibration mode carries its own, read at `:2077`.

**The restamp treadmill, measured.** `GENERATOR_SOURCES`
(`experiments/held_out_prefixes.py:155-178`) holds 22 files,
`orchestrator/game.py` among them. The regeneration test
(`tests/experiments/test_held_out_prefixes.py:796-816`) rebuilds whatever sits
at `MANIFEST_PATH` (`experiments/held_out_prefixes.py:146`) and asserts
`rebuilt == manifest`, `source_sha256` included. All 22 match the tree at
`989c7c17`, by a hash comparison that generates no prefix:

```sh
python3 -c 'import hashlib,json
d=json.load(open("audits/deduction-candidate/held-out/manifest.json"))
d=d["source_sha256"]
print(len(d),[p for p,h in d.items()
              if hashlib.sha256(open(p,"rb").read()).hexdigest()!=h])'
# 22 []
```

Keeping them matched has a price, on the record. The citation guard touched
`orchestrator/game.py`; `68dfe979` re-stamped the band for it; that restamp
moved `experiments/held_out_prefixes.py`'s own digest, which the same record
lists as a source, and `72998c7b` corrected the note and digest again, all
preserved in `dependency_restamps.entries[0]`. All three substrate cards move
`PROMPT_VERSION_SETS` (`orchestrator/game.py:397`), so without this card the
wave owes three restamps of a band nobody will draw.

**The open-obligation test has two branches and needs a third.**
`test_a_binding_to_a_converted_record_stays_an_open_obligation`
(`tests/experiments/test_fresh_deduction_instrument.py:4816-4865`) reads the
record whose band the Inputs row binds (`:4724-4758`;
`audits/deduction-candidate/execution-manifest.md:1648`). Today that is the
live freeze and the test returns at
`tests/experiments/test_fresh_deduction_instrument.py:4838`. Marked development
in place it would
fall through to `assert converted["superseded_by"] == MANIFEST_PATH` and then
to `assert live["status"] == "held_out"` on the same file, which no honest edit
can satisfy: no band replaced this one, because none was frozen.

**The two cards to dispose of.**
[The sixth freeze](held-out-prefix-freeze-6.md) is `ready`, preregisters
2100-2999 and has executed nothing.
[The v1 retirement](retire-temporal-evidence-v1.md) is `ready` and blocked on
an adopting record for evidence v2 that this evaluation was the only planned
source of. `scripts/validate_task_docs.py:160-164` allows `done` only with
every box checked and a `## Results` section; `:188-254` re-derives the
inventory sentence at `tasks/README.md:43`.

## Acceptance

- [x] Review correction: the archive cannot reach the live client factory.
  `verify_archived_set` returns an `ArchivedSet` — a sibling of `FrozenSet`
  under a shared `VerifiedPrefixRecord`, not a subclass — and
  `build_authorized_client` refuses anything but its three proof types before
  it reads the credential. Proved both ways by
  `tests/experiments/test_fresh_deduction_instrument.py::TestAuthorizedClient::test_the_archive_is_not_evidence_a_live_client_may_be_built_from`
  and, statically, by `.venv/bin/mypy` on a probe holding
  `build_authorized_client(verify_archived_set())`.
- [x] Review correction (Codex 3, the same defect read from the documentation
  lens): the two docstrings that asserted the old invariant now state the one
  the code enforces — `build_authorized_client`'s "only producer" paragraph
  (`experiments/fresh_deduction_instrument.py`) and
  `TestAuthorizedClient::test_a_client_cannot_be_built_before_the_frozen_set_is_verified`'s
  — and the dated Results subsection names `verify_frozen_set` as the reader
  whose return value is the client-ordering proof.
- [x] Review correction (Codex 1): the live reader refuses any record carrying
  a `converted` block, whatever its `status`, with a message of its own naming
  that block and its date. Proved by
  `TestFrozenSet::test_a_record_that_says_it_was_already_spent_is_refused_as_held_out`,
  whose plant is the committed archive with `status` flipped back to
  `held_out`, and by `TestFrozenSet::test_a_set_marked_development_is_refused`,
  which keeps the status refusal on a record carrying no block.
- [x] Review correction (Codex 2): `write_manifest` writes over exactly one
  shape — a JSON object marked `held_out` with no `converted` block — and every
  other shape raises `HeldOutPrefixError` naming the file and what was found
  there, the bytes left untouched. Proved by
  `tests/experiments/test_held_out_prefixes.py::test_write_manifest_refuses_every_shape_that_is_not_a_freeze`
  over development-data-with-no-block, a JSON list and a file that is not JSON.
- [x] A dated closing record, 2026-09-19, attributed to the owner's acceptance
  of D1, D2 and D8, is written into `audits/deduction-candidate/README.md`,
  `preregistration.md`, `checkpoint.md` and a final dated section of
  `execution-manifest.md`. It states that the preregistered primary outcome,
  decision rule and tradeoff bound stay the record of what was measured and are
  no longer the project's gate; that five runs and three calibrations are
  context, not adoption evidence; and that no result in them is restated,
  re-scored or withdrawn. The section is APPENDED after `## Verification of
  this manifest`, so existing line citations stay valid, and carries no row
  beginning `| Seed band |`, which `manifest_bound_band`
  (`experiments/fresh_deduction_instrument.py:1194-1211`) requires to be unique.
- [x] A `CLOSURE_CLAUSE` constant, shaped like `RESUMPTION_CLAUSE`
  (`experiments/fresh_deduction_instrument.py:1607`), is the sentence that
  section carries, and both live gates refuse while the committed manifest
  holds it: `assert_live_run_is_authorized` (`:1323`) and
  `assert_calibration_is_authorized` (`:1967`). In the run gate the check goes
  LAST, after `assert_manifest_binds_the_live_band` (`:1419`) and before
  `assert_limits_are_feasible` (`:1424`), so only an otherwise authorized run
  reaches the closing refusal; in the calibration gate it follows the
  mode-clause check (`:2077`). `fake` still returns at `:1353`, so every dry
  run keeps working. PLANTED both ways: one invocation is authorized against a
  root whose manifest copy drops the closing section and refused against the
  committed one. The three calibration authorizations that pass today
  (`tests/experiments/test_fresh_deduction_instrument.py:6634`, `:7972`,
  `:10738`) move onto that root through a helper modelled on
  `_root_binding_the_live_band` (`:475`). Results confirms `tasks/work/` holds
  no `ready` or `active` `fresh-deduction-authorization-*` or
  `fresh-deduction-limits-*` card, and that this card opens none.
- [x] `audits/deduction-candidate/held-out/manifest.json` is edited IN PLACE,
  keeping its path, with `status` set to `development` and a `converted` block:
  `date` 2026-09-16, `pull_request` `#465`, `branch`
  `work/fresh-deduction-run-5`, `rendered_seeds` all fifty accepted seeds in
  order, `informed` this card, `superseded_by` `null`, `note` giving the
  complete but INCONCLUSIVE result and the closing ruling. Every other byte is
  preserved, as the four earlier conversions preserved theirs,
  `dependency_restamps` included: its note is history and is not rewritten.
  `ConvertedRecord.superseded_by` (`experiments/held_out_prefixes.py:1472`)
  becomes `str | None`, commented so `None` reads as "the evaluation closed and
  no band replaced this one". The file is NOT moved to
  `manifest-band-8000-8999.json` and NOT added to `CONVERTED_BANDS`
  (`experiments/held_out_prefixes.py:375-400`): nothing took the live slot, and
  adding this band would make
  `test_the_inputs_row_names_every_converted_band`
  (`tests/experiments/test_fresh_deduction_instrument.py:4777-4814`) demand a
  Seed band row naming the band it also binds. Results states the alternative.
- [x] The regeneration test (`tests/experiments/test_held_out_prefixes.py:796`)
  becomes an archive check that regenerates nothing. STILL CHECKED: the
  `accepted`, `skipped` and `source_sha256` blocks are byte-identical to the
  bytes this band was frozen with, pinned as three `_block_digest` constants in
  the idiom of `_BAND_7000_BLOCKS_AT_1323CD75` (`:891-899`) and named for the
  commits that wrote them, `88d42f82` for the first two and `72998c7b` for the
  third; fifty unique digests over seeds 8000 to 8057; eight `witnessed_kill`
  skips; the development definitions absent; no prefix bytes. NO LONGER
  CHECKED: that today's generator reproduces those fifty digests. Results says
  so in one sentence and says what carries the weight instead: the record names
  its 22 source digests, so the regeneration stays reproducible from a checkout
  of `72998c7b`, and the generator keeps its coverage on the debug seeds, which
  touch no band. PLANTED both ways: mutating one accepted digest in a copy
  turns the check red, and editing a `GENERATOR_SOURCES` file leaves it green.
- [x] `write_manifest` (`experiments/held_out_prefixes.py:1569`) refuses to
  overwrite an archived record, so the `__main__` path cannot regenerate over
  the bytes the fifth run consumed; freezing again needs its own card. PLANTED:
  a root whose record is `held_out` is written, one carrying a `converted`
  block is refused. `PREREGISTERED_BAND` (`:345-350`) keeps 8000-8999,
  commented to say it names the band the archived record holds, that no run
  draws it, and that a seventh band needs its own card; the `ConvertedBand`
  docstring (`:353-363`) and the module docstring (`:9`) stop calling the
  record at `MANIFEST_PATH` the held-out one. A test asserts the closed state
  directly: no record under `audits/deduction-candidate/held-out/` has
  `status == "held_out"`. The range guard (`:1187-1230`) and `tally_reasons`
  (`:1233`) are unchanged, and band 2100-2999 is named in no source file,
  constant, test or tally range: its reservation lives in the documents, and
  Results says plainly that nothing in code stops a future tally over it.
- [x] `test_a_binding_to_a_converted_record_stays_an_open_obligation`
  (`tests/experiments/test_fresh_deduction_instrument.py:4816`) gains a third
  branch for the closed state, a `development` record AT `MANIFEST_PATH`:
  `superseded_by` is `null`, the execution manifest carries the closing clause,
  and an otherwise well-formed live invocation is refused. The other two
  branches keep their assertions unchanged, so a future freeze restores the
  obligation without an edit. PLANTED: a copy whose `converted.superseded_by`
  names a path while the record sits at `MANIFEST_PATH` fails it.
- [x] `combined_accounts` is SHELVED, not deleted, and said so in the closing
  record: the arm definition
  (`experiments/fresh_deduction_instrument.py:1160-1169`) stays, its levers
  stay default-OFF (`orchestrator/experiment_config.py:42-50`), its templates
  stay in the tree and keep rendering in the suite, no card develops it,
  nothing is re-scored. ONE later edit to that arm is expected and named here:
  [the grounded-SKIP card](grounded-skip-and-guard-labels.md) retires
  `citation_relevance_version`, and `RecordedExperimentConfig` is
  `extra="forbid"` (`orchestrator/experiment_config.py:32`), so that card drops
  `citation_relevance_version=1` at
  `experiments/fresh_deduction_instrument.py:1167` and the arm keeps importing.
  The record also points that card at the wording it harvests: the candidate's
  SKIP register at
  `agents/strategic/prompts/qwen3_6_27b/vote_ballot_accounts.j2:21`, against the
  default's "a SKIP needs neither" at `qwen3_6_27b/vote_ballot.j2:268`. No
  template byte moves here.
- [x] The two open cards are disposed of.
  [The sixth freeze](held-out-prefix-freeze-6.md) is retired unexecuted and
  honestly under the validator: the title becomes the retirement, Status
  becomes `done`, Acceptance becomes one checked item stating that no sixth
  band was frozen, and `## Results` records the closure, its date and the
  ruling behind it. Its band search stays in Evidence as the document reserving
  2100-2999, with one sentence saying that reservation is a document and not
  code. [The v1 retirement](retire-temporal-evidence-v1.md) is re-assessed and
  NOT executed: Status stays `ready`, every box unchecked, no deletion
  performed, and one dated sentence in its Evidence records that the adopting
  record it waits for will not come from this evaluation, the only record the
  accepted direction produces being
  [the wave's single re-record](process-rerecord.md), whose adoption scope is
  that card's decision.
- [x] `audits/deduction-candidate/README.md` indexes the archived record as
  archived; the `audits/` row (`docs/artifacts.md:109`, today 26,522,872
  tracked bytes over 328 files, from `git ls-files audits | wc -l` and `git
  ls-files -z audits | xargs -0 cat | wc -c`) is recomputed with the change
  staged; `tasks/README.md:43`'s inventory sentence is updated for the retired
  card; `scripts/verify_ml_evidence.py` passes offline. Every item above that
  adds a gate carries its planted failure, applied, run and reverted, named in
  Results with the assertion it produced.

## Constraints

No live provider call of any kind, no calibration, and the credentials file is
never opened. The held-out generator is not run on any band: 2100-2999 must
stay unseen, and the archived band is not regenerated either, because this card
retires that regeneration rather than performing it one last time. No recorded
byte moves: no replay, report, usage profile or measurement record is
rewritten, re-scored or regenerated, and every published figure of the five
runs and three calibrations keeps its recorded meaning. Closing an evaluation
does not retrospectively turn its inconclusive result into a rejection.

No agent behaviour and no prompt byte. `agents/` does not import `engine/`,
`meetings/` does not import `experiments/`, and this card touches neither.
Invalid input raises: each new refusal is an exception naming the document and
the date, never a silent skip. This card is the only writer of both experiment
modules, both test modules and the four `audits/deduction-candidate/` documents
in wave 1; `docs/artifacts.md` and `tasks/README.md` are reconciled by the
coordinator at merge.

## Expected scope

`experiments/fresh_deduction_instrument.py` (the closure clause and its two
refusals), `experiments/held_out_prefixes.py` (optional `superseded_by`, the
`write_manifest` refusal, three comment blocks),
`tests/experiments/test_held_out_prefixes.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`audits/deduction-candidate/held-out/manifest.json`, that directory's
`README.md`, `preregistration.md`, `checkpoint.md` and `execution-manifest.md`
(one appended dated section), [the sixth freeze](held-out-prefix-freeze-6.md),
[the v1 retirement](retire-temporal-evidence-v1.md) (one dated sentence),
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s inventory
sentence, this card. Not in scope: `agents/`, `meetings/`, `orchestrator/`,
`engine/`, `llm/`, `frontend/`, every prompt template, every committed
recording. Delivered on `work/close-deduction-candidate-evaluation` with one
pull request into `main`, a merge commit or fast-forward and never a squash,
every commit carrying
`Card: tasks/work/close-deduction-candidate-evaluation.md`.

Order, identical on all seven cards. WAVE 1 is parallel and changes no agent
behaviour: [the process scorecard](process-scorecard.md),
[the spectator tour](spectator-tour-and-alternatives.md) and this card, which
merges FIRST so the substrate wave's `GENERATOR_SOURCES` edits owe no restamp
to a retired band. The SUBSTRATE WAVE is serial, all three moving the
`qwen3_6_27b` prompt stamps and the ballot or claim schema:
[alibi as a route](alibi-as-route.md), then
[grounded SKIP and guard labels](grounded-skip-and-guard-labels.md), then
[the weighing channel](ballot-weighing-channel.md). Then
[the re-record](process-rerecord.md), once. Deferred and in no card: the body
freshness band, an impostor who reports a body, the `docs/` front door.

## Record impact

Retires an evaluation and archives its inputs. No recording, report, DTO,
metric, weight or prompt byte moves; no experiment becomes ON; no adopting
record is created; no default behaviour changes here. The prompt version-bump
cascade does not apply: no `.j2` version marker, no `PROMPT_VERSION_SETS` or
`DEFAULT_PROMPT_VERSIONS` entry (`orchestrator/game.py:352`, `:397`) and no
live-recorded prompt-version test pin is touched. It applies to the three
substrate cards this card unblocks, and their change is a departure that has to
be said out loud: the owner's rulings of 2026-09-19 intend a change to SHIPPED
DEFAULT behaviour in prompts, in the ballot and claim schemas and in the
meeting guards, rather than another default-OFF lever, so `AGENTS.md:71-73` is
superseded for that wave and each of those cards says so in its own Record
impact. This card adds no lever and changes no default; it removes the two
obligations that would otherwise chain to all three, the restamp of a retired
band and a live gate that could still be opened.

Committed recordings keep loading and verifying: no analysis code, no schema
and no renderer is in scope, so `scripts/verify_samples.sh` and the four
`build_sample_report.py --check` runs read the same bytes as before and are run
as gates anyway. The `audits/` artifacts row moves because that directory's
bytes move, and is recomputed with the change staged.

## Validation

`uv run pytest tests/experiments -q` (fake and scripted providers only, $0),
with each planted failure applied, run and reverted, then `uv run python
scripts/validate_task_docs.py`, `uv run python scripts/check_doc_facts.py`, `uv
run python scripts/verify_ml_evidence.py` (offline; never `--complete`), `uv
run pytest tests/scripts/test_verify_ml_evidence.py -q`, then `bash
scripts/check.sh` run whole in a clean worktree so no gate after the first
failure is masked, then `bash scripts/verify_samples.sh`, then `uv run python
scripts/build_sample_report.py --sample-dir <set> --check` over each of
`replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i` and
`replays/ml_corpus/9p2i`. Never the live evaluation, never a live calibration,
never the held-out generator on a band.

## Results

Delivered on `work/close-deduction-candidate-evaluation`. The contract is
[the direction memo of 2026-09-19](../direction-2026-09-19-process-over-outcome.md),
whose decisions D1, D2 and D8 the owner accepted that date (rulings in its
section 12). The architecture this sits inside is
[explicit cleanup experiments](../../docs/architecture.md#explicit-cleanup-experiments):
`combined_accounts`'s three profile versions stay OFF and unadopted, and this
card moves no lever, no default and no recorded byte. The delivery rule is
[AGENTS.md](../../AGENTS.md) "Delivery" and
[the workflow](../../docs/workflow.md#one-card-per-change).

### What was decided, and why it reads this way

**The closure is a clause in the document, not a flag.** `CLOSURE_CLAUSE`
(`experiments/fresh_deduction_instrument.py`) is one sentence, held byte for
byte in the module and in the execution manifest's appended
"Closure (2026-09-19)" section, exactly as `RESUMPTION_CLAUSE` and the three
calibration clauses are. The four of them authorize a spend; this one refuses
it. `assert_the_evaluation_is_not_closed` reads the committed document, so
reopening the evaluation means deleting the owner's sentence from the record
that carries it — a visible act that needs its own card — rather than passing
an argument.

**Both gates, last among the document checks.** In
`assert_live_run_is_authorized` the call sits after
`assert_manifest_binds_the_live_band` and before `assert_limits_are_feasible`;
in `assert_calibration_is_authorized` it follows the mode-clause check. A run
naming the wrong model is told about the model — "this evaluation is closed" is
the answer for a run that would otherwise have been allowed, and putting it
first would hide every other defect behind the newest gate.
`test_a_misconfigured_run_is_told_what_is_wrong_with_it` holds that ordering.

**The section was APPENDED, after `## Verification of this manifest`,** so every
line citation the sections above carry stays valid, and it carries no row
beginning `| Seed band |`: `manifest_bound_band` requires exactly one, and the
Inputs table still holds it, bound to 8000-8999.

**Why the archived record was not moved and not listed.** It keeps the path
`audits/deduction-candidate/held-out/manifest.json`. The alternative was the
four earlier conversions' shape — `git mv` to `manifest-band-8000-8999.json`
plus a `CONVERTED_BANDS` entry — and it was rejected on both halves. A band
moves aside because the NEXT freeze takes the live path, and no band replaced
this one; and listing 8000-8999 as converted would make
`test_the_inputs_row_names_every_converted_band` demand a Seed band row naming
the band that row also binds, which is a document contradicting itself.
`superseded_by` is therefore `null`, typed `str | None` and commented to say
that `None` means the evaluation closed and no band replaced this one, not
"unknown" and not "not yet".

**`combined_accounts` is SHELVED, not deleted.** The arm definition stays, its
levers stay default-OFF in `orchestrator/experiment_config.py`, its templates
stay in the tree and keep rendering in the suite, and no card develops it. The
closing record names the one later edit that is expected:
[the grounded-SKIP card](grounded-skip-and-guard-labels.md) retires
`citation_relevance_version`, and `RecordedExperimentConfig` is
`extra="forbid"`, so that card drops `citation_relevance_version=1` from the arm
and the arm keeps importing. The record also points that card at the wording it
harvests — the SKIP register at
`agents/strategic/prompts/qwen3_6_27b/vote_ballot_accounts.j2:21` against the
default's "a SKIP needs neither". No template byte moved here.

**No card reopens the gates.** `tasks/work/` holds seven
`fresh-deduction-authorization-*` and `fresh-deduction-limits-*` cards
(`authorization`, `-2`, `-3`, `-4`, `-5`, `limits-4`, `limits-5`) and every one
of them is `**Status:** done`; none is `ready` or `active`
(`grep -l '^\*\*Status:\*\* \(ready\|active\)' tasks/work/fresh-deduction-authorization-*.md tasks/work/fresh-deduction-limits-*.md` exits 1 with no output). This card
opens none, and no sixth authorization or limits card exists.

### What the archive check still checks, and what it no longer does

`test_the_archived_band_keeps_the_blocks_it_was_frozen_with`
(`tests/experiments/test_held_out_prefixes.py`) replaces
`test_the_committed_manifest_regenerates_from_its_own_band`. NO LONGER CHECKED:
that today's generator reproduces those fifty digests — which is what made every
edit to a `GENERATOR_SOURCES` file owe this band a restamp, twice already
(`68dfe979` and its correction `72998c7b`, both for one lever's edit to
`orchestrator/game.py`). What carries that weight instead is the record's own
`source_sha256`: 22 files by name and digest, so the regeneration stays
reproducible from a checkout of `72998c7b`, and the generator keeps its coverage
on the debug seeds 9001-9002, which touch no band. STILL CHECKED: the
`accepted`, `skipped` and `source_sha256` blocks byte-identical to the bytes
this band was frozen with, pinned as `_BAND_8000_BLOCKS_AT_88D42F82` (accepted
`c0e7b0b0…`, skipped `86eba6d1…`) and `_BAND_8000_SOURCES_AT_72998C7B`
(`9e9ff7b5…`); fifty unique digests over seeds 8000 to 8057 in ascending order
with `last_accepted_seed` 8057; eight `witnessed_kill` skips and no other
reason; the source block naming exactly `GENERATOR_SOURCES`; the development
definitions absent (`test_the_manifest_records_the_development_definitions_as_absent`);
and no prefix bytes (`test_the_manifest_commits_no_prefix_bytes`).

This card is its own first demonstration: it edits
`experiments/held_out_prefixes.py`, which is one of the 22 sources, so the
retired test would have demanded a restamp of a retired band from this very
branch. It does not, and the archive check is green.

### 2100-2999: a document, not code

Nothing in code stops a future tally, freeze or recording over 2100-2999. That
band is named in no source file, no constant, no test and no tally range; the
range guard (`_refuse_a_seed_range_that_touches_a_frozen_band`) refuses only
`PREREGISTERED_BAND` and the four `CONVERTED_BANDS`, all of which were actually
frozen. The reservation lives in
[the retired sixth freeze card](held-out-prefix-freeze-6.md)'s Evidence and in
the closing records, and a seventh freeze would have to re-run that card's
census rather than trust it. `PREREGISTERED_BAND` stays 8000-8999, commented to
say it names the band the archive holds, that no run draws it, and that a
seventh band needs its own card.

### The two cards disposed of

[The sixth freeze](held-out-prefix-freeze-6.md) is retired unexecuted: title,
`**Status:** done`, one checked acceptance item stating that no sixth band was
frozen, and a `## Results` recording the closure, its date and the ruling. Its
band search stays in Evidence as the document reserving 2100-2999, with the
paragraph saying that reservation is a document and not code.
[The v1 retirement](retire-temporal-evidence-v1.md) is re-assessed and NOT
executed: `**Status:** ready`, every box unchecked, no deletion performed, and
one dated paragraph in its Evidence recording that the adopting record it waits
for will not come from this evaluation — the only record the accepted direction
produces being [the wave's single re-record](process-rerecord.md), whose
adoption scope is that card's decision.

### Verification

Run in this worktree with `uv sync --frozen` and `npm ci` done first.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 624 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 73 work cards, 7 ready / 66 done |
| `.venv/bin/python scripts/check_doc_facts.py` | passed (doc facts, front door, ml-program, budgets) |
| `.venv/bin/python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 — every check passed |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh`, whole, exit code captured directly | exit 0 — 8,001 Python tests passed, 20 skipped, 3 xfailed; 515 frontend tests over 19 files; strict mypy clean over 484 sources; ruff, import contracts (4 kept, 0 broken), doc facts, prompt sync and the production build all green |
| `bash scripts/verify_samples.sh` | exit 0 — all 50 `4p1i` and all 50 `9p2i` canonical samples verified clean |
| `scripts/build_sample_report.py --sample-dir <set> --check` over `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` | 4 of 4 exit 0: each report "is consistent with its replays" |

No live provider call, no calibration, no `--complete`, and the held-out
generator was run on no band by hand: the `.env` file was never opened.

### Planted failures, applied, run and reverted

| Gate | Plant | Assertion it produced |
| --- | --- | --- |
| The closing clause on both live gates | The committed manifest's `## Closure (2026-09-19)` section deleted | `Failed: DID NOT RAISE <class 'experiments.fresh_deduction_instrument.LiveRunNotAuthorized'>` on the run gate and on all three calibration modes; 4 of `TestTheClosingClause`'s 7 cases red, then green again on restore |
| The same, the other way, committed | `test_the_same_run_is_authorized_against_a_manifest_without_the_section` | The identical invocation passes the whole gate against a copy without the clause, so the refusal is the clause and nothing else |
| The archive check | `accepted[0].sha256` zeroed in the committed record | `AssertionError: assert 'd101e3d97508…' == 'c0e7b0b048c1…'` |
| The archive check, the other way | `orchestrator/game.py` (a `GENERATOR_SOURCES` file) appended to | `source digests now stale: ['experiments/held_out_prefixes.py', 'orchestrator/game.py']` and the archive check still green — the restamp obligation is gone |
| The closed branch of the obligation test | `converted.superseded_by` set to `MANIFEST_PATH` while the record sits there | `AssertionError: manifest.json is the archive at the live path and names 'audits/…/manifest.json' as its replacement; a record that HAS a successor is not the closed state` |
| `write_manifest` on an archive | `test_write_manifest_refuses_to_regenerate_over_an_archive` (committed, both ways) | `HeldOutPrefixError` matching `ARCHIVED record` over a root holding the archive, bytes unchanged; the same command over a `held_out` record writes it |
| The two prefix readers | `test_the_archive_reader_refuses_a_set_still_to_be_spent` and `test_the_committed_record_is_the_archive_and_the_live_reader_refuses_it` (committed, both ways) | `FrozenSetMismatch` matching `ARCHIVED record` on a held-out record, and matching `'converted' block` on the archive (`not 'held_out'` until the round-1 correction below moved the live reader's first refusal onto the block) |

Each tree-level plant was applied to the committed file, run, and reverted; the
suite is green on the restored tree and `git status` shows no stray edit.

### Decision that departs from the card's Expected scope

The card scopes `experiments/fresh_deduction_instrument.py` to "the closure
clause and its two refusals". One further change was directly necessary and is
reported rather than hidden. Marking the record `development` makes
`verify_frozen_set` refuse it, and `run_instrument` called that reader on the
FAKE path too — so the conversion alone turned 90 offline cases red and broke
the mechanics check this manifest publishes as reproducible
(`python -m experiments.fresh_deduction_instrument --dry-run`). The live gate is
not the thing that needed relaxing, so nothing about it moved: the body of
`verify_frozen_set` is now shared with a second, separately named reader,
`verify_archived_set`, which accepts EXACTLY the archived record (status
`development` plus a `converted` block) and refuses a `held_out` one by name.
`run_instrument` picks the reader from the provider, so every live path still
reaches `verify_frozen_set` and is refused twice over — by the closing clause
and by the status — while the rehearsal, which reaches no provider and renders
to no model, draws the archive. Neither reader can stand in for the other, and
both directions are planted. Closing an evaluation stops the spending, not the
arithmetic that documents what it spent.

### Limitations

- The rehearsal still REGENERATES the archived band's fifty prefixes each time
  it runs, because no prefix bytes are committed and it needs inputs. That is
  unchanged from before this card and is not the restamp treadmill: neither
  reader compares `source_sha256`, so a generator-source edit that leaves the
  prefixes alone — which is what the substrate wave's `orchestrator/game.py`
  edits are, per the restamp entry at `6a144038` — keeps every gate green.
- Nothing in code reserves 2100-2999, as stated above.
- The closure is enforced on the two authorization gates. A future session that
  deletes the clause and re-freezes a band reopens the evaluation; that is
  intended, and it is why the refusal lives in the committed document rather
  than in a constant nobody reads.
- No result is re-scored, so every figure this directory publishes keeps the
  meaning it had, including the fifth run's inconclusive one. Closing an
  evaluation is not a rejection of its candidate.
- Delivery states: Implemented and Verified here. Independently reviewed, owner
  reviewed, merged and adopted are not claimed; adoption is not applicable, as
  no experiment becomes ON and no adopting record is created.

### Review corrections, round 1 (2026-09-19)

Independent review returned four blocking findings, all of them about the new
refusals rather than the closure itself. Each is repaired below; none moves an
agent behaviour, a prompt byte, a recording byte or a published figure, and the
archived record's bytes are untouched, so the `audits/` inventory row does not
move again.

**Finding 1 and finding 2 are one defect, reported by two lenses: the archive
satisfied the live client factory.** `verify_archived_set` returned a
`FrozenSet`, which `build_authorized_client` accepts as proof that the inputs
were verified before a provider existed — so a caller holding the archive could
build a live client with no invocation and no closure check, and the docstring
claiming `verify_frozen_set` was that token's only producer had become false.
The two readers now return two types. `VerifiedPrefixRecord` holds what both
verify; `FrozenSet` and `ArchivedSet` are SIBLINGS under it, neither an instance
of the other, so the archive is not a `FrozenSet` narrowed by a flag but a
different record with a different name. `build_authorized_client` keeps its
annotation and gains the run-time half of it, refused before the credential is
read: mypy alone is enforced only where the checker runs.

Which reader is the client-ordering proof: `verify_frozen_set`, and it alone for
the evaluation path — with `verify_calibration_set` and `verify_calibration_draw`
for the two calibration paths, exactly as before. `verify_archived_set` is not a
fourth producer and proves nothing to that factory. The two docstrings that
stated the old invariant now state this one, in the module
(`build_authorized_client`) and in the test
(`TestAuthorizedClient::test_a_client_cannot_be_built_before_the_frozen_set_is_verified`).
The two cases that used to hand the archive to the factory to reach its
credential refusal now take a real `FrozenSet` from its only producer, through
`_verified_held_out_set`, which writes the pre-closing record into a `tmp_path`
copy and reads it back with `verify_frozen_set`: on this tree there is no
held-out set to verify, and a hand-built token would have asserted nothing about
who may produce one.

**Finding 3 (Codex 1): the live reader trusted `status` alone.** A copy of the
committed archive with one field flipped back to `held_out`, its `converted`
block left in place, was accepted and would have regenerated and re-spent all
fifty prefixes. The block is a FACT about the bytes — it names the run that
rendered them — and the status is a label, so the block is now checked first and
independently, with its own message naming the block and its date. The status
refusal stays for a record that carries no block
(`TestFrozenSet::test_a_set_marked_development_is_refused`). One consequence is
recorded rather than hidden: the committed archive is doubly disqualified, and
the live reader now names the block rather than the status when refusing it, so
the round-0 plant table above is annotated with the wording that reproduces at
this head.

**Finding 4 (Codex 2): `write_manifest` silently overwrote malformed records.**
The guard read the `converted` key alone, so development data whose block had
been dropped, and any file that was not a JSON object, fell through to a fresh
`held_out` manifest over the accepted hashes the guard exists to preserve — and
a file that was not JSON at all raised a bare `JSONDecodeError` where AGENTS.md
requires a named refusal. `_assert_the_file_in_the_way_is_a_freeze` now allows
exactly one shape, a JSON object marked `held_out` with no `converted` block,
and names the file and what was found there in every other case.

| Command, at this head | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 629 passed (624 before these corrections; the five new cases are the four planted above and the `FrozenSet` half of the client gate) |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 73 work cards, 7 ready / 66 done |
| `.venv/bin/python scripts/check_doc_facts.py` | passed (doc facts, front door, ml-program, budgets) |
| `.venv/bin/python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh`, whole, exit code captured directly | exit 0 |
| `bash scripts/verify_samples.sh` | exit 0 |
| `scripts/build_sample_report.py --sample-dir <set> --check` over the four sets | 4 of 4 exit 0 |

| Gate added in round 1 | Plant | Assertion it produced |
| --- | --- | --- |
| The client factory's type gate | `if not isinstance(frozen, FrozenSet \| CalibrationSet \| CalibrationDraw):` → `if False:` | `AssertionError: Regex pattern did not match. Expected regex: 'ArchivedSet is'. Actual message: "FEATHERLESS_API_KEY is not set…"` — the archive built past the gate |
| The same, statically | `build_authorized_client(verify_archived_set())` in a scratch module | `error: Argument 1 to "build_authorized_client" has incompatible type "ArchivedSet"; expected "FrozenSet \| CalibrationSet \| CalibrationDraw"`, with the `verify_frozen_set()` call on the next line accepted |
| The live reader's `converted` refusal | `elif "converted" in manifest:` → `elif "converted" in manifest and False:` | `Failed: DID NOT RAISE <class 'experiments.fresh_deduction_instrument.FrozenSetMismatch'>` on the flipped archive, and the committed archive accepted as a live set |
| `write_manifest`'s shape gate | the pre-review guard restored (`isinstance(existing, Mapping) and "converted" in existing`) | two `Failed: DID NOT RAISE <class 'experiments.held_out_prefixes.HeldOutPrefixError'>` — the file regenerated over — and one bare `json.decoder.JSONDecodeError` |

Each plant was applied to the committed file, run, and reverted; the two
modules were diffed against their pre-plant copies afterwards and are
byte-identical, and the suite is green on the restored tree.
