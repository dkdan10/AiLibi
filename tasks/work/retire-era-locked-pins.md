# Retire the era-locked comparators, pins and fixtures the tree keeps by inertia

**Status:** ready

## Outcome

The tree keeps instruments, fixtures and test literals that measure eras the shown set has left. Some refuse to
run, some pin role or outcome counts on bytes that no longer exist, and some re-pin a count at every promotion
while proving no defect (craft rule 2). On 2026-10-09 the owner ruled, verbatim: "Merge both when verified and
retire the memo's D14 list" (decision memo 8.9). The list is the baselines memo's Part 4 D14 with D14-T1 to T3
and the RETIRE rows of its Part 3.1. The same day the owner amended it, verbatim: "Keep the comparison records"
(memo 8.9, "Amendment of 2026-10-09"): `replays/candidates/stage-b-r1` stays as the record that isolates the
cooldown dial, the proposal that round r+1 deletes round r is declined, and this card drops the round-1 item (L6);
everything else on the list stands. This card carries the list as amended, under craft rule 3 and
`docs/agent-procedures.md` "Retiring substrate levers": each mechanism goes with its coupled consumers, one
history line stays where the memo asks for one, and the registry rows are recomputed.

After this card:
- `scripts/counterfactual_phase20.py` (refuses to run) is gone with its test and its two coupled tests.
- The prompt-regression fixture family and its close gate are gone, and so is their always-on entry.
- The three Phase-10 corrected-baseline fixtures, their anchor tests, `WAVE2_GATE_SPEC`, the `--baseline-out`
  derivation and the gameplay-facts extractor's cross-era rows are gone. The six Phase-10 fold functions stay,
  because the committed eval report, the frozen referee and the frozen deception instrument are built from them.
- `RATIFIED_I11_CELLS` and the S9 disclosure tuple are each replaced by one dated history line.
- The scorecard page no longer folds the fifth run. Its archive stays byte for byte.
- `replays/candidates/stage-b-r1/` stays whole, with its golden row and every reader of it, as the amendment rules.
  No byte under `replays/candidates/` moves, and the candidates README's rule is not changed here.
- The re-pin family is split. A pin that only copies a count from the shown bytes is deleted, derived at test time
  or moved behind the campaign marker. Integrity, firewall, determinism and digest pins stay in the default gate.
- The tier contract is re-derived once from the direction's yardstick. The four ML value-pin files move as D14-T1
  option (b) says. `docs/workflow.md` states the campaign re-run rule, and the campaign workflow gains a per-change
  trigger on `tests/training/**`, its weekly schedule unchanged.

No recorded byte is edited, no history is re-scored, and the corpus FROZEN line and every ML artifact stay where
they are. Nothing ships: the demo bundle built at the base and at the head is identical.

## Evidence

Doctrine: `tasks/direction-2026-09-19-process-over-outcome.md` and its addenda (a vote rests on held data; role-
correctness reported, never a gate); `docs/game-shape.md`; AGENTS.md craft rules 2, 3, 5 and 6; `docs/workflow.md`;
`docs/architecture.md`; `docs/artifacts.md`; the decision memo `tasks/decision-2026-09-24-stage-b-wave.md` sections
8.5, 8.7, 8.8 and 8.9 (`:1601-1622` at `335cbdc9`, its amendment of 2026-10-09 at `:1612-1622`), and section 1's
proposal at `:246-248`, which the amendment declines; the baselines memo
(`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`,
an advisory memo outside the tree): Part 2 rows G21, G24, G26, G27, G29, G52, G58, S17, L6, L9, V7, W45 and T3-T6,
Part 3.1's RETIRE, DEMOTE and REBASE rows for them, and Part 4 D14 with D14-T1 to T3. Templates:
`tasks/work/promote-round-2.md` (Evidence item 10, the re-pin sweep) and `tasks/work/post-promotion-follow-through.md`
(the re-pin count). Held cards: `tasks/work/rubric-extractor-era.md`, whose W-row half this card takes under G27 and
which the orchestrator closes unexecuted before this card merges, and `tasks/work/retire-temporal-evidence-v1.md`,
which stays `ready` and blocked pending the owner's D15 word and which this card does not touch. Every `path:line`
below is a citation at `335cbdc9`, the amendment's commit, labelled as such and re-anchored by symbol at dispatch;
`git diff --stat 225d2b77 335cbdc9` names only the decision memo, so every other citation reads the same at
`225d2b77`, where it was first measured. Every count is count-only, measured by the command beside it and
re-measured at dispatch; the dispatch figure governs.

**What goes, and who reads it** (at `335cbdc9`; consumers by `git grep`, dated history excluded: `agent_prompts/`,
`tasks/phase-*.md`, closed audits, `DESIGN.md`, `training/reports/` and the coevo EVIDENCE-MANIFEST stay as written):

| item | mechanism | coupled consumers |
|---|---|---|
| G29 | `scripts/counterfactual_phase20.py` (1,722 lines; refuses since the baseline-7 graduation); `tests/scripts/test_counterfactual_phase20.py` (5 tests, one holding the Phase-20 counterfactual memo's table) | `tests/eval/test_recorded_arm_readers.py:1826-1845` and `tests/eval/test_regroup_instruments.py:294-306` import it to prove it refuses; prose at `tests/eval/test_recorded_flag_census.py:35`, `:542` and `scripts/counterfactual_phase21.py:121`. The memo `audits/audit-phase-20-counterfactual.md` is a closed audit and stays |
| G24 | `eval/prompt_regression.py` (342 lines), `tests/eval/test_prompt_regression.py` (7 tests), `tests/fixtures/prompt_regression/` (7 files, 2,023,961 bytes) | the always-on entry `tests/training/test_suite_tiers.py:47` and its docstring `:12-15`; `training/README.md:137-141`; docstrings `eval/alibi_fabrication.py:99`, `:119`; the comment `eval/meeting_quality.py:321` (the legacy suspicion-graph header it names is still emitted by `agents/strategic/prompts/qwen3_5_9b`, so the parse stays and only the comment changes); `docs/history.md:42-45` |
| G27 | `tests/fixtures/phase10/corrected_w{0,1,2}_baseline.json` (3 files, 12,507 bytes); `WAVE2_GATE_SPEC` (`eval/meeting_quality.py:2620-2666`, `__all__` `:3217`); `--baseline-out` with `corrected_baseline_from_report` and `serialize_corrected_baseline` (`scripts/build_sample_report.py:28`, `:35-45`, `:481-530`, `:588-609`) | `tests/eval/test_gate_spec_metrics.py:1-19`, `:85-86`, `:102-131`, `:1023-1153` (the anchor tests and the whole-derivation pin); `tests/eval/test_wave2_metrics.py:43`, `:685-696`; comments `eval/meeting_quality.py:78`, `:1931`, `scripts/build_sample_report.py:355`; the extractor's `_cross_era_trajectory` (`audits/workflows/extract_gameplay_facts.py:673-781`), its call `:3509-3529`, its facts key `:4548` and the self-check clause `:3818-3828`. `git grep cross_era` finds no other reader; `scripts/refresh_samples.sh` runs no extractor since the profile card rewired its rubric step (0 hits), so it needs no edit |
| G58 (kept) | the six fold functions of `eval/meeting_quality.py`: `recount_threshold_inversions` `:1285`, `compute_gate_metrics` `:1764`, `compute_multi_signal_conversion` `:2300`, `compute_supply_gauges` `:2493`, `compute_conversion_per_meeting` `:2732`, `compute_effective_deflection` `:2881` | `scripts/build_sample_report.py:75-80`, `:336-337`, `:356-357`; `eval/meeting_quality.py:3206`; `eval/watchability.py:348`, `:2449`; `eval/deception_instruments.py:172`, `:828`; the extractor `:154-156`, `:3410`, `:3416` (both results feed other facts rows, `:4427-4488`); `tests/training/test_conviction_model.py:35`, `:272`. Only the `--baseline-out` calls (`:502-505`) leave |
| G52 | `RATIFIED_I11_CELLS` (`eval/evidence_honesty.py:875-915`), `RatifiedTargetingBaseline` (`:847-873`), `RATIFIED_BASELINE` (`:305`) | docstrings `:140-147`, `:813-817`, `:1150-1154`; `tests/agents/test_impostor_policy.py:2159-2320` (the "before" asserts); `tests/scripts/test_measure_baseline_cli.py:22-23`, `:257-304` |
| G21 | `_DISCLOSURE_HISTORY` and `_DISCLOSURE_HISTORY_COMMIT` (`scripts/check_doc_facts.py:951-965`) and the S9 branch of `check_corpus_disclosures` (`:1129`, `:1153-1166`, `:1210-1216`, summary `:1053-1056`) | `tests/scripts/test_check_doc_facts.py:2224-2258` (three tests); the note `replays/ml_corpus/README.md:118-123` and the pooled cell `:187` that adds S9's 145 |
| S17 | `FifthRunAppendix` (`eval/process_scorecard.py:590`), the `appendix` field (`:638`), `APPENDIX_NOTE`, `fold_fifth_run` and `FIFTH_RUN_ARCHIVE` (`:1862-1955`), the call `:2066`, `__all__`; the renderer `scripts/publish_process_scorecard.py:314`, `:399-423` | `docs/process-scorecard.md:227-231`, `docs/process-scorecard.json` (`appendix`); `tests/scripts/test_process_scorecard.py:45`, `:89`, `:302-308`. The archive `audits/deduction-candidate/run-2026-09-16` stays, and so does the writer's guard that refuses to write there (`:361`) |
| L6 (kept by the amendment) | `replays/candidates/stage-b-r1/` (55 tracked files, 37,095,574 bytes, tree `f295db68`; last changed `b16690af`, 2026-09-28) | not retired: the owner's amendment keeps it as the comparison record that isolates the cooldown dial. Its byte readers (the census, kill-cooldown, route-check, golden, route-lines, refresh and counterfactual tests, `docs/experiment-arms.md`'s Candidate round 1 section, `replays/candidates/README.md`) are not retargeted, and the golden's `candidates/stage-b-r1/9p2i` row stays (`tests/meetings/test_prompt_byte_golden.py:1368`) |
| L9 and V7 | the re-pin family | the round-2 promotion re-pinned 39 files with 530 `was` annotations (`git diff d41c9006 4a36dc03 -- tests/ frontend/src/`, added lines matching `(#|//) was`); V7's role literals `tests/api/test_eval.py:197-222`, `tests/eval/test_meeting_quality.py:542-615`; the e2e copies of the API's commit literal `frontend/e2e/evidence-journey.ts:45-46` (the identity is typed once in `tests/api/test_public_results.py:224-232`); the golden's `_RETIRED_GUARD_PINS` counts (`tests/meetings/test_prompt_byte_golden.py:1363-1369`). The sweep pattern of `promote-round-2.md` Evidence item 10 lists 108 files under `tests/`, `frontend/src` and `frontend/e2e` |
| D14-T1 | `tests/training/test_goodhart_probe.py` (30 default tests), `test_rewards.py` (54), `test_finalist_eval_pins.py` (26), `test_bakeoff_harness.py` (59): 169 of the 476 default tests under `tests/training/` | `_CAMPAIGN_FILES` `:53-64` and the single mixed file `:78-95` of `test_suite_tiers.py`; `training/README.md:137-141`; `pyproject.toml:93`; `CONTRIBUTING.md:84-87` |
| D14-T2 | `_ALWAYS_ON_FAMILIES` (`tests/training/test_suite_tiers.py:39-48`), locked decision 2 of Phase 19 | the seven families that remain after G24: champion acceptance, ES, determinism, artifact-digest, train/serve parity, the leak property sweep, the prompt byte-golden |
| D14-T3 | `.github/workflows/campaign-tier.yml` (schedule `:26-27`, its comment on path filters `:17-22`) | `docs/workflow.md` "Discover, implement, verify" |

Counts at `335cbdc9`: `git ls-files tests/fixtures | wc -l` gives 35 and `git ls-files -z tests/fixtures | xargs -0
wc -c` gives 4,064,349 bytes, the `docs/artifacts.md:105` row; removing the ten files leaves 25 files and 2,027,881
bytes. `audits/` holds 334 files and 31,431,870 bytes (`:113`); `replays/candidates/` holds 56 files (`:103`, 35 MB),
a row this card does not move (the record adds round 3's files to it first, and the promotion card recomputes it).
`uv run pytest --collect-only -q tests/training | grep -c ::` gives 476 and with `-m campaign` 337, which is the
whole campaign tier (every campaign mark sits under `tests/training/`). `uv run python scripts/verify_ml_evidence.py`
(offline, never `--complete`) exits 0: 64 checks, 52 OK, 0 FAIL, 7 ABSENT (evidence branches not fetched), 5 INFO.

**Registry rows each deletion recomputes** (`docs/artifacts.md` at `335cbdc9`; `verify_ml_evidence.py` compares a
"tracked bytes" figure exactly and a file count against the git index, `inventory_problems`): G24 and G27 move the
`tests/fixtures/` row (`:105`, exact bytes and files); the extractor edit moves the `audits/` row (`:113`, exact
bytes), which the round-3 record also writes, so it is re-derived after that merge. With L6 kept, the
`replays/candidates/` row (`:103`) is not this card's. S17 leaves the scorecard row's "3 files" and G21 leaves the
`replays/ml_corpus/` row's "209 files" as they are. `tests/scripts/test_verify_ml_evidence.py` pins no live row value (its inventory cases
build synthetic trees), so it needs no edit while every row keeps its key.

**Why each goes.** G29 refuses to run and its pins match no committed set. G24 gates arithmetic over three Phase-5
fixtures, pins role scalars by exact equality and sits on the always-on list. G27's anchors compare eras the
shown set has left, and the extractor's W0 to W2 rows compare two eras and describe neither. G52 and G21 are
literals for bytes the tree no longer holds. S17 is the retired arena's appendix. L6 stays: the owner kept the
comparison records, because each era's candidate copy isolates one dial. The L9 transcription pins fail on any
re-record and prove no defect. The four ML files read role or outcome on frozen records in the per-change gate while the ML hold stands.

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case proving it bites. `B` is the merge base
with `main` after `main` is merged in following the round-3 record's merge; `H` is the PR head.

- [x] Review correction: the shown set's honesty cells are held again (review round 2). The first build's sweep
  had deleted their literals from `tests/eval/test_evidence_honesty.py` with no gate holding them (no honesty report is
  committed), and two listed-class mutants of the fold survived at `7ae55b51` that the base killed. Every shown-set
  literal that left is restored (57 assertions, 27 of them widening a sliced list back to all four sets) beside the
  partitions and row counts the sweep added, until the orchestrator answers the PR's Question.
  `test_the_agent_frame_reads_its_own_two_ticks_not_the_engine_frame` and
  `test_the_render_budget_counts_rendered_memory_rows_not_prompt_lines` hold the two named computations without the
  shown bytes. Proof: the two named mutants (P1, P2) and ten more mutants of the fold, nine of them in the listed
  classes, each fail that file at H; five of the twelve survived the file at `7ae55b51`, and each of those five
  also fails the two planted cases alone (`bin/mutate.py`, `bin/mutate_planted.py`).
- [x] Review correction: `scripts/check_doc_facts.py`'s module docstring (item 20) and `check_corpus_disclosures`
  say six coverage pairs, a crew and an impostor pair for each set in the tree, and that the corpus README's S9
  figures are a dated history record the check does not read (review round 2). Proof: `check_doc_facts.py` exits
  0; a count-only search for "eight roll-call" under `scripts/` gives 0.
- [x] Review correction: the shown set's supply gauges are held to a second surface. The first build's sweep had
  swapped their literals for bounds no gate held (the committed report has no supply block).
  `test_the_supply_gauges_equal_a_fold_of_the_recorded_rows` in `tests/eval/test_gate_spec_metrics.py` now requires
  them to equal an independent fold of the recorded meeting rows and to sit inside the committed report's flag
  taxonomy, and `test_an_impostor_accusing_itself_is_not_an_accused_impostor_meeting` plants the self-accusation the
  bytes never record. Proof: the flag-role read made a constant (each direction) and the weak and strong branches
  swapped each fail that file at H (`bin/mutate.py`, M3, M3b, M7).
- [x] Review correction: every walked set has a key in the golden again, `samples/9p2i` included. Its row is a
  counted one (meetings and ballots from an independent count of its replay files, the two moved-ballot cells literal
  zeros), and `_retired_guard_pin` raises `KeyError` for a set without a key and derives nothing in its place.
  Proof: `test_every_reconstruction_divergence_is_a_retired_guard[9p2i]` reads the counted row; the `samples/9p2i`
  key deleted from the source fails the golden (mutant G6).
- [x] Review correction: the golden's keying is an equality again, and a deleted row raises.
  `test_the_retired_guard_pins_are_keyed_by_the_path_under_replays` asserts the walked sets equal the keyed sets, and
  `test_a_walked_set_whose_row_is_deleted_raises` plants each deletion (`samples/9p2i`, `candidates/stage-b-r1/9p2i`)
  and expects `KeyError` naming the set. Proof: the round-1 row deleted from the source fails the golden (mutant G7;
  the review's same plant gave 4 passed at `29973a67`).
- [x] Review correction: `docs/architecture.md` no longer says prompt regression checks live under `eval/` (the
  Codex P2 on this PR). Proof: the multiline sweep (`bin/sweep.py`) prints no hit there; `check_doc_facts.py` exits 0.
- [x] Review correction: no other live sentence names the retired suite. The `TournamentEvalReport` docstrings in
  `eval/meeting_quality.py`, and `eval/cost_dashboard.py` with `tests/eval/test_cost_dashboard.py`, no longer name it
  as a consumer. Proof: the sweep, widened to multiline, spaced, hyphenated and task-name forms of every retired
  mechanism, goes from 134 hits to 121, each remaining hit classed in Results.
- [x] Review correction: Results ruling (6) no longer says the promotion card does not exist.
  `tasks/work/promote-round-3.md` (since `a331ab90`) and `stage-b-record-r3.md` name no retired path or symbol, and the
  golden names they read are kept. Proof: `bin/card_names.py`, count-only, gives 0 retired names in both.
- [x] Review correction: the swap rehearsal's failure list sums to its stated total. Proof: re-run at `d7360f27`;
  the per-file list in Results sums to the pytest total, by test id.
- [x] **G29 is gone with its consumers.** The script, its test and the two refusal tests that import it (in
  `test_recorded_arm_readers.py` and `test_regroup_instruments.py`, cited above) are deleted; the three prose sites
  are rewritten; one history line in `docs/history.md`'s Phase 20 entry names the last commit holding the script.
  Mechanism: Python import at collection, and the sweep. Proof: `git grep -n counterfactual_phase20` outside dated
  history prints only that line; a scratch test importing the module fails collection with `ModuleNotFoundError`.
- [x] **G24 is gone, and so is its always-on entry.** The module, its test and the seven fixture files are deleted
  (nothing else imports the module); the `_ALWAYS_ON_FAMILIES` entry and the docstring line leave
  `test_suite_tiers.py`; the comments and docstrings above are rewritten; `docs/history.md`'s Phase 5 entry gains one
  line naming the last commit holding the fixtures. Mechanism: the always-on meta-test (`test_suite_tiers.py:123`)
  asserts every listed file exists. Proof: a scratch copy re-adding the entry fails with "missing always-on file
  tests/eval/test_prompt_regression.py".
- [x] **G27 is gone; G58 stays whole.** The three fixtures, the three anchor tests, the fixture constants and their
  digests, `WAVE2_GATE_SPEC` with its test, `--baseline-out` with its two helpers and its whole-derivation pin, and
  the extractor's cross-era function, call, facts key and self-check clause are deleted; one history line in the
  Phase 10 entry of `docs/history.md` names the last commit holding the fixtures. The six fold functions keep every
  consumer listed above. Mechanism: argparse; `build_sample_report.py --check` (the committed eval report's schema
  is unchanged); the extractor's own tests. Proof: `build_sample_report.py --baseline-out x` exits 2 with
  "unrecognized arguments"; `--check` exits 0 on all four sets; `git grep -n "corrected_w\|cross_era\|WAVE2_GATE_SPEC"`
  outside dated history prints only the history lines; each of the six names still has its production caller.
- [x] **G52 becomes one history line.** `RATIFIED_I11_CELLS`, `RatifiedTargetingBaseline` and `RATIFIED_BASELINE`
  (no reader survives) are deleted with the tests' "before" asserts; the module docstring of
  `eval/evidence_honesty.py` keeps one dated line naming the commit that last held the block and
  `audits/audit-phase-20-preregistration.md` section 3.1, where the values are recorded. The live-fold asserts of the
  same tests follow the L9 rule. Mechanism: strict mypy and import (a stale name fails). Proof: `measure_baseline.py
  --honesty --json` exits 0 on the four sets; a scratch import of `RATIFIED_I11_CELLS` fails.
- [x] **G21 becomes one history line, and the disclosure gate keeps its teeth.** The tuple, its commit constant and
  the S9 branch leave `check_doc_facts.py`; every cell the check still reads is re-derived from a recorded report in
  the tree. In `replays/ml_corpus/README.md` the note's checker clause becomes one dated history line naming
  `d41c9006` and the command that re-derives the S9 figures there; the S9 cells leave the labelled `**k/n**` shape
  the check reads, and the pooled crew-triggered cell is either re-derived over the three live sets or moved into
  that history line (the choice and its reason in Results). Mechanism: `check_corpus_disclosures`. Proof: the drift
  test retargeted to a live cell (`crew C9`) yields exactly one error; the three S9 tests are deleted; the checker
  exits 0.
- [x] **The scorecard page stops folding the fifth run; its archive is untouched.** The fold, its model, note,
  constant, field and section are deleted; the page header carries one history line naming the archive and the
  commit that last published the appendix; `SCHEMA_VERSION` goes to 3 with one dated line in its comment, because a
  version-2 reader expects the `appendix` key (the bump rule, `eval/process_scorecard.py:173-177` at `335cbdc9`);
  both files are regenerated. Mechanism: `publish_process_scorecard.py --check` and `read_before_columns`'s sha256
  pin. Proof: `--check` exits 0 at H and exits 1 on a scratch copy of the JSON with the `appendix` key restored;
  `git diff --stat B H -- audits/deduction-candidate/run-2026-09-16 docs/process-scorecard-before.json` prints nothing.
- [ ] **The re-pin family is split, and the next promotion re-pins no transcribed count.** The family is the 39 files
  above, V7's two files, `frontend/e2e/evidence-journey.ts`, the golden's pin table and any file a card merged
  since `335cbdc9` added with a literal count of a committed set (the sweep re-run at B). Each pin is classed as:
  *integrity* (schema validation, partition identities, byte identity, the frozen before columns), *firewall*,
  *determinism*, *digest* (of bytes that never legitimately change: weights, sidecars, frozen fixtures), or a
  *semantic zero* (retired rewrites, conformance cells, `unclassified == 0`, `citation_coerced == 0`), all of which
  stay in the default gate; or *transcription*, a literal equal to a count, rate or digest of the shown bytes that a
  legitimate re-record changes. A transcription pin is deleted where a byte-identity gate already holds the fact
  (`build_sample_report.py --check`, the census, scorecard and profile `--check`, `verify_samples.sh`), derived at
  test time where it cross-checks two surfaces, or, only under `tests/training/`, moved behind a function-level
  campaign mark. V7's role literals are deleted; the validation, route and partition asserts and the semantic zeros
  stay; each "was N" trail collapses to one history line. The e2e asserts the rendered source link equals the served
  summary's `source_url`, so the commit is typed once (the API test). The golden keeps its semantic zeros as
  literals and compares its meeting and ballot counts with an independent count of the replay files, with no
  campaign mark (it is an always-on family); every row keeps its key, the `candidates/stage-b-r1/9p2i` row included
  (the golden raises on an unpinned set). Results carry a ledger: per file, pins kept, deleted, derived and moved,
  each deletion naming the gate that holds its fact. Pins of instruments the owner keeps frozen (the baselines
  memo's KEEP FROZEN row, and G28's pins pending D15) are classed but kept unless a byte-identity gate already holds
  the same fact; the ledger names each. Mechanism: the swap rehearsal, run the way a promotion now runs under the
  amendment. In a scratch worktree at B and at H, round 2's replays, MANIFEST, roster, report and declared config are
  moved out of `replays/samples/9p2i` into `replays/candidates/stage-b-r2/` (its README carrying the
  `candidate-declaration` block), round 3's are moved in from `replays/candidates/stage-b-r3/`, and the era registry
  is pointed at both (`samples/9p2i` under a round-3 era; `STAGE_B_R2.declared_config` at the candidate copy); the
  default tier then runs. Proof: the failures at B that assert a transcribed count read 0 at H, apart from the
  frozen-instrument pins the ledger keeps; every failure left at H is one of those, or an integrity, provenance or era
  item the promotion card owns (a golden row for the new candidate copy among them), listed by test id.
- [x] **D14-T1 option (b) holds.** `test_goodhart_probe.py` and `test_rewards.py` carry `pytestmark =
  pytest.mark.campaign` (the seed-0 reward pin stays in the tree, per decision memo 8.2 item 4); in
  `test_finalist_eval_pins.py` and `test_bakeoff_harness.py` the value pins (win and loss counts and rates, per-arm
  `referee_passed`, baseline ids, floors and committed result rows) carry function-level marks while the prefix
  digest, row order, stamp conventions, firewall AST scans, determinism demotion, digests, round trips, seed-set
  derivation and objective fence stay default. `test_suite_tiers.py` lists the two whole files in `_CAMPAIGN_FILES`
  and generalizes the mixed file into a mapping of the three mixed files with their campaign and always-on names.
  `training/README.md` section 2 states the rule in one sentence with one history line. Mechanism: the tier
  meta-tests. Proof: a scratch copy with one value pin's mark removed fails; one with a module mark on a mixed file
  fails; one with a mark on an always-on name fails. Results record the default and campaign collection counts at B
  and at H.
- [x] **D14-T2: the always-on families are re-derived once.** Each family is classed by what its assertions judge:
  always-on is determinism, byte identity, firewall and provenance; a family that reads role or outcome on a frozen
  record is campaign. The table and one history line land in `training/README.md` section 2; the dict, its docstring,
  the marker description at `pyproject.toml:93` and `CONTRIBUTING.md:84-87` follow. A meta-test pins that every
  campaign mark sits under `tests/training/`. Mechanism: the tier meta-tests. Proof: a campaign mark planted in a
  `tests/eval/` copy fails; a mark on an always-on family file fails with its family named.
- [x] **D14-T3: the re-run rule is written and the trigger exists.** `docs/workflow.md` states that a change to a
  campaign-tier file records the campaign count, from the campaign workflow's run at the exact head cited by run id,
  or from `uv run pytest -m campaign` when no run exists. `campaign-tier.yml` gains a `pull_request` trigger with
  `paths: [tests/training/**]`, keeps the cron and `workflow_dispatch` unchanged, renames the job without "(weekly)"
  and rewrites its path-filter comment. A meta-test reads the workflow. Proof: a scratch copy without the path entry
  fails, and so does one with the cron changed.
- [x] **Registry rows, nothing else recorded, nothing shipped.** The `tests/fixtures/` and `audits/` rows of
  `docs/artifacts.md` are recomputed at H; the `replays/candidates/` row is untouched. Mechanism:
  `verify_ml_evidence.py` offline exits 0 with 0 FAIL; `git diff --stat B H` over `replays/samples`, `replays/candidates`,
  `replays/ml_corpus` (except its README), `training/artifacts`, `training/reports`, `agents/tactical/learned`,
  `experiments/lab` and the closed audits prints nothing; `verify_samples.sh` and `build_sample_report.py --check` pass on every set; the
  census, scorecard and profile `--check` exit 0; the demo bundle built at B and at H is identical (`diff -r`).
  Proof: a scratch tree with the fixtures row left at 4,064,349 bytes fails the inventory.
- [x] **No live-tense sentence describes a retired mechanism, and no copy carries an ID.** Each deleted name is
  grepped repo-wide and every live docstring, comment and doc line is rewritten. Each history line is dated, names
  its commit and links no deleted path. Mechanism: the sweep and `check_doc_facts.py`. Proof: a count-only scan of the
  added lines of `docs/history.md`, `docs/workflow.md`, `training/README.md` and `replays/ml_corpus/README.md` for
  `\b[A-Z][0-9]+\b` prints 0, and a scratch line with "G24" gives one hit.
- [x] **One bounded mutation pass and the CI record.** One pass over the card's changed production and gate lines
  (the checker's disclosure branch, the scorecard writer, the tier meta-tests and workflow pin, the derived e2e and
  golden checks) with the classes: dropped filter or wrapper, swapped collection, comparison made a None test, role,
  kind, room or tick read made a constant, dropped tuple member, swapped branches, loaded source read as its
  literal, and message argument made a constant (nonblocking after the first fix round). Survivors are listed. CI's
  green run at H and the campaign workflow's run at H are cited by run id.

## Constraints

**House rules.** The engine stays a pure deterministic tick function; `agents/` never imports `engine/`; no
module-level mutable state; invalid input raises. No new `AILIBI_*` lever, no prompt registry bump, no new field. No
recorded byte is edited or moved and no history is re-scored: round 1's candidate directory stays whole, as the
owner's amendment of 2026-10-09 rules. The corpus FROZEN line and every ML artifact never move (offline
`verify_ml_evidence.py`, never `--complete`). Role-correctness is reported, never a gate; nothing pushes an agent
toward the correct answer; the meeting layer labels and never rewrites. Stage-B lessons bind: each production line is
held by a test that goes red when neutered; guarantees are stated at delivered strength (the e2e no longer names the
commit itself; the moved ML pins run weekly and on `tests/training/**` changes, not on every change); live-tense
sentences about retired behaviour are fixed in the same PR; numbers are measured at the head that states them; no
test of a surviving mechanism is weakened, and each deleted pin names the gate that holds its fact; every sourced
constant has a planted source-change case.

**Not in scope.** The five live substrate toggles (the standing lever doctrine). Any recorded byte. The frozen corpus
and ML artifacts. `replays/candidates/` whole: round 1's directory, its readers and the family README (the amendment
keeps the comparison records, and the promotion card writes the family next). The extractor's other rows. G26's
synthetic decomposition tests and the six fold functions (G58). `counterfactual_phase21.py` beyond one comment, and
its test and pins (G28 waits on D15). Any value of a frozen instrument (the KEEP FROZEN row). D14-T1 option (c) (the
KEEP-row pins T13 and T14).
The dashboard copy, the README and the front door. Closed audits, `DESIGN.md`, frozen reports and lab records stay as
written; a frozen report whose run command now selects only the default half is a limitation stated in Results.

**Merge window against round 3's freeze, and order.** This card merges only after `tasks/work/stage-b-record-r3.md`
merges: from round 3's first seed to that merge, the record's freeze covers `engine agents meetings observation
orchestrator eval api scripts llm`, `experiments`, `training`, `audits/tactical-gameplay` and the paths its
nothing-moves diff reads (`tests/fixtures`, round 1's directory, `replays/ml_corpus`), and this card writes `eval`,
`scripts`, `training/README.md` section 2, `tests/training` and `tests/fixtures`. Dispatch may come earlier: the
branch is built and gated while round 3 records, never merged, then merges `main` in after the record's merge and
re-derives every row and count at that head. It merges before the round-3 promotion card (`promote-round-3`, one
card with the tour re-curation under decision memo 8.7 item 3), so that card re-pins fewer literals, and before
`front-door-process-first`. If the orchestrator keeps round 2 shown instead (memo 8.8), this card merges after the
record all the same, and the front-door card follows it. The held `rubric-extractor-era` is closed unexecuted by the
orchestrator's `docs:` commit on `main` before this card merges (its paths are outside the freeze), so it is never a
second writer of the extractor. `retire-temporal-evidence-v1` stays `ready` and blocked; its closure waits on the
owner's D15 word, and it is not dispatched beside this card.

**One writer per file.** This card writes Expected scope's files, in this order with its neighbours (each later
writer dispatches or merges `main` in after the earlier one merges):
- after the record: `tests/meetings/test_prompt_byte_golden.py` (the record's r3 row lands first; this card derives
  the counts and keeps the r1 row), `docs/artifacts.md` (the record's candidates and audits rows first; this card
  writes the `tests/fixtures/` and `audits/` rows only) and the L9 family files the record touches, if any.
- before the promotion: the L9 family (`frontend/src/lib/bodies.test.ts` and `contradictions.test.ts` among it), the
  golden, `frontend/e2e/evidence-journey.ts`, `docs/artifacts.md`, `scripts/check_doc_facts.py` and its test (the G21
  branch), `replays/ml_corpus/README.md` (the G21 note), `docs/history.md` (the Phase 5, 10 and 20 lines),
  `eval/process_scorecard.py`, `scripts/publish_process_scorecard.py` and `docs/process-scorecard.md` and `.json`
  (S17, schema 3), and `scripts/counterfactual_phase21.py` (one comment). The promotion writes each of them after
  this card merges.
- before the front-door card: `scripts/check_doc_facts.py` and its test.
- this card alone in the wave: `tests/api/test_eval.py` and `tests/eval/test_meeting_quality.py` (V7),
  `.github/workflows/campaign-tier.yml`, `pyproject.toml`'s marker text, `CONTRIBUTING.md`, `training/README.md`
  section 2, `tests/training/*`, `audits/workflows/extract_gameplay_facts.py`, `eval/meeting_quality.py`,
  `scripts/build_sample_report.py` and `eval/evidence_honesty.py`.
- never here: `replays/candidates/` and its README, `tests/scripts/test_candidate_sets.py`,
  `tests/scripts/test_counterfactual_phase21.py` and `docs/experiment-arms.md` (the amendment leaves this card no
  reason to write them; the promotion owns them), and `docs/process-scorecard-before.json`.

**Delivery and publication.** Branch `work/retire-era-locked-pins`, one PR into `main`, merged or fast-forwarded,
never squashed, never amended after push; merge `main` in, never rebase. Focused commits, one per item group. Each
commit body carries `Card: tasks/work/retire-era-locked-pins.md` immediately followed by the exact line
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The PR fills every template section; agents post no PR
comments. CI's green run at H, cited by run id, is the gate record (memo 8.7 item 1). Nothing ships: no viewer,
shown replay, public payload, README or media byte changes, and the V7 literals are test literals, not copy (the
dashboard copy in `frontend/src/lib/copy.ts` and `TournamentDashboard.tsx` is not written). The merge still reruns
`.github/workflows/pages.yml`, which rebuilds an identical bundle. The merge is the orchestrator's (memo 8.9).

**Stop and ask** if round 3's record does not merge; if `rubric-extractor-era` is still `ready` when this card is
ready to merge (its closure precedes this merge); if a deleted mechanism has a production consumer not listed here; if a transcription pin's fact is held by no gate and cannot be
derived; if a classification would move a pin the owner's KEEP rows protect; or if the swap rehearsal shows a
failure this card cannot class.

## Expected scope

Deleted: `scripts/counterfactual_phase20.py`; `tests/scripts/test_counterfactual_phase20.py`; `eval/prompt_regression.py`;
`tests/eval/test_prompt_regression.py`; `tests/fixtures/prompt_regression/` (`baseline.json`, `v_a/` and `v_b/`, each
`replay-seed-{8,13,30}.jsonl`); `tests/fixtures/phase10/corrected_w0_baseline.json`, `corrected_w1_baseline.json`,
`corrected_w2_baseline.json`. Nothing under `replays/` is deleted.

Production and generated: `eval/meeting_quality.py`, `eval/alibi_fabrication.py`, `eval/evidence_honesty.py`,
`eval/process_scorecard.py`, `scripts/publish_process_scorecard.py`, `docs/process-scorecard.md`,
`docs/process-scorecard.json`, `scripts/build_sample_report.py`, `scripts/check_doc_facts.py`,
`scripts/counterfactual_phase21.py` (one comment), `audits/workflows/extract_gameplay_facts.py`,
`.github/workflows/campaign-tier.yml`, `pyproject.toml` (the marker description only).

Documents: `docs/history.md`, `docs/artifacts.md` (the `tests/fixtures/` and `audits/` rows), `docs/workflow.md`,
`training/README.md` (section 2), `replays/ml_corpus/README.md` (the disclosure note and its cells),
`CONTRIBUTING.md`, and this card's Results.

Tests, by item: `tests/training/test_suite_tiers.py`, `test_goodhart_probe.py`, `test_rewards.py`,
`test_finalist_eval_pins.py`, `test_bakeoff_harness.py`; `tests/eval/test_recorded_arm_readers.py`,
`test_regroup_instruments.py`, `test_recorded_flag_census.py`, `test_gate_spec_metrics.py`, `test_wave2_metrics.py`;
`tests/scripts/test_check_doc_facts.py`, `test_process_scorecard.py`, `test_measure_baseline_cli.py`;
`tests/meetings/test_prompt_byte_golden.py`; `tests/api/test_eval.py`; `frontend/e2e/evidence-journey.ts`.

The re-pin family at `335cbdc9`, each written only where its ledger row moves a pin: `frontend/src/lib/bodies.test.ts`,
`contradictions.test.ts`; `tests/agents/test_absence_prior.py`, `test_beliefs.py`, `test_beliefs_hard_evidence_gate.py`,
`test_impostor_policy.py`, `test_memory_meeting_history.py`; `tests/api/fixtures/evidence_mechanisms.py`,
`tests/api/test_evidence_taxonomy.py`, `test_replay_loader.py`, `test_view_model.py`;
`tests/eval/test_accusation_calibration.py`, `test_deduction_metrics.py`, `test_evidence_honesty.py`, `test_funnel.py`,
`test_funnel_pooling.py`, `test_gate_metrics.py`, `test_kill_craft.py`, `test_meeting_quality.py`,
`test_reporter_justice.py`, `test_solvability.py`, `test_validity.py`, `test_vj_instruments.py`,
`test_vote_correctness.py`, `test_watchability.py`, `test_watchability_reanchor.py`;
`tests/meetings/test_citation_relevance.py`, `test_contradictions.py`, `test_manager.py`, `test_transcript.py`,
`test_vote_tally_parity.py`; `tests/training/test_surrogate_dataset.py`, `test_surrogate_fidelity.py`; plus any file
the sweep at B adds, named in the ledger (for instance `tests/eval/test_gameplay_census.py`,
`tests/scripts/test_refresh_samples.py` or `tests/experiments/test_route_check_replay.py`, only where a pin there
transcribes a count of the shown bytes; their round-1 legs stay as they are).

Never written here: `replays/samples/`, `replays/candidates/` (round 1's directory and the family README),
`replays/ml_corpus/` except its README, `tests/scripts/test_candidate_sets.py`,
`tests/scripts/test_counterfactual_phase21.py`, `docs/experiment-arms.md`, `docs/process-scorecard-before.json`,
`training/artifacts/`,
`training/reports/`, `training/rewards.py`, `agents/`, `engine/`, `meetings/`, `orchestrator/`, `api/`,
`frontend/src/` non-test files, `experiments/`, the round-3 audit and every closed audit, `DESIGN.md`,
`tasks/README.md`, the decision memo, the held cards and this card's Status line (the orchestrator's, on `main`).

## Record impact

**What moves:** ten fixture files leave the tree (reachable at the commits the history lines name); four modules,
scripts and test files are deleted; the scorecard pair regenerates at schema 3 without the appendix; two registry
rows; the tier map, its meta-test and the campaign workflow's triggers.

**What stays unchanged:** every byte, MANIFEST and report under `replays/samples/*`, `replays/candidates/*` and
`replays/ml_corpus/*`: round 1's and round 3's candidate sets both stay (the amendment); the frozen before columns;
the fifth-run archive; the ML artifacts and reports; the six fold functions and the committed eval reports' schema; the levers, the prompt registry and every default; the ladder
tip. **Publication:** none (an identical bundle rebuilds on merge). **Evaluation:** none; the default gate shrinks
by the moved and deleted pins, and the campaign tier grows by the moved ones, both counted in Results.

## Validation

Run in a bare shell (`env | grep -c '^AILIBI_'` prints 0) at H, after `main` is merged in following the record's
merge. Quote each exit code as it came back. On macOS the evolution-strategy hash pin is Linux-only, so CI's run at H
is the gate record (memo 8.7 item 1); no local `check.sh` is required at the final head.

```sh
git merge-base --is-ancestor <round-3 record merge> HEAD             # exit 0
uv run pytest tests/training/test_suite_tiers.py -q                  # the tier contract
uv run pytest --collect-only -q tests/training | grep -c ::          # default count, B and H
uv run pytest --collect-only -q -m campaign | grep -c ::             # campaign count, B and H
uv run pytest -m campaign -q                                         # the moved pins pass
uv run python scripts/verify_ml_evidence.py                          # offline, 0 FAIL, never --complete
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/publish_game_profile.py --check
bash scripts/verify_samples.sh
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
uv run python scripts/measure_baseline.py replays/samples/9p2i --honesty --json > /dev/null
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --baseline-out "$SCRATCH/x"  # exit 2
git diff --stat B HEAD -- replays/samples replays/candidates training/artifacts training/reports \
  agents/tactical/learned experiments/lab                            # empty
git ls-files tests/fixtures | wc -l; git ls-files -z tests/fixtures | xargs -0 wc -c | tail -1
git ls-files audits | wc -l
git log -1 --format=%s -- tasks/work/rubric-extractor-era.md         # the orchestrator's closure, before this merge
```

Then the swap rehearsal at B and at H in scratch worktrees (round 2 moved to `replays/candidates/stage-b-r2/` and
round 3 moved into `replays/samples/9p2i`, as Acceptance states; count-only, no prompt or transcript printed), the demo
bundle built at B and at H and compared with `diff -r`, the planted cases named in Acceptance, the frontend e2e in
CI's `frontend-e2e` job, and CI's green run at H plus the campaign workflow's run at H, each cited by run id.

## Results

Built on `work/retire-era-locked-pins` from `origin/main` at `97549508`, with `main` merged in at `a2433319`
(`9775c9d6`, one decision-memo docs commit). `B` below is `9775c9d6`, the merge base; the swap rehearsal's
B checkout ran at `97549508`, which differs from `B` only in `tasks/decision-2026-09-24-stage-b-wave.md`.
Round 3's record has not merged, so this head is built and gated but not mergeable: the merge waits for the
record's merge, then merges `main` in and re-derives every row and count below at that head (orchestrator
rulings 4 and 5). Every census here is count-only; no rendered prompt, transcript text or seed-band prefix
was printed, band 2100-2999 stayed unseen and the held-out generator was not run. Scratch work stayed under
the session scratchpad and nothing from it is committed.

**Commits.** `26cb11f2` G29; `f147954a` G24; `87ba4d2c` G27; `dc0c5f54` G52; `de39fdac` G21; `902e36f6` S17;
`f5b0aa30` D14-T1 to T3; `2a21144e`, `abcbb042`, `70ed42c3`, `5cd107d8`, `49cf72aa`, `911f8a11`, `6810a7ac`
the L9 and V7 sweep (the last two add the viewer suites, the e2e and the game-profile pair); `63ab4efb` the
Phase 5 history wording; `a2433319` the merge of `main`; then this Results commit.

**Sections relied on.** This card; `docs/architecture.md` ("Determinism and the substrate ladder", the
layering and the firewall); `docs/agent-procedures.md` ("Retiring substrate levers", "Environment and
history", "GitHub operations"); `training/README.md` section 2; `docs/workflow.md`; `docs/artifacts.md`;
the decision memo sections 8.7 to 8.9 with the amendment of 2026-10-09.

**Orchestrator rulings recorded.** (1) The owner's words bind: "Merge both when verified and retire the
memo's D14 list" and "Keep the comparison records" (decision memo 8.9 and its amendment of 2026-10-09).
That amendment is the reason L6 is not carried: `replays/candidates/stage-b-r1/` stays whole, its golden row
stays pinned, and the proposal that round r+1 deletes round r is declined. (2) The list retired is this
card's. (3) The swap rehearsal ran in scratch worktrees only. (4) The frozen-pathspec items (`eval`,
`scripts`, `training/README.md`, `tests/training`, `tests/fixtures`) merge only after round 3's record. (5)
The registry rows are re-derived at the merge. (6) Nothing deleted here is read by round 3's record or
promotion card: `tasks/work/stage-b-record-r3.md` and `tasks/work/promote-round-3.md` (on `main` since
`a331ab90`) name none of the retired paths or symbols (a count-only search for each name gives 0 in both).
Both read the golden's `_RETIRED_GUARD_PINS` table and its `KeyError` for a set without a key, and the
promotion card also reads `_retired_guard_pin` and a `samples/9p2i` row. Those are kept, not retired: the
first Results head dropped the `samples/9p2i` key and the `KeyError` for a walked set, and review round 1
restored both (corrected 2026-10-09; the first wording said no `promote-round-3` card existed).

### What left the tree

Deleted: `scripts/counterfactual_phase20.py`; `tests/scripts/test_counterfactual_phase20.py`;
`eval/prompt_regression.py`; `tests/eval/test_prompt_regression.py`; `tests/fixtures/prompt_regression/`
(`baseline.json`, `v_a/` and `v_b/`, each `replay-seed-{8,13,30}.jsonl`);
`tests/fixtures/phase10/corrected_w0_baseline.json`, `corrected_w1_baseline.json`,
`corrected_w2_baseline.json`. Nothing under `replays/` is deleted (`git diff --stat B HEAD` over
`replays/samples replays/candidates training/artifacts training/reports agents/tactical/learned
experiments/lab` prints 0 lines; under `replays/ml_corpus/` only the README moves).

The two refusal tests that imported the G29 script left `tests/eval/test_recorded_arm_readers.py` and
`tests/eval/test_regroup_instruments.py`; `WAVE2_GATE_SPEC` and its test, `--baseline-out` with
`corrected_baseline_from_report` and `serialize_corrected_baseline` and the whole-derivation pin left
`eval/meeting_quality.py`, `scripts/build_sample_report.py`, `tests/eval/test_gate_spec_metrics.py` and
`tests/eval/test_wave2_metrics.py`; the extractor lost `_cross_era_trajectory`, its call, its facts key
and its self-check clause. `RATIFIED_I11_CELLS`, `RatifiedTargetingBaseline` and `RATIFIED_BASELINE` left
`eval/evidence_honesty.py` with the "before" asserts of `tests/agents/test_impostor_policy.py` and
`tests/scripts/test_measure_baseline_cli.py`. `_DISCLOSURE_HISTORY`, its commit constant and the S9 branch
left `scripts/check_doc_facts.py` with three tests (two deleted, the drift test retargeted to `crew C9`).
`FifthRunAppendix`, the `appendix` field, `APPENDIX_NOTE`, `fold_fifth_run` and `FIFTH_RUN_ARCHIVE` left
`eval/process_scorecard.py`; the renderer's appendix section left `scripts/publish_process_scorecard.py`,
whose guard now names the archive in `PROTECTED_ARCHIVES` and still refuses to write there.

**History lines and the commits they name** (each commit an ancestor of H; `git diff --quiet <commit> B`
over the retired bytes exits 0 for each):

| line | names | tree | holds |
|---|---|---|---|
| `docs/history.md` Phase 5 | `4e5b6d6a` | `23b87d51cc9d` | the three-seed fixtures (the module changed later, so the line names the commit for the fixtures alone) |
| `docs/history.md` Phase 10 | `83148aa6` | `a84ec893cfa3` | the three corrected-baseline fixtures |
| `docs/history.md` Phase 20 | `a8a3db9b` | `aca64f72db63` | `scripts/counterfactual_phase20.py` |
| `eval/evidence_honesty.py` docstring | `09dab356` | | the I-11 block, byte-equal to B's; values in `audits/audit-phase-20-preregistration.md` section 3.1 |
| `docs/process-scorecard.md` header | `e75780b7` | `9854ec796a2b` | the last published appendix; the archive keeps its bytes |
| `replays/ml_corpus/README.md` note | `d41c9006` | | the S9 bytes; the note gives the command that re-derives the S9 figures in a checkout of that commit |

The pooled crew-triggered cell is re-derived over the three live sets (531/531) rather than moved into the
history line, because all three reports carry it and the check then keeps reading a live cell; the S9 cells
of item 8 leave the labelled `**k/n**` shape the check reads.

### Acceptance evidence (exit codes as they came back, bare shell: `env | grep -c '^AILIBI_'` printed 0)

| command, at H unless stated | exit |
|---|---|
| `uv run pytest tests/training/test_suite_tiers.py -q` (8 passed) | 0 |
| `uv run pytest -m campaign -q` (439 passed) | 0 |
| `uv run python scripts/verify_ml_evidence.py` (64 checks: 52 OK, 0 FAIL, 7 ABSENT, 5 INFO) | 0 |
| `uv run python scripts/check_doc_facts.py` | 0 |
| `uv run python scripts/validate_task_docs.py` | 0 |
| `publish_process_scorecard.py --check`, `publish_gameplay_census.py --check`, `publish_game_profile.py --check` | 0, 0, 0 |
| `bash scripts/verify_samples.sh` | 0 |
| `build_sample_report.py --check` on samples/4p1i, samples/9p2i, ml_corpus/4p1i, ml_corpus/9p2i | 0, 0, 0, 0 |
| `measure_baseline.py <set> --honesty --json` on the same four sets | 0, 0, 0, 0 |
| `build_sample_report.py --sample-dir replays/samples/9p2i --baseline-out x` ("unrecognized arguments") | 2 |
| `git merge-base --is-ancestor <round-3 record merge> HEAD` | not runnable: the record has not merged |

`git ls-files tests/fixtures | wc -l` gives 25 and the tracked bytes are 2,027,881, the row's figures;
`git ls-files audits` gives 334 files and 31,425,810 bytes, the row's figures (both re-derived after the
record's merge, which adds round 3's audit). `git log -1 -- tasks/work/rubric-extractor-era.md` reads
`97549508 docs: apply the extractor card's closure span correctly`, the orchestrator's closure, before
this merge. `git diff --stat B HEAD -- audits/deduction-candidate/run-2026-09-16
docs/process-scorecard-before.json` prints nothing.

**Planted cases** (each run in a scratch worktree at H and undone; `bin/planted.py` there):

| case | gate | exit | expected message |
|---|---|---|---|
| a scratch test importing `counterfactual_phase20` | collection | 2 | `ModuleNotFoundError` |
| the always-on entry for `tests/eval/test_prompt_regression.py` re-added | tier meta-test | 1 | "missing always-on file tests/eval/test_prompt_regression.py" |
| `from eval.evidence_honesty import RATIFIED_I11_CELLS` | import | 1 | `ImportError` |
| `--baseline-out x` | argparse | 2 | "unrecognized arguments" |
| the scorecard JSON with B's `appendix` key restored | `publish_process_scorecard.py --check` | 1 | (byte drift) |
| one finalist value pin's function mark removed | tier meta-test | 1 | "must carry a function-level campaign mark" |
| a module mark on the bake-off harness (mixed) | tier meta-test | 1 | "MIXED-tier file and may not carry a module-level" |
| a mark on the always-on `test_artifact_round_trip` | tier meta-test | 1 | "is an always-on pin and must stay in the default gate" |
| a campaign mark in a `tests/eval/` copy | tier meta-test | 1 | "campaign marks outside tests/training/" |
| a module mark on `tests/training/test_es.py` | tier meta-test | 1 | "ES: tests/training/test_es.py judges determinism" (the family named) |
| the workflow's `tests/training/**` path entry replaced | tier meta-test | 1 | failed |
| the workflow's cron changed | tier meta-test | 1 | "the weekly schedule must stay" |
| the `tests/fixtures/` row left at 4,064,349 bytes / 35 files | `verify_ml_evidence.py` | 1 | FAIL |
| the drift test retargeted to `crew C9` (`test_corpus_disclosure_coverage_cell_drift_detected`) | `check_corpus_disclosures` | passes | exactly one error, naming the cell; the three S9 tests are gone |
| a scratch history line naming "G24" | the ID scan | | one hit |

**Tier counts.** `uv run pytest --collect-only -q tests/training | grep -c ::`: 476 at B, 376 at H.
`uv run pytest --collect-only -q -m campaign | grep -c ::`: 337 at B, 439 at H (every campaign mark under
`tests/training/`). The whole default tier collects 10,886 at B and 10,763 at H. The campaign tier grows by
102: the two whole files (84 tests) and 18 function-marked value pins (15 finalist-eval, 3 bake-off). The
training default tier shrinks by 100: those 102, less the net 2 tests the tier meta-test gained (four new
cases replacing two).

**ID scan.** A count-only scan of the lines added between B and H for `\b[A-Z][0-9]+\b`: `docs/history.md`
0, `docs/workflow.md` 0, `training/README.md` 0, `replays/ml_corpus/README.md` 2. The two hits are that
README's own set labels (`S9`, `C9`) on the two lines of item 8 whose S9 cells lost their bold markers: the
label scheme is the README's defined vocabulary and the check locates `C9` by it, so the line cannot be
edited without carrying the label. No task or audit ID was added. A scratch line naming "G24" gives one hit.

### The re-pin ledger

Rule applied to each pin of the family (the 39 files of the round-2 sweep, V7's two files, the e2e, the
golden, and the files the sweep at B added): integrity, firewall, determinism, digest and semantic-zero pins
stay; a transcription pin is deleted where a byte-identity gate holds its fact (`build_sample_report.py
--check` for the committed reports, the census, scorecard and profile `--check` for their files,
`verify_samples.sh` for the manifests), derived at test time where it cross-checks two surfaces (a new
count-only helper, `tests/_helpers/recorded_counts.py`, reads each set's rows; sibling instruments and the
published census are the other surfaces), and moved only under `tests/training/`. Named exhibits are found
by the shape their test needs. The frozen sets (`replays/ml_corpus/*` and `replays/samples/4p1i`, baseline
9) keep their literals. "was" trails removed between B and H: 496 lines, counted by
`bin/ledger_counts.py` (added lines matching `(#|//) was`); the 318 left sit on frozen-set pins.

| file | derived | deleted (gate) | kept |
|---|---|---|---|
| `tests/_helpers/recorded_counts.py` (new), `tests/_helpers/committed.py` | the count fold; the movement-decided list names only the frozen sets' 51 meetings | | |
| `tests/eval/test_evidence_honesty.py` | the shown set's turns, prompts, ballots and meetings against the recorded rows (`tests/_helpers/recorded_counts.py`), and its testimony rows against a count of the tagged meeting frame in the recorded bytes; partitions and nestings beside every shown literal | none: no honesty report is committed, so no byte-identity gate holds the shown cells (corrected 2026-10-09: the first ledger named `build_sample_report.py --check`, which does not read this instrument) | the shown set's other cells as literals, restored in review round 2 because no gate holds them and none has a second surface short of re-implementing the fold (the card's stop-and-ask, raised in the PR's Questions); two planted cases for the agent-frame window and the rendered-row count; frozen sets; the semantic zeros |
| `tests/eval/test_gate_spec_metrics.py` (added 2026-10-09; the first ledger missed it) | the decomposition, the multi-signal fold and the committed report's impostor ejections agree; the supply gauges equal an independent fold of the recorded meeting rows (non-vent flags, weak and strong, zero-flag meetings, subject roles, accused-impostor meetings), the genuine-subject count is re-folded, and the flag census sits inside the committed report's taxonomy | the W0 to W2 anchor tests and the whole-derivation pin left with their mechanism (G27, not transcription). The committed report carries no supply block, so `build_sample_report.py --check` holds none of the gauges; the over-gate listener count is held by its synthetic case alone | the synthetic cases |
| `tests/eval/test_deduction_metrics.py` | the report-block cells as partitions and cross-checks (rows, DTO rule, kill-craft, impostor ejections); the weak-only exhibit found | shown literals (`build_sample_report.py --check`) | the meeting-flag cross-tab lines and the partner-ballot tuple, which `check_doc_facts.py` parses as the reading guide's source (front-door owned) |
| `tests/eval/test_gameplay_census.py` | the shown JSON figures as partitions and cross-checks; the harness, double-kill and trigger-tick games found | the shown literals (`publish_gameplay_census.py --check`) | round 1's legs; era pins |
| `tests/eval/test_reporter_justice.py`, `test_vj_instruments.py`, `test_vote_correctness.py`, `test_wave2_metrics.py`, `test_funnel.py`, `test_funnel_pooling.py`, `test_accusation_calibration.py`, `test_validity.py`, `test_solvability.py`, `test_kill_craft.py`, `test_gate_metrics.py`, `test_witness_entitlement.py` | the shown cells as their own ratios, partitions and nestings, held to the rows and sibling folds (I-2 claims, solvability body meetings, funnel report meetings, MANIFEST winners); the gate block equals its recompute; lost openings read off the rows; the witnessed-kill producer case found | | frozen sets; the four bare `nine.*` citation lines and the partner tuple `check_doc_facts.py` parses; the round-2 classification finding in `test_vote_correctness.py`, named as round 2's for the promotion to re-point; semantic zeros (genuine-class supply, sheltered survivors, retired guards) |
| `tests/api/test_eval.py`, `tests/eval/test_meeting_quality.py` (V7) | the ejection, meeting and SKIP partitions against the rows; the recompute equals the stored conversion block | every role-reading literal and the recount tables (`build_sample_report.py --check`); each trail is one history line | validation, route and partition asserts; `unclassified == 0`, `citation_coerced == 0` |
| `tests/api/test_evidence_taxonomy.py`, `test_observation_references.py`, `test_replay_loader.py`, `test_view_model.py` | taxonomy totals via the committed report; the citation exhibits, the forged ballot, the finales and the non-meeting control found; action labels against applied actions; chips equal the surrogate dataset's independent marker parse | | frozen 4p1i rows; the retired-guard zeros |
| `tests/api/fixtures/evidence_mechanisms.py`, `tests/api/test_evidence_mechanisms.py`, `tests/eval/test_watchability.py`, `test_watchability_reanchor.py` | | | classed and kept: the mechanism anchors are the executable evidence the Task-19.11 owner decision reserves, and the referee floors are the frozen referee (the KEEP FROZEN row); no byte-identity gate holds either |
| `tests/agents/test_absence_prior.py`, `test_beliefs.py`, `test_beliefs_hard_evidence_gate.py`, `test_impostor_policy.py`, `test_memory_meeting_history.py` | histograms partition the recorded meetings; anchors found by shape; the hard-evidence census and the counterfactual held to their partitions; the refuted living lead found | | the clamp's zero polarity; frozen rows and totals (re-measured over the three frozen sets) |
| `tests/meetings/test_contradictions.py`, `test_transcript.py`, `test_manager.py`, `test_vote_tally_parity.py`, `test_citation_relevance.py` | meeting totals counted off the rows; classes found by mechanism; compared ballots equal the recorded EJECT ballots; the collision held above zero | | frozen-set totals (25; 16/19/12/7/3/365; 531 with 321/210); retired-guard markers at zero |
| `tests/meetings/test_prompt_byte_golden.py` | `samples/9p2i`'s meetings and ballots come from an independent count of its replay files (a counted row); the route-line ballots equal the reconciled ballots | | the semantic zeros as literals; the `samples/4p1i` and `candidates/stage-b-r1/9p2i` literal rows; a key for every walked set and `KeyError` for a set without one (restored 2026-10-09); no campaign mark |
| `tests/orchestrator/test_replay.py`, `tests/training/test_surrogate_dataset.py`, `tests/scripts/test_measure_baseline_cli.py` | tick rows counted; the marker census per set; CLI lines against the instrument objects and the MANIFEST | | frozen sets' census rows |
| `tests/eval/test_game_profile.py`, `tests/api/test_game_profile_view.py` (added by the sweep at B) | shelf order and the tripped game's absence; the planted pointer on the chip's first member | the shelf sizes, members and readings (`publish_game_profile.py --check`) | |
| `frontend/src/lib/bodies.test.ts`, `contradictions.test.ts`, `annotations.test.ts`, `regroup.test.ts`, `vents.test.ts` (the last three added by the sweep at B) | frames, reports, meetings and flags counted off the JSONL; the census twins equal `docs/gameplay-census.json`; exhibits found; the negative controls stated as inequalities | | the fixture digests (integrity); frozen 4p1i literals; semantic zeros |
| `frontend/e2e/evidence-journey.ts` | each rendered source link equals the served summary's `source_url` | the two commit literals (typed once, in `tests/api/test_public_results.py`) | |
| `tests/training/test_goodhart_probe.py`, `test_rewards.py`, `test_finalist_eval_pins.py`, `test_bakeoff_harness.py` | | | moved: the two whole files carry the module mark; 18 value pins carry function marks (D14-T1) |

### The swap rehearsal

In scratch worktrees at B (`97549508`) and at H, round 2's replays, MANIFEST, roster and report moved to
`replays/candidates/stage-b-r2/9p2i/` with its declared config and a README carrying the
`candidate-declaration` block; the round-3 bytes moved into `replays/samples/9p2i`; `eval/eras.py` named
`samples/9p2i` under a round-3 era and pointed `STAGE_B_R2.declared_config` at the candidate copy; the eval
report, profile, census and scorecard were regenerated and the three corpus-bound viewer fixtures
regenerated from their documented generators; nothing was committed. **Round 3 has not recorded**, so round
1's candidate bytes stood in for it (its declared config differs from round 2's only by the missing
`kill_cooldown_ticks`). The rehearsal re-runs on round 3's bytes at the merge.

| | default tier (pytest) | viewer (vitest) |
|---|---|---|
| B | 535 failed, 23 errors | 17 failed |
| H (`d7360f27`, review round 1) | 342 failed, 23 errors | 1 failed |

By test id, 193 tests failing at B pass at H, and no test fails at H that passed at B; the 193 are the
transcription and exhibit pins above. Every failure left at H is one of these, by test id; the per-file
counts below sum to 342, pytest's own total (the full list is reproducible from the rehearsal's output). The
23 errors are 17 in `tests/experiments/test_route_check_replay.py` and 6 in
`tests/experiments/test_route_lines_replay.py`, the same count at B (round 1 of review re-ran H only; B's
bytes did not move). Review round 2 restored the shown honesty literals, so 23 of these 193 fail again at
`d66eb34e`; that round's subsection gives the re-run and the new totals.

- **Front door and era stamps the promotion or the front-door card owns** (195,
  `tests/scripts/test_check_doc_facts.py`, every test that runs the checker over the tree): the README and
  reading guide's dates and win rates, the era link, the `eval/vote_correctness.py` stamps, and the round
  record's win-split header.
- **Era and provenance items the promotion owns**: `tests/eval/test_eras.py` (8), `tests/api/test_sets.py`
  (15, the featured list's criteria and claims), `tests/scripts/test_measure_featured_criterion.py` (9),
  `tests/api/test_public_results.py` (22, the published cases and source roots),
  `tests/scripts/test_public_recording_provenance.py` (19), `tests/orchestrator/test_recording_fingerprint.py`
  (1), `tests/scripts/test_build_demo_bundle.py` (4), `tests/scripts/test_publish_game_profile.py` (4),
  `tests/scripts/test_publish_gameplay_census.py` (3), `tests/scripts/test_verify_ml_evidence.py` (3, the
  `replays/candidates/` row), `tests/scripts/test_refresh_samples.py` (2), `tests/eval/test_process_scorecard.py`
  (1), `tests/scripts/test_counterfactual_phase21.py` (1, never written here), `tests/meetings/test_route_lines_arm.py`
  (1, the declared-config listing of the candidate copy); `tests/experiments/test_route_check_replay.py` (21) and
  `tests/experiments/test_route_lines_replay.py` (5), with the 23 setup errors, which pin columns to recorded shas
  and to the r2 column's meetings, neither of which the scratch tree's stand-in carries;
  `tests/meetings/test_prompt_byte_golden.py` (2: the walk of the new candidate copy
  `candidates/stage-b-r2/9p2i` and the keying equality, both the missing row the promotion lands, since the
  golden raises on a walked set without a key); `tests/eval/test_gameplay_census.py` (9), whose round-1
  pooling and r2-column legs read the stand-in as round 1 itself (a stand-in confound) or the r2 column at
  its candidate path; the viewer's `PublicResults.test.tsx` declared-config copy (the stand-in's config).
- **Front-door literals kept** (`check_doc_facts.py` parses them): `tests/eval/test_deduction_metrics.py` (2),
  `tests/eval/test_vj_instruments.py` (1).
- **Kept by classification**: `tests/eval/test_vote_correctness.py` (1, round 2's recorded finding),
  `tests/api/test_evidence_mechanisms.py` (5, the reserved decision's anchors), `tests/eval/test_watchability.py`
  (7) and `test_watchability_reanchor.py` (1, the frozen referee); from `d66eb34e`,
  `tests/eval/test_evidence_honesty.py` (23, the shown cells restored pending the PR's Question).

### Bundle, mutation pass and CI

**Demo bundle.** Built at H and at B in one scratch checkout (B's bytes written over H's for every path that
differs, then H's restored): `diff -r` exits 0 over the bundle's 110 files. Nothing ships.

**Viewer e2e.** Run locally at H with the pinned Chromium (build 1194): `e2e/evidence.spec.ts` 2 passed and
`e2e/bundle.spec.ts` 4 passed, so the journey's source links equal the served summary's `source_url` in both
the API and the static mode. CI's `frontend-e2e` job is the record.

**Mutation pass** (one pass, 30 mutants, in a scratch worktree; `bin/mutate.py` there): the checker's
disclosure branch 8, the scorecard writer 6, the tier meta-tests and the workflow pin 8, the golden's derived
rows 4, the count helper 2, the e2e's derived links 2, over the classes the card names (dropped filter or
wrapper, swapped collection, comparison made a None test, role or kind read made a constant, dropped tuple
member, swapped branches, loaded source read as its literal, message argument made a constant). 26 killed:
21 by a failing run (20 on the committed bytes; the golden's literal-count mutant G4 on the swapped
rehearsal, where the count is not round 2's) and 5 (T1, T5, T6, T7, T8, the meta-test lines) because the
gate's planted case stopped biting or lost its message. 4 survived, each equivalent or unobservable on the recorded
bytes, so no fix round followed:
- C4, the pooled crew-triggered cell's numerator and denominator swapped: both read 531, since no recorded
  meeting is impostor-triggered (the cell's own claim).
- S2, the archive's `is_file` filter dropped from the protected-input list: it adds the archive's
  directories to a list that already refuses everything beneath the archive root.
- S5, the protected directories listed in reverse: the order is not observable.
- G3, the frozen-row lookup made a None test: the round-1 row's pin equals its independent count.
Each killing command passes unmutated (checked in the same worktree).

**CI.** At `3aaa5966`, the first Results commit: CI run 37917006312 green (project checks, frontend checks,
frontend e2e), and the campaign workflow's run 37917006619 green on the same head, triggered by the new
`pull_request` path filter. Each later head's two runs are cited by run id in the PR body, which carries the gate
record (memo 8.7 item 1). (Corrected 2026-10-09: this paragraph first said every later commit changed only this
card; review round 1 and round 2 changed tests and the checker.)

### Decisions and limitations

- The sweep at B added five files the round-2 sweep did not touch, because each transcribed the shown set and
  failed the rehearsal: `tests/eval/test_game_profile.py`, `tests/api/test_game_profile_view.py`,
  `frontend/src/lib/annotations.test.ts`, `regroup.test.ts` and `vents.test.ts`.
- Docstring follow-through outside Expected scope, each a live-tense sentence about a retired mechanism:
  `eval/balance_eval.py`, `eval/report_schema.py` and `tests/eval/test_alibi_fabrication.py` (G24).
- `audits/workflows/gameplay-data-audit-v2.workflow.js` still names the corrected fixtures in its Phase-10
  step text; it is that close audit's workflow (last changed at `76828008`), no live card runs it, and it
  stays as written with the closed audits.
- Frozen reports whose run command now selects only the default half: none found among the reports this card
  cites; the four moved ML files run whole under `-m campaign` (439 passed at H).
- The CI record at H is the gate record (memo 8.7 item 1); no local `check.sh` ran at the final head. The
  macOS checkout carries the Linux-only ES hash pin, which is why.

### Review corrections, round 1 (2026-10-09)

Three verifier lenses and the Codex review read `29973a67`; seven findings were blocking. This round's commits:
`3ec65c05` (the golden), `f31c78b7` (the supply gauges), `d7360f27` (the live sentences), then this Results
commit. Every figure below was measured at `d7360f27`, whose tree differs from this commit's only in this card.
Scratch work stayed under the session scratchpad (`retire-fix-r1-wf_4562b969-24c-5/`), nothing from it is
committed, and every census was count-only.

**What each finding asked, and what changed.**
- *The shown supply gauges had no gate.* The first build's sweep swapped ten literals of `compute_supply_gauges` on
  the shown set for bounds, but the committed report carries no supply block, so `build_sample_report.py --check`
  never held them, and two listed-class mutants survived. `tests/eval/test_gate_spec_metrics.py` now folds the
  recorded meeting rows independently (`_recorded_supply`: non-vent flags, their band by the production predicate,
  zero-flag meetings, subject roles from the report by `game_id`, accused-impostor meetings) and requires the
  gauges to equal it. It re-folds the genuine-subject count and holds the flag census inside the committed
  report's taxonomy (all flags equal the non-vent flags plus the recorded vent flags; weak and strong bound the
  taxonomy's weak-signal and cross-statement classes). The over-gate listener count parses each voter's
  rendered graph, which no second surface counts: its synthetic case holds the fold, and the shown count is not
  asserted (a stated limit). The file joins the ledger, and the honesty row's gate is corrected (below).
- *The golden dropped the `samples/9p2i` row and stopped raising for a walked set without one.* Each walked set
  has a key again. `samples/9p2i` holds a `_Counted` row: meetings and ballots from an independent count of its
  replay files, the two moved-ballot cells as literal zeros. The frozen rows stay literal, and
  `_retired_guard_pin`, the name `promote-round-3.md` cites, raises `KeyError` for any set without a key and
  derives nothing in its place. The keying test is an equality again (`walked == keyed`), and
  `test_a_walked_set_whose_row_is_deleted_raises` plants the deletion of each of the two rows. This restores the
  L9 item's "every row keeps its key ... the golden raises on an unpinned set", which the promotion and record
  cards read.
- *Ruling (6) said no `promote-round-3` card existed.* It has been on `main` since `a331ab90`. The sentence
  above is corrected in place. `bin/card_names.py` (count-only) finds none of the retired paths or symbols in
  `promote-round-3.md`, `stage-b-record-r3.md` or `front-door-process-first.md`. The golden names those cards
  read (`_RETIRED_GUARD_PINS` twice in each card; `_retired_guard_pin` once in the promotion card) are kept.
- *`docs/architecture.md` still placed prompt regression checks under `eval/`* (the Codex P2 on `3aaa5966`,
  anchored at `eval/report_schema.py:5`). Valid. The `eval/` paragraph now names the determinism and leak
  checks, both still there (`eval/determinism_test.py`, `eval/leak_scan.py`, `eval/leak_test.py`).
- *Other live sentences named the deleted suite.* `eval/meeting_quality.py` (the `TournamentEvalReport`
  module and class docstrings) now names the committed sample reports and the dashboard's API as the wrapper's
  readers. `eval/cost_dashboard.py` (module and field docstrings) and `tests/eval/test_cost_dashboard.py` (three
  docstring and comment sites) describe the cross-run comparison without the deleted loop.
- *The rehearsal's failure list summed to 338 against a stated 340.* There were two causes. The first tally
  parsed test ids up to the first space, so four spaced parametrized ids of
  `tests/experiments/test_route_lines_replay.py` collapsed into two (it read 3 for 5). It also stated pytest's
  total before `6810a7ac` fixed the two game-profile tests. Re-run at `d7360f27` with the parser fixed, the per-file
  list sums to pytest's own 342 (the table above, restated in place). The two golden failures that return at H
  are the new candidate copy's missing row, which the promotion lands, and the 23 errors are named by file.

**The widened sweep.** `bin/sweep.py` joins each tracked text file with comment markers stripped and whitespace
collapsed, so a phrase wrapped across a line break still matches. It searches the spaced, hyphenated, underscore
and task-name forms of every retired mechanism (prompt regression, Task 5.8, regression suite or loop, the
Phase-20 counterfactual, the corrected baselines, the Wave-2 gate spec, baseline-out, cross-era, the ratified
I-11 block, the disclosure history, the fifth run, the appendix symbols). It skips the dated-history paths the
card excludes and `tasks/`. It printed 134 hits at `29973a67` and 121 at `d7360f27`; the 13 removed are the sites
above. The 121 left, classed:

| class | hits | where |
|---|---|---|
| dated history lines | 11 | `eval/report_schema.py` (2, the version-bump history), `orchestrator/game.py` (5, prompt-bump history, a path this card never writes), `training/README.md` (2), `eval/evidence_honesty.py` (1), `docs/process-scorecard.md` (1) |
| the fifth run as the kept archive and its instruments | 81 | `experiments/fresh_deduction_instrument.py` (16) and its test (38), `experiments/held_out_prefixes.py` (1) and its test (2), `tests/agents/test_public_account_prompts.py` (5), `agents/strategic/prompts/loader.py` (1), `tests/scripts/test_paired_stats.py` (1), the scorecard JSON rows (6) and the frozen before column (1), and the scorecard's own lines: the archive it protects, its schema history line and the planted appendix case (`eval/process_scorecard.py` 3, `scripts/publish_process_scorecard.py` 3, `tests/scripts/test_process_scorecard.py` 4) |
| "cross-era" naming the refusal to pool across eras | 13 | `eval/gameplay_census.py` (4) and its test (3), `eval/reporter_justice.py` (1) and its test (2), `eval/process_scorecard.py` (1) and its test (1), `tests/scripts/test_check_doc_facts.py` (1) |
| other kept mechanisms | 3 | the champion-flip ruling's ratified floors (`tests/scripts/test_champion_flip_ruling.py`, 2); the Wave-2 gate-spec metrics, which are the kept fold functions (`scripts/build_sample_report.py`, 1) |
| closed audits' workflows | 13 | `audits/workflows/gameplay-data-audit-v2.workflow.js` (12), `audits/workflows/mvp-close-audit.workflow.js` (1) |

**Mutation probe of this round** (`bin/mutate.py`, `bin/mutate2.py`: 16 mutants in place, each restored, over the
spans the findings name and the spans this round changed, in the listed classes; the targeted file for each).

| id | span | class | result |
|---|---|---|---|
| M3, M3b | `compute_supply_gauges`, the flag subject's role | role read made a constant (impostor; crew) | killed, killed |
| M7 | the same, weak and strong | swapped branches | killed |
| S1 | the same, the accused subject's role | role read made a constant | killed |
| S2 | the same, the self-accusation filter | dropped filter | survived, then killed by the planted `test_an_impostor_accusing_itself_is_not_an_accused_impostor_meeting` (the shown bytes record 0 impostor self-accusations) |
| S3, S5 | the same, zero-flag and genuine-subject meetings | comparison inverted | killed, killed |
| S4 | `recorded_contradiction_flags`, the vent filter | dropped filter | killed |
| S6 | the same, the over-gate threshold | comparison made a None test | killed (the synthetic case) |
| S7 | the same, a turn's claims | swapped collection (observations) | killed |
| G1 | `_retired_guard_pin`, the missing-key test | comparison made a None test | survived: equivalent, because the mapping's own lookup raises `KeyError` naming the key |
| G2 | the same, the counted-row test | comparison made a None test | killed |
| G3 | the same, counted and literal rows | swapped branches | killed |
| G4 | the same, the counted row's moved ballots | loaded source read as its literal | survived: equivalent, because every counted row's semantic zero is 0 |
| G5 | the same, the counted meetings | swapped collection (turns) | killed |
| G8 | the same, the `KeyError` text | message argument made a constant | killed |

14 killed, 2 equivalent survivors. The planted row deletions run beside the probe: the `samples/9p2i` key and
the round-1 row, each deleted from the source, fail the golden. The review's same plant gave 4 passed at
`29973a67`. The earlier pass's G3 survivor (the old lookup made a None test) belonged to the derive-anything
lookup this round removed.

**Validation at `d7360f27`** (bare shell, `env | grep -c '^AILIBI_'` printed 0; exit codes as they came back):
`test_suite_tiers.py` 0; collection: `tests/training` default 376, `-m campaign` 439, whole default tier 10,766
(10,763 at `29973a67`, plus the two planted golden cases and the one planted supply case); `pytest -m campaign`
0; `verify_ml_evidence.py` (offline) 0; `check_doc_facts.py` 0; `validate_task_docs.py` 0; the scorecard,
census and profile `--check` 0, 0, 0; `verify_samples.sh` 0; `build_sample_report.py --check` on samples/4p1i,
samples/9p2i, ml_corpus/4p1i, ml_corpus/9p2i and candidates/stage-b-r1/9p2i 0, 0, 0, 0, 0; `measure_baseline.py
--honesty --json` on the four sets 0, 0, 0, 0; `--baseline-out` 2; the nothing-moves diff from `97549508` 0 lines;
`tests/fixtures` 25 files and 2,027,881 bytes, `audits` 334 files and 31,425,810 bytes (the rows' figures). The
extractor card's last commit is still the orchestrator's closure (`97549508`). Demo bundle: built at B
(`9775c9d6`) and at `d7360f27` in one scratch checkout, `diff -r` exits 0 over 110 files. The viewer suite at H in
the rehearsal: 1 failed, 810 passed, the same declared-config copy as before.

**Decisions of this round.**
- Follow-through outside Expected scope, each a live sentence about the retired suite: `docs/architecture.md` (the
  `eval/` paragraph; not a front-door page, and `promote-round-3` writes the file after this card merges),
  `eval/cost_dashboard.py` and `tests/eval/test_cost_dashboard.py`.
- The honesty ledger row names no gate, because none exists: no honesty report is committed, so the shown cells
  whose literal left in the first sweep are held only by their partitions, nestings and semantic zeros and by
  the instrument's synthetic cases. It is a stated limit, raised in the PR's Questions rather than widened here.
- The L9 acceptance box stays open. Its proof is the swap rehearsal on round 3's bytes, which do not exist yet,
  so it closes at the merge, when the rehearsal re-runs on them.
- CI's run at this round's head is cited by run id in the PR body (memo 8.7 item 1); no card-only commit records it.

### Review corrections, round 2 (2026-10-09)

Three verifier lenses read `7ae55b51`. Two findings were blocking, one from the integrity lens and one from the
documentation lens. This round's commits are `b4d972a0` (the honesty pins), `d66eb34e` (the checker's
docstrings) and then this Results commit. Every figure below was measured at `d66eb34e`, whose tree differs from
this commit's only in this card. Scratch work stayed under the session scratchpad
(`retire-fix-r2-wf_4562b969-24c-9/`), nothing from it is committed, and every census was count-only.

**What each finding asked, and what changed.**
- *The shown honesty cells had no gate.* The first build's sweep replaced the shown set's literals in
  `tests/eval/test_evidence_honesty.py` with partitions and nestings. No honesty report is committed, so no
  byte-identity gate held those cells, and two listed-class mutants survived at `7ae55b51` that the base killed:
  the agent-frame cell read over the engine window, and the render budget counted as prompt lines. The finding
  offered three repairs: planted synthetic cases, a derivation from the recorded rows, or the literals restored
  until the orchestrator answers the PR's Question. This round restores the literals for every cell and adds
  planted cases for the two named computations. The restored cells are I-2 to I-7 and I-10, the agent clock, the
  render budget's total, mean and buckets, the self-placement, trail and completed-task censuses, and the
  movement, grounded-prosecution and corridor counterfactuals. That is 57 assertions. 27 of them widen a sliced or
  baseline-only list back to all four sets, and each of the 27 assertions they replace is implied by its
  replacement. The cells that already had a second surface stay derived and are not re-pinned: the turns,
  prompts, ballots and meetings counted off the rows, and the testimony rows counted off the tagged meeting frame
  in the recorded bytes. The two planted cases hold the named computations without the shown bytes.
  `test_the_agent_frame_reads_its_own_two_ticks_not_the_engine_frame` has three cases: the spoken room in the
  agent window only, in the engine window only, and an agent window with no recorded tick.
  `test_the_render_budget_counts_rendered_memory_rows_not_prompt_lines` folds two six-line prompts, each with one
  observation row and one testimony row. The rest of the cells are not derived, because a derivation would be a
  second implementation of the fold inside the test, which is no independent surface. The card's stop-and-ask
  covers a fact no gate holds, so the cells stay literal and the PR's Question stays with the orchestrator.
- *The checker's docstrings promised eight recomputed coverage pairs.* Item 20 of the module docstring and
  `check_corpus_disclosures` now say six pairs: a crew and an impostor pair for each of the three sets
  `_DISCLOSURE_SETS` names. Both also say that the README's S9 figures are a dated history record the check does
  not read. The finding's repro (an edited crew S9 cell leaves the checker at exit 0) is now the documented
  behaviour. A count-only search for "eight roll-call" under `scripts/` gives 0.

**Re-probe of the removed cells.** `bin/mutate.py` applied 12 mutants of `eval/evidence_honesty.py` in place,
each restored afterwards, and byte-compared the source at the end. Each mutant ran against this round's test file
and against `7ae55b51`'s copy of it in the same tree (killed means the file fails). `bin/mutate_planted.py` ran the
same mutants against the two planted cases alone. Both test files pass unmutated.

| id | span | class | H | `7ae55b51` | planted cases alone |
|---|---|---|---|---|---|
| P1 | the agent-frame cell's window | swapped collection (the engine window) | killed | survived | killed |
| P2 | the render budget's row count | swapped collection (the prompt's lines) | killed | survived | killed |
| R1 | the agent-frame cell's empty-window guard | dropped wrapper | killed | survived | killed |
| R2 | the agent frame's tick offsets | dropped tuple member | killed | survived | killed |
| R3 | the copyable self-location test | comparison inverted | killed | killed | survived |
| R4 | the claim's speaker role | role read made a constant | killed | killed | survived |
| R5 | the two lower living-roster buckets | swapped branches | killed | killed | killed |
| R6 | the testimony-row match | comparison inverted (a None test) | killed | killed | killed |
| R7 | the testimony row's living count | a read made a constant (no listed class) | killed | survived | killed |
| R8 | the move's destination room | swapped collection (the origin field) | killed | killed | survived |
| R9 | the move's tick against the sighting's | dropped filter | killed | killed | survived |
| R10 | the venting meetings | dropped filter | killed | killed | survived |

All 12 are killed at H. Eleven are in the listed classes. R7 reads the living count as a constant, which no class
lists, so it is reported here and not counted in the pass. The five that survived `7ae55b51` (P1, P2, R1, R2,
R7) each fail the planted cases alone, so they stay held after a re-record moves the literals.

**The rehearsal, re-run for the changed files.** The scratch copy of `d66eb34e` had round 2's set moved to
`replays/candidates/stage-b-r2/9p2i/` and round 1's bytes copied into `replays/samples/9p2i`, with its declared
config written without `kill_cooldown_ticks`, as before. On that tree `tests/eval/test_evidence_honesty.py` reads
23 failed and 95 passed. `7ae55b51`'s copy of the file reads 114 passed, and B's copy reads 26 failed and 88
passed. By test id, the 23 are a subset of B's 26. The three B failures that now pass are the marker, persona and
tagged-frame tests, whose shown cells stay derived. `tests/scripts/test_check_doc_facts.py` gives the same
failure ids on that tree with this round's checker and with `7ae55b51`'s (187 failed each), so the docstrings move
no test. No other test file changed after `d7360f27`. The default tier on the rehearsal therefore reads 342 + 23 =
365 failed and the same 23 errors at `d66eb34e`. 170 of B's failures pass at H, and no test fails at H that passed
at B. The 23 are kept by classification (the ledger row above) and fail until the promotion re-pins them or the
orchestrator rules otherwise. The L9 box stays open, as before.

**Validation at `d66eb34e`** (bare shell, `env | grep -c '^AILIBI_'` printed 0; exit codes as they came back):
- `test_suite_tiers.py` 0.
- Collection: `tests/training` default 376, `-m campaign` 439, the whole default tier 10,770. That is 10,766 plus
  the four planted honesty cases.
- `pytest -m campaign` 0 (439 passed).
- `verify_ml_evidence.py`, offline, 0 (64 checks: 52 OK, 0 FAIL, 7 ABSENT, 5 INFO).
- `check_doc_facts.py` 0 and `validate_task_docs.py` 0.
- The scorecard, census and profile `--check`: 0, 0 and 0. `verify_samples.sh` 0.
- `build_sample_report.py --check` on samples/4p1i, samples/9p2i, ml_corpus/4p1i, ml_corpus/9p2i and
  candidates/stage-b-r1/9p2i: 0, 0, 0, 0 and 0.
- `measure_baseline.py --honesty --json` on the four sets: 0, 0, 0 and 0. `--baseline-out` exits 2 with
  "unrecognized arguments".
- The nothing-moves diff from `9775c9d6` prints 0 lines, and under `replays/ml_corpus/` only the README moves.
  The archive and before-column diff prints 0 lines.
- `tests/fixtures` holds 25 files and 2,027,881 bytes, and `audits` holds 334 files and 31,425,810 bytes: the
  rows' figures.
- The extractor card's last commit is still the orchestrator's closure (`97549508`).
- `tests/eval/test_evidence_honesty.py` 0 (118 passed). `tests/scripts/test_check_doc_facts.py` 0 (323 passed).

**Demo bundle.** `bin/bundle_compare.sh` built the bundle at `d66eb34e` and at B (`9775c9d6`) in one checkout.
For B it wrote B's bytes over all 96 differing paths, then restored the head, leaving a clean status. `diff -r`
exits 0 over the bundle's 110 files. Nothing ships.

**Decisions of this round.**
- The honesty cells are restored as literals rather than derived. A derivation would need a second implementation
  of the fold in the test, and the card's stop-and-ask covers a fact no gate holds. The PR's Question now asks
  whether the promotion re-pins these literals, or whether they leave with the planted cases holding the
  computations.
- The CI paragraph above said every later commit changed only this card. It is corrected in place.
- No follow-through outside Expected scope this round: `tests/eval/test_evidence_honesty.py` is in the re-pin
  family, and `scripts/check_doc_facts.py` is in Expected scope.
