# Close the accuracy-gated deduction evaluation and shelve its candidate

**Status:** ready

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

- [ ] A dated closing record, 2026-09-19, attributed to the owner's acceptance
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
- [ ] A `CLOSURE_CLAUSE` constant, shaped like `RESUMPTION_CLAUSE`
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
- [ ] `audits/deduction-candidate/held-out/manifest.json` is edited IN PLACE,
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
- [ ] The regeneration test (`tests/experiments/test_held_out_prefixes.py:796`)
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
- [ ] `write_manifest` (`experiments/held_out_prefixes.py:1569`) refuses to
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
- [ ] `test_a_binding_to_a_converted_record_stays_an_open_obligation`
  (`tests/experiments/test_fresh_deduction_instrument.py:4816`) gains a third
  branch for the closed state, a `development` record AT `MANIFEST_PATH`:
  `superseded_by` is `null`, the execution manifest carries the closing clause,
  and an otherwise well-formed live invocation is refused. The other two
  branches keep their assertions unchanged, so a future freeze restores the
  obligation without an edit. PLANTED: a copy whose `converted.superseded_by`
  names a path while the record sits at `MANIFEST_PATH` fails it.
- [ ] `combined_accounts` is SHELVED, not deleted, and said so in the closing
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
- [ ] The two open cards are disposed of.
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
- [ ] `audits/deduction-candidate/README.md` indexes the archived record as
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
