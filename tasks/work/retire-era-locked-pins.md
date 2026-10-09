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

- [ ] **G29 is gone with its consumers.** The script, its test and the two refusal tests that import it (in
  `test_recorded_arm_readers.py` and `test_regroup_instruments.py`, cited above) are deleted; the three prose sites
  are rewritten; one history line in `docs/history.md`'s Phase 20 entry names the last commit holding the script.
  Mechanism: Python import at collection, and the sweep. Proof: `git grep -n counterfactual_phase20` outside dated
  history prints only that line; a scratch test importing the module fails collection with `ModuleNotFoundError`.
- [ ] **G24 is gone, and so is its always-on entry.** The module, its test and the seven fixture files are deleted
  (nothing else imports the module); the `_ALWAYS_ON_FAMILIES` entry and the docstring line leave
  `test_suite_tiers.py`; the comments and docstrings above are rewritten; `docs/history.md`'s Phase 5 entry gains one
  line naming the last commit holding the fixtures. Mechanism: the always-on meta-test (`test_suite_tiers.py:123`)
  asserts every listed file exists. Proof: a scratch copy re-adding the entry fails with "missing always-on file
  tests/eval/test_prompt_regression.py".
- [ ] **G27 is gone; G58 stays whole.** The three fixtures, the three anchor tests, the fixture constants and their
  digests, `WAVE2_GATE_SPEC` with its test, `--baseline-out` with its two helpers and its whole-derivation pin, and
  the extractor's cross-era function, call, facts key and self-check clause are deleted; one history line in the
  Phase 10 entry of `docs/history.md` names the last commit holding the fixtures. The six fold functions keep every
  consumer listed above. Mechanism: argparse; `build_sample_report.py --check` (the committed eval report's schema
  is unchanged); the extractor's own tests. Proof: `build_sample_report.py --baseline-out x` exits 2 with
  "unrecognized arguments"; `--check` exits 0 on all four sets; `git grep -n "corrected_w\|cross_era\|WAVE2_GATE_SPEC"`
  outside dated history prints only the history lines; each of the six names still has its production caller.
- [ ] **G52 becomes one history line.** `RATIFIED_I11_CELLS`, `RatifiedTargetingBaseline` and `RATIFIED_BASELINE`
  (no reader survives) are deleted with the tests' "before" asserts; the module docstring of
  `eval/evidence_honesty.py` keeps one dated line naming the commit that last held the block and
  `audits/audit-phase-20-preregistration.md` section 3.1, where the values are recorded. The live-fold asserts of the
  same tests follow the L9 rule. Mechanism: strict mypy and import (a stale name fails). Proof: `measure_baseline.py
  --honesty --json` exits 0 on the four sets; a scratch import of `RATIFIED_I11_CELLS` fails.
- [ ] **G21 becomes one history line, and the disclosure gate keeps its teeth.** The tuple, its commit constant and
  the S9 branch leave `check_doc_facts.py`; every cell the check still reads is re-derived from a recorded report in
  the tree. In `replays/ml_corpus/README.md` the note's checker clause becomes one dated history line naming
  `d41c9006` and the command that re-derives the S9 figures there; the S9 cells leave the labelled `**k/n**` shape
  the check reads, and the pooled crew-triggered cell is either re-derived over the three live sets or moved into
  that history line (the choice and its reason in Results). Mechanism: `check_corpus_disclosures`. Proof: the drift
  test retargeted to a live cell (`crew C9`) yields exactly one error; the three S9 tests are deleted; the checker
  exits 0.
- [ ] **The scorecard page stops folding the fifth run; its archive is untouched.** The fold, its model, note,
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
- [ ] **D14-T1 option (b) holds.** `test_goodhart_probe.py` and `test_rewards.py` carry `pytestmark =
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
- [ ] **D14-T2: the always-on families are re-derived once.** Each family is classed by what its assertions judge:
  always-on is determinism, byte identity, firewall and provenance; a family that reads role or outcome on a frozen
  record is campaign. The table and one history line land in `training/README.md` section 2; the dict, its docstring,
  the marker description at `pyproject.toml:93` and `CONTRIBUTING.md:84-87` follow. A meta-test pins that every
  campaign mark sits under `tests/training/`. Mechanism: the tier meta-tests. Proof: a campaign mark planted in a
  `tests/eval/` copy fails; a mark on an always-on family file fails with its family named.
- [ ] **D14-T3: the re-run rule is written and the trigger exists.** `docs/workflow.md` states that a change to a
  campaign-tier file records the campaign count, from the campaign workflow's run at the exact head cited by run id,
  or from `uv run pytest -m campaign` when no run exists. `campaign-tier.yml` gains a `pull_request` trigger with
  `paths: [tests/training/**]`, keeps the cron and `workflow_dispatch` unchanged, renames the job without "(weekly)"
  and rewrites its path-filter comment. A meta-test reads the workflow. Proof: a scratch copy without the path entry
  fails, and so does one with the cron changed.
- [ ] **Registry rows, nothing else recorded, nothing shipped.** The `tests/fixtures/` and `audits/` rows of
  `docs/artifacts.md` are recomputed at H; the `replays/candidates/` row is untouched. Mechanism:
  `verify_ml_evidence.py` offline exits 0 with 0 FAIL; `git diff --stat B H` over `replays/samples`, `replays/candidates`,
  `replays/ml_corpus` (except its README), `training/artifacts`, `training/reports`, `agents/tactical/learned`,
  `experiments/lab` and the closed audits prints nothing; `verify_samples.sh` and `build_sample_report.py --check` pass on every set; the
  census, scorecard and profile `--check` exit 0; the demo bundle built at B and at H is identical (`diff -r`).
  Proof: a scratch tree with the fixtures row left at 4,064,349 bytes fails the inventory.
- [ ] **No live-tense sentence describes a retired mechanism, and no copy carries an ID.** Each deleted name is
  grepped repo-wide and every live docstring, comment and doc line is rewritten. Each history line is dated, names
  its commit and links no deleted path. Mechanism: the sweep and `check_doc_facts.py`. Proof: a count-only scan of the
  added lines of `docs/history.md`, `docs/workflow.md`, `training/README.md` and `replays/ml_corpus/README.md` for
  `\b[A-Z][0-9]+\b` prints 0, and a scratch line with "G24" gives one hit.
- [ ] **One bounded mutation pass and the CI record.** One pass over the card's changed production and gate lines
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

Filled at delivery: every deleted path; the commits and tree shas the history lines name; the amendment of
2026-10-09 cited as the reason L6 is not carried; the L9 ledger and the swap rehearsal's counts at B and H; the
tier counts; the registry rows; each command's exit code; the mutation pass and its survivors; the CI run ids; the sections relied on (this card,
`docs/architecture.md`, `docs/agent-procedures.md`, `training/README.md` section 2); decisions and limitations.
