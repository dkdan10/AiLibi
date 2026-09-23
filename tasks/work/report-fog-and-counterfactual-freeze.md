# Keep the reported body in view on a game-deciding tick, and freeze the Phase-21 counterfactual memo

**Status:** ready

## Outcome

Three default-tier tests are red on `main` at `95fb894b`, and the owner's Q5 ruling of
2026-09-23 routed them to this card. The card changes as little as it can: one code fix in the
viewer's loader, and one retirement of a test that compares against a frozen record. Its items
keep the decision memo's section-5 numbering, whose item 2 (the adjacency guard) is card B's.

- **Item 1: the report-tick fog (a real viewer defect).**
   `tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body` fails because of
   how the loader handles one tick shape. When a body report lands on the tick that decides the
   game, the engine opens no meeting. The loader re-opens the reported body in the fog only in
   `MEETING` phase, so on that tick the reporter's served As-agent view drops the body they have
   just found.
   - After this card, the loader re-opens the body on that frame as well.
   - The test covers both committed sample sets.
   - A guard fails the test if no committed game still carries the shape.
- **Items 3 and 4: the Phase-21 counterfactual memo (a comparison that can only read red).**
   `tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run`
   and `::test_the_memo_marks_every_advisory_cell` compare a dated baseline-8 memo,
   `audits/audit-phase-21-counterfactual.md`, with a live run on the baseline-9 bytes. The memo
   is the frozen side of a measured/frozen pair, and nothing will ever re-issue it, so after any
   re-record this comparison can only fail. After this card:
   - The comparison is retired.
   - The drift gate carried one live assertion, the four corroboration cells. It keeps a test of
     its own, with a planted failure.
   - The fold and perturbation machinery existed only for the comparison. It is deleted, with
     one history line per deleted test.
   - The memo gains a dated provenance erratum, E.4. It names the commit and the command that
     reproduce its tables.

**What does not move:** recorded bytes, rendered prompt bytes, detector output, instrument
pins, scorecard figures, derived views, and every input an agent sees.

**What does move:** the served fog on the final frame of three games, none of them featured.
The PR names this viewer change first, because a merge to `main` publishes.

## Evidence

Every file:line citation is at `95fb894b`; re-verify each at dispatch. The routing and the
recommendation come from the orchestrator's 2026-09-23 decision memo (section 5, and card C in
section 6) and its `bugs_other` investigation. Those memos are not committed. Every figure below
either re-derives from the tree with the commands in Validation or is labelled as the
investigation's. Every figure is re-measured at dispatch.

**Ruling relied on (Q5, 2026-09-23, verbatim):** "Look into why the tests would still fail, if
they are necessary at all, or a separate potential path forward. Go with the recommended idea
from that." The recommended path is this card: a code fix for the fog, and retirement for the
memo comparison.

**Reproduction at `95fb894b`.** Run each id alone with `uv run pytest -q <id>`.

| test | where it fails | what it prints |
|---|---|---|
| the fog test | `tests/api/test_view_model.py:1267` | `p-9 does not see the body it reported (p-3) at tick 13 of headless-seed-13` |
| the drift gate | `tests/scripts/test_counterfactual_phase21.py:726`, `memo_pooled == live_pooled` | `C-1`: memo `(460, 1525)`, live `(529, 1516)` |
| the advisory-marks test | its subset assertion at `:678` | — |

The record (`audits/audit-2026-09-22-process-rerecord.md:1157-1158`) and its card
(`tasks/work/process-rerecord.md:1394`, `:1402-1403`) left all three red for this decision.

**Item 1: why the loader is at fault.**

*Engine order is by design.*
- `engine/tick.py:641-658` handles the report first.
- The win check then runs inside the `MEETING` branch: "A tick that decides the game does not
  open a meeting" (`9af1bf3d`).
- So the tick's events end `MeetingTriggered`, `GameOver`, and the phase is `GAME_OVER`.
- The recording has no `meeting` row at that tick.

*The recorded instance.* At tick 13 of `replays/samples/9p2i/replay-seed-13.jsonl`:
- `p-1 kill p-6` is applied;
- `p-6 do_task` is rejected;
- `p-9 report body-p-3-7` is applied;
- then `game_over` follows at tick 13 (`IMPOSTOR_PARITY`), with no `meeting` row.

*The event projection already handles this tick.* `api/replay_loader.py:2223-2251` suppresses
the `meeting_triggered` chip when `state.phase == "GAME_OVER"`. It still projects `report_body`,
"because the body was still found".

*The fog re-open does not handle it.*
- `body_id` is derived only under `if state.phase == "MEETING":` (`api/replay_loader.py:1683-1692`).
- It is passed as `reopened_body_id` at `:1702-1705`.
- `_agent_visibility_map` explains why the re-open is needed (`:2027-2036`): the solve excludes
  discovered bodies.
- `_meeting_trigger_from_events` (`:2926-2939`) returns no body for an emergency trigger.

*The defect has been latent since `9af1bf3d`.* The test reads only `samples/9p2i` (its fixture is
at `tests/api/test_view_model.py:126-135`), which held no such tick at baseline 8.

**Census of game-deciding report ticks.** One count-only walk over the replay JSONL. A game
qualifies when:
- its last `tick` row holds an applied `report`;
- `game_over` carries that same tick;
- no `meeting` row carries it.

| set | baseline 8, `39a568c6` (investigation) | baseline 9, `95fb894b` (measured writing this card) | the game: tick, reporter, body, how it ended |
|---|---|---|---|
| `samples/9p2i` | 0 | 1 | `headless-seed-13`: tick 13, p-9, p-3, `IMPOSTOR_PARITY` |
| `samples/4p1i` | 1 | 1 | `headless-seed-3`: tick 10, p-2, p-3, `CREWMATE_TASKS` |
| `ml_corpus/9p2i` | 0 | 0 | — |
| `ml_corpus/4p1i` | 1 | 1 | `headless-seed-1009`: tick 7, p-4, p-2, `CREWMATE_TASKS` |

On the two 4p1i ticks, the tick that decides the game is a completed task beside the report,
not a kill.

**Census of the reporter's fog.** This walk runs through `ReplayLoader`, measured writing this
card and count-only. It counts reporters whose served `visibility.visible_bodies` lacks the body
they reported:

| set | `report_body` events | reporters missing their own body |
|---|---|---|
| `samples/9p2i` | 136 | 1 |
| `samples/4p1i` | 37 | 1 |
| `ml_corpus/9p2i` | 416 | 0 |
| `ml_corpus/4p1i` | 37 | 1 |

Each miss is at exactly one of the three frames named above.

**Blast radius of item 1.**
- *Where the fog goes.* It feeds only the API's `AgentVisibilityView`
  (`api/replay_loader.py:3436-3446`, `api/schemas.py:272-286`).
- *Readers that do not see it.* Agents, memory, eval and ML read engine packets.
  `eval/funnel.py:377-395` re-runs its own observation walk.
- *The leak test.* `tests/api/test_leak.py:1125-1132` requires every visible body's room to be
  one the observer has seen, and the reporter's own room always is.
- *The demo bundle.* It bakes loader payloads for the featured games of `replays/samples` only
  (`scripts/build_demo_bundle.py:312-364`).
  - The featured list (`frontend/src/components/ReplayPicker.tsx:109-152`) is 9p2i seeds 23, 0,
    29, 2 and 4p1i seeds 2, 11, 29. None of the three games is on it, and `ml_corpus` is never
    baked.
  - A bake-only run measured at `95fb894b` on Darwin arm64 wrote 156 files and 4,808,974 bytes
    under `data/`. The tree digest, from the Validation command, is `37afc888dd22ecc4…`.
  - The investigation expects the tree to be byte-identical after the fix. This card measures
    that instead of assuming it.

**Items 3 and 4: why the comparison retires.**

*The memo is a dated baseline-8 record.* `audits/audit-phase-21-counterfactual.md:1-14`:
- "Every number here is recomputed on the baseline-8 bytes";
- dated 2026-09-01;
- "Substrate: baseline 8".

*It claims a live check.*
- The introduction to §10 (`:606-608`) says the test compares every row "so the memo cannot drift
  from the script".
- The Errata preamble (`:893-899`) says the test reads the errata as the authoritative pin.

*Its errata.*
- E.1 (`:901`) and E.2 (`:1070`) republished moved rows on the same baseline-8 population.
- E.3 (`:1224`) is provenance only: "No figure in this memo moves".
- The fold (`tests/scripts/test_counterfactual_phase21.py:3009-3034`) can override a row, but it
  cannot delete one.

**Measured drift on baseline 9.** This is the investigation's count, taken with the test module's
own parsers against `cf.run(all sets)`:

| surface | differing |
|---|---|
| pooled cells | 42 of 43 |
| per-set cells | 130 of 172 |
| ballot census | 15 of 16 |
| kind census | 5 of 8, and 7 of 8 |
| render census | 18 of 18 |
| ledger rows | 46 in the memo, 42 live, nearly disjoint |
| class-total keys | 7 in the memo, 6 live |
| advisory cells | 6 flagged but unmarked, 5 of them on `samples/4p1i` |

The four corroboration cells pass. They are `cf.COMMITTED_CORROBORATION_CELLS`
(`scripts/counterfactual_phase21.py:277-284`), re-pinned to baseline 9 by `948abae1`. The script
also refuses a disagreement itself (`_corroboration_pin_check`, `:4999-5037`). No committed test
plants a moved cell.

**Why retire, argued from the measured/frozen pair rule.** `3eebc7d5` re-stamped "only the half
that may move": a re-record re-derives the measured side of a pinned pair. The frozen side moves
only at a step that re-issues it.

Here the live run is the measured side, and the dated memo is the frozen side. No step re-issues
the memo:
- Phase 21 closed on VERDICT FINDING (`509e92ed`, #430).
- The memo's last amendment is `608ae1f6` (#427).
- `git log --first-parent --oneline 3eebc7d5..39a568c6 -- 'replays/samples/*/replay-seed-*.jsonl' 'replays/ml_corpus/*/replay-seed-*.jsonl'`
  prints nothing. The baseline-8 replay bytes the memo describes held unchanged on `main` from
  the record to `39a568c6`, the last `main` before the baseline-9 merge `acf6c604`.

A test that compares the two sides is therefore not a drift gate. It turns red at every re-record
and turns green at none.

**Why the Phase-20 precedent does not apply as it stands.** `efcd43b8` retired the Phase-20
comparison because the levers it priced had graduated. This script's own "FROZEN" refusal
(`scripts/counterfactual_phase21.py:4130-4153`) fires only when a lever is unregistered or
graduated. That trigger does not hold here: the three Wave-2 levers are still live toggles that
read OFF under an empty environment. That was checked writing this card:
`cf.WAVE_2_LEVERS` are all in `TOGGLEABLE_SUBSTRATE_FLAG_KEYS`, and `substrate_flag_snapshot({})`
reads all three False. Citing `efcd43b8` would claim a graduation that did not happen. Its shape
is still the model to follow: keep a "still carries its table" pin
(`tests/scripts/test_counterfactual_phase20.py:1-19`), and delete the comparison and its
perturbation cases.

**Why the fixture route is not taken.** `70e49468` freezes exhibits under
`tests/fixtures/baseline8_exhibits/`. Keeping this gate alive the same way would mean committing
the baseline-8 replay JSONL: 115,886,311 bytes in 300 files, or 233,746,908 with the tournament
reports (the decision memo, measured at `39a568c6`). Nothing reads those numbers any more.

**The gate passed at `39a568c6`.** The investigation ran the default tier on a `git archive` of
`39a568c6`. It had 15 failures, all archive artifacts ("not a git repository"), and neither test
is among them. This card re-confirms that in a real checkout before E.4 cites the commit.

**Why E.4, and not the zero-byte variant.** Without E.4, §10 and the Errata preamble would name an
enforcing mechanism that no longer exists (craft rule 5). The cost of E.4 is one `audits/` byte
change, which recomputes the registry row `docs/artifacts.md:109`: 26,632,967 tracked bytes in 329
files at `95fb894b`, measured writing this card. `inventory_problems`
(`scripts/verify_ml_evidence.py:2867-2901`) enforces that row through
`tests/scripts/test_verify_ml_evidence.py::test_every_counted_registry_row_matches_the_index`
(`:1906`), which passes at `95fb894b`.

**The module at `95fb894b`.** `tests/scripts/test_counterfactual_phase21.py` collects 112 tests.
Thirteen of those collected ids retire, from ten functions:
- the two memo comparisons: the drift gate at `:704-779` and the advisory-marks test at
  `:673-678`;
- the three errata-fold tests at `:557`, `:575` and `:583-608`, the last one parametrized four
  ways;
- the five perturbation cases at `:462`, `:533`, `:628`, `:644` and `:681`.

Once those ten functions go, these helpers have no caller left, as a `grep -w` count shows:
- `_published_tables`, `_split_errata`, `_published_render_census`, `_published_parses`;
- `_bump_last_number`, `_perturb_first_published_value`, `_strip_one_advisory_marker`;
- `_advisory_cells`, `_memo_advisory_cells`;
- `_memo_ballot_census`, `_census_value`, `_flatten_ballot_census`, `_BALLOT_CENSUS_LABELS`;
- `_memo_render_census`, `_flatten_render_census`, `_RENDER_LEGS`;
- `_memo_kind_census`, `_run_kind_census`, `_REPORTED_KINDS`, `_first_int`;
- `_memo_ledger_rows`, `_memo_tally`, `_run_ledger_rows`, `_LedgerRow`;
- `_memo_class_totals`, `_totals`, `_run_tables`, `_columns`, `_ERRATA_HEADING`.

These stay:
- `test_the_memo_table_parses_into_rows` (`:455`), which needs `_memo_tables`, `_parse_tables`,
  `_values` and `_value`;
- the three no-bar tests (`:404-436`, eight plants) and `_bar_language`;
- `_set_block`, `_rows`, `_PAIR` and `_CELL_ID`;
- every test that reads the live instrument.

## Acceptance

**Item 1: the report-tick fog** (one commit).

- [ ] **The loader re-opens a body reported on a game-deciding tick.**
  - The change is the investigation's probed shape, or an equivalent: after
    `api/replay_loader.py:1692`, add
    `elif state.phase == "GAME_OVER" and any(isinstance(event, MeetingTriggeredEvent) for event in events): _, body_id = _meeting_trigger_from_events(events)`.
  - `meeting_id` and `trigger_kind` stay `None`, matching the projection's no-chip rule.
  - An emergency trigger re-opens nothing.
  - The comment at `:1698-1701` and the docstring at `:2027` are corrected from "on its meeting
    frame" to "on its report frame, including a game-deciding report that convenes no meeting".
  - No task id is added to either.

  **Mechanism:** the fog test, parametrized as below.
  **Planted proof:** the new parametrized test is run against the unfixed loader (the base's
  `api/replay_loader.py`). It must fail on both sets, naming `headless-seed-13` tick 13 and
  `headless-seed-3` tick 10, and then go green with the fix. Results quotes both runs.

- [ ] **The test covers `samples/9p2i` and `samples/4p1i`, with a vacuity guard.**
  - The test is parametrized over the two sets. Each set's loader is built the way the existing
    `nine_p_two_i_loader` fixture builds it. That fixture stays for its other consumers.
  - Per set, the test asserts that at least one game-deciding report frame was exercised: a frame
    with a `report_body` event and no `meeting_triggered` event. If none was, it fails with a
    message naming the set.
  - The docstring says that a re-record which removes the shape turns this test red, and that the
    remedy is a frozen exhibit (the `70e49468` precedent), not a deleted guard.

  **Mechanism:** that guard assertion.
  **Planted proof:** a committed case feeds the guard a loader whose games hold no such frame, and
  requires the guard's `AssertionError`. For example, use the synthetic `meeting_loader` fixture,
  after confirming it holds none.

- [ ] **The served fog moves only at the three named frames.** Run the reporter-fog census before
  and after the fix, on all four sets. Also compare every served
  `(game, tick, agent, visible_bodies)` tuple across the two runs.
  - The misses read 1 -> 0 on `samples/9p2i`, `samples/4p1i` and `ml_corpus/4p1i`, and 0 -> 0 on
    `ml_corpus/9p2i`.
  - Every differing tuple lies on one of the three frames: `headless-seed-13` tick 13,
    `headless-seed-3` tick 10 and `headless-seed-1009` tick 7. That covers the reporter and any
    co-located living agent.
  - Results quotes the census scripts whole and gives the counts only.

  **Mechanism:** the census, with its command.
  **Perturbed proof:** the before run is the defect this census detects, at exactly those frames.
  An after run with any tuple outside them stops the card.

- [ ] **The demo bundle is measured before and after, and named first in the PR.**
  - Bake `data/` with the Validation command at the parent and at the fix commit, on one host.
  - Give both file counts, byte totals and tree digests, and `diff -r` the two trees.
  - The expected result is byte-identical. Whatever it reads, the PR's first line names the viewer
    change as a publication decision on merge and quotes that result.

  **Mechanism:** the digest command.
  **Perturbed proof:** bake `samples/9p2i` seed 13 alone (`games=(FeaturedGame("9p2i", 13),)`)
  before and after. Its tree must differ, which shows the diff would catch a featured frame that
  changed.

- [ ] **The firewall and derived views are unchanged.** All of these pass unchanged:
  - `tests/api` (including `test_leak.py` and its body clause at `:1125-1132`);
  - `tests/scripts/test_build_demo_bundle.py`;
  - `scripts/gen_frontend_types.py --check`;
  - `scripts/publish_process_scorecard.py --check`;
  - the four `scripts/build_sample_report.py --sample-dir <set> --check` runs.

  `git diff --stat` on the protected paths is empty (see Validation).

  **Mechanism:** those checks.
  **Proof:** the leak test's body clause fails any re-opened body in an unseen room. The census
  item above is the witness that the change is confined.

**Items 3 and 4: freezing the counterfactual memo** (one commit; both tests read the one memo,
and E.4 describes both).

- [ ] **The frozen side is confirmed before it is cited.** In a detached worktree at
  `39a568c6420531b7e22adcd5827fc18094594006`, in a bare shell with no `AILIBI_*` export, both
  retiring tests pass. The same command at `95fb894b` fails on both. Results quotes the counts
  only: "2 passed" and "2 failed".

  If they do not both pass at `39a568c6`, stop and report. E.4 then has no commit to cite, and
  searching further back is the orchestrator's call.

  **Mechanism:** pytest, with the two exact node ids.
  **Perturbed proof:** the pair itself. The same command at two SHAs reads opposite outcomes, so
  the pointer E.4 quotes is shown to discriminate.

- [ ] **The corroboration pins keep a test of their own.**
  - The new `@pytest.mark.slow` test `test_the_corroboration_cells_equal_the_committed_record`,
    over `full_run`, asserts `pins["checked"] is True` and all four cells against
    `cf.COMMITTED_CORROBORATION_CELLS`.
  - It uses one helper that takes the payload and the committed mapping.
  - Results maps every assertion of the deleted drift gate that did not read the memo to its new
    home. Nothing live is lost.

  **Mechanism:** that test.
  **Planted proof:** the helper fails in both of these committed cases:
  - it is fed the measured payload with one committed cell moved by one;
  - it is fed a payload whose `checked` is False.

- [ ] **The comparison and its coupled machinery are deleted (craft rule 3).**
  - Delete the ten functions and every helper that has no caller left (Evidence).
  - Confirm each helper is gone with a `grep -n -w` in the file, which must find nothing.
  - `ruff check` and `mypy` stay clean. Imports that are now unused go too.
  - The collected count reads 112 - 13 + the added tests, stated exactly.
  - The module docstring holds one history line per deleted test, 10 lines. Each line says what
    the test compared and that the memo froze (E.4). The line for the drift gate names where its
    corroboration half now lives.

  **Mechanism:** the grep, the collected count and ruff.
  **Planted proof:** compare two sets: the `def test_` names at `95fb894b` that are missing at the
  head, and the names in the history block. They must be equal. Dropping one history line in a
  scratch copy must make the comparison name that test.

- [ ] **The docstrings argue the retirement, not the old gate.**
  - Items 4 and 5 of the module docstring (`:15-25`), the banner for section 5 (`:400`) and the
    `full_run` docstring (`:278`) state the current pins.
  - They say the memo is the frozen baseline-8 record, argued from `3eebc7d5`'s pair rule and from
    "no step re-issues the memo".
  - They say why `efcd43b8` does not apply (its graduation trigger does not hold) and why the
    `70e49468` fixture route was not taken (its cost).

  **Mechanism:** every test the docstring names as a current pin is collected.
  **Planted proof:** renaming one of those tests in a scratch copy makes that check report it.

- [ ] **E.4 is appended, and nothing above it is rewritten.** `git diff --numstat` shows 0
  deletions for the memo. E.4 follows the pattern of E.3:
  - a dated `### E.4` heading;
  - "No figure in this memo moves";
  - the tables are the baseline-8 record, frozen;
  - from the commit that carries E.4, no test compares them with a live run;
  - the §10 introduction and the Errata preamble describe the mechanism as it stood through
    `39a568c6`.

  The reproduction pointer gives the full SHA `39a568c6420531b7e22adcd5827fc18094594006` as the
  last `main` whose recordings are the bytes these tables describe, and at which both
  comparisons passed. It also gives the exact commands: the two-node-id pytest run, and
  `uv run python scripts/counterfactual_phase21.py --sets all`, run in a bare shell in a checkout
  of that commit.

  E.4 carries no table row, no bar language and no task id. It names commits by SHA, as E.1-E.3
  do.

  **Mechanism:** the retained parse pin and the three no-bar tests, run over the amended memo.
  **Planted proof:** the eight no-bar plants still bite. The pointer's command reproduces, as the
  first item of this group shows.

- [ ] **Registry row 109 is recomputed last.**
  1. After the last `audits/` byte of the PR, stage the change.
  2. Recompute the row with the Validation one-liner, which counts `git ls-files` and sums sizes
     from disk. It reads 329 files, and 26,632,967 bytes plus the bytes E.4 adds, stated exactly.
  3. Touch only row 109.

  The offline verifier (`scripts/verify_ml_evidence.py`, never `--complete`) reads its in-tree
  family inventory row OK. Its FAIL rows are card A's ML rows only, and this card adds none.

  **Mechanism:** `test_every_counted_registry_row_matches_the_index`.
  **Planted proof:** in a scratch edit, leave the row at 26,632,967 after E.4; the registry test
  must go red. `test_availability_rejects_exact_byte_drift_without_count_change` stays green.

**The whole card.**

- [ ] **The three ids leave the red list, and no new id appears.**
  - Before the final gate, merge `main` into the branch. Merge; do not rebase.
  - Run `bash scripts/check.sh` whole, in a clean worktree. Card B merges before this card
    (the merge order under Constraints), so its failing ids must be a subset of the ids card A
    owns (the ML reds), or none once card A has merged.
  - Results lists the failing ids with their owners.

  **Mechanism:** `check.sh`, which runs `-n auto --dist loadfile` and the frontend legs.
  **Proof:** at `95fb894b` it failed on 50 ids, these three among them. By pytest outcome they
  are 41 failed plus 9 errors, the 9 errors all card A's; by owner they are card A's 41 ML ids,
  card B's six and these three.

## Constraints

**Spend and inputs.**
- The spend is `$0`: no provider, no model call, no recorder, no `.env`.
- The verifier runs offline, never `--complete`.
- The commands run in a bare shell with no `AILIBI_*` export; the counterfactual script refuses
  under one.

**The freeze.** None of these change, and none are read differently:
- `engine/`, `agents/` (the prompt set included), `meetings/`, `observation/`, `orchestrator/`;
- `eval/`, `training/`, `frontend/`, `replays/`;
- `scripts/`, including `scripts/counterfactual_phase21.py`, whose FROZEN refusal text stays.

The fog is a spectator-only DTO. The card pushes no agent toward any answer, and no agent input
changes. Role-correctness gates nothing.

**What is not rewritten.** Nothing re-derives, rewrites or re-cites the memo's figures, E.1-E.3,
or the dated records that name the retired ids:
- `audits/audit-2026-09-22-process-rerecord.md:1158`;
- `tasks/work/process-rerecord.md:1402-1403`;
- `tasks/phase-21.md`.

A baseline-9 counterfactual table would be a new dated memo, which nobody has asked for.

**One writer per file across the three baseline-9 cards.**
- **Card A** (`tasks/work/ml-reground-baseline-9.md`) owns:
  - `training/` (the four training reports included) and `tests/training/`;
  - `tests/scripts/test_verify_ml_evidence.py`, which this card only runs;
  - `tests/eval/test_balance_eval_meeting_runner.py` and
    `tests/experiments/test_torch_probe_excluded.py`;
  - `docs/artifacts.md` rows 103-104, `training/README.md`, `docs/ml-program.md`,
    `replays/ml_corpus/README.md` and the `docs/glossary.md` lines its new prose needs;
  - `scripts/verify_ml_evidence.py`, only when a constraint pin moves.
- **Card B** (`tasks/work/committed-channel-rederivation.md`) owns:
  - `tests/_helpers/committed.py` and `tests/_helpers/test_committed_single_home.py`;
  - `tests/meetings/test_contradictions.py` and `tests/meetings/test_transcript.py`;
  - `tests/eval/test_evidence_honesty.py` and `tests/agents/test_reported_testimony.py`;
  - the docstring span `eval/evidence_honesty.py:2295-2297`.
- **This card** owns:
  - `api/replay_loader.py` and `tests/api/test_view_model.py`;
  - `tests/scripts/test_counterfactual_phase21.py`;
  - `audits/audit-phase-21-counterfactual.md`;
  - `docs/artifacts.md` row 109.

**Status and the task index.** `tasks/README.md` is the orchestrator's.
`scripts/validate_task_docs.py` derives its inventory sentence from every card's
`**Status:**`, so any Status flip here would redden `check.sh`. The worker therefore fills
Results and leaves the Status line to the orchestrator, who flips it together with the
sentence in one commit.

**`docs/artifacts.md` has two writers:** this card writes row 109, and card A writes rows 103-104.
Whichever PR merges second merges `main` first, recomputes its own rows if they moved, and
re-runs `test_every_counted_registry_row_matches_the_index` before merging.

**Merge order and done (identical in the three baseline-9 cards).** Card A is
`tasks/work/ml-reground-baseline-9.md`, card B is `tasks/work/committed-channel-rederivation.md`
and card C is `tasks/work/report-fog-and-counterfactual-freeze.md`. Merge order: B, then C,
then A last, after merging `main` into its branch. If A is ready first, it may merge first.
Whichever pull request merges last merges `main` into its branch first and shows
`bash scripts/check.sh` fully green on `main`. A card is done when every acceptance item has
evidence and every id still failing at its gate belongs to one of the other two cards.

This card is card C. The last-merge rule is the Q5 consequence the decision memo draws.

**Stop and report, with the partial output,** if any of these happens:
- the two tests do not both pass at `39a568c6`;
- the fog diff reaches a frame outside the three named ones;
- a recorded, generated or derived byte moves;
- `check.sh` shows an id that no card owns.

## Expected scope

**Code.** Only `api/replay_loader.py`:
- the `elif` after `:1692`;
- the comment at `:1698-1701`;
- the docstring at `:2027-2036`.

**Tests.**
- `tests/api/test_view_model.py`: the parametrized fog test, its vacuity guard and the guard's
  planted case. The test's unused `monkeypatch` parameter goes if nothing then reads it.
- `tests/scripts/test_counterfactual_phase21.py`:
  - the new corroboration test and its two planted cases;
  - the deletions;
  - the docstrings and the section-5 banner;
  - the history block.

**Documents.**
- `audits/audit-phase-21-counterfactual.md`: E.4 appended, and nothing else.
- `docs/artifacts.md`: row 109 only.
- This card's Results.

**Out of scope.** Nothing else, including:
- every file the Constraints freeze;
- `audits/README.md`;
- `tests/fixtures/`;
- the `AILIBI_EVIDENCE_QUALITY_LIFT` export in the existing fixture. At `95fb894b`, `git grep -n EVIDENCE_QUALITY_LIFT -- '*.py'` finds it read only under `tests/`, and cleaning it up is not this card's job.

**Delivery.**
- The branch is `work/report-fog-and-counterfactual-freeze`.
- One pull request goes into `main`, merged or fast-forwarded and never squashed. It populates
  every section of `.github/pull_request_template.md`.
- Each commit body carries `Card: tasks/work/report-fog-and-counterfactual-freeze.md`.

**Commits, one per item.**
1. Item 1: the loader fix and its tests.
2. Items 3 and 4: the retirement, E.4 and the row-109 recompute. The recompute is computed after
   the commit's last `audits/` byte is final.
3. The Results commit.

If a review round touches `audits/` again, recompute row 109 again, last.

## Record impact

**Item 1 is a viewer repair, not an experiment, so adoption is not applicable.**
- *What changes:* the served `/replays/{id}` payload's `visibility.visible_bodies`, on the final
  frame of `samples/9p2i` `headless-seed-13` (tick 13), `samples/4p1i` `headless-seed-3` (tick 10)
  and, for a loader pointed at it, `ml_corpus/4p1i` `headless-seed-1009` (tick 7). The body
  re-appears for the reporter and for any co-located living agent.
- *What does not change:* no recorded byte, state hash, action disposition, golden fixture,
  generated frontend type, eval figure, scorecard row or derived view.
- *Agents:* they read engine packets, so no agent input and no prompt byte moves.
- *Publication:* the Pages rebuild on merge re-walks the featured games through the changed
  loader. None of the three games is featured, so the baked data is expected to be byte-identical.
  The PR names the change first anyway, with the measured bundle result, because `AGENTS.md`
  treats a viewer change as a publication decision.
- *Future games:* a future game decided on a report tick is served with the body in view. A game
  decided on an emergency trigger re-opens nothing, which is correct.

**Items 3 and 4 are a test retirement plus one provenance erratum.**
- *What changes:* one `audits/` file grows by the E.4 bytes. Registry row 109's byte total moves;
  its count of 329 files does not.
- *What does not change:* no figure in the memo, no instrument output and no committed pin.
- *What the live instrument keeps:* its corroboration pins (now planted), the baseline-9 tripwire
  readings, OFF-equals-record, the refusals and the planted reader cases.
- *What it loses:* the memo's whole-run comparison. From now on, drift in the instrument's
  output is caught only by the retained readings. The deleted fold machinery stays reachable in
  git history.
- *Earlier verdicts:* E.1-E.3 and the Phase 21 verdict stand unchanged.

## Validation

```
# item 1 (SCRATCH is a scratch directory outside the tree)
uv run pytest -q "tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body"   # red on the base loader, green after
uv run pytest -q tests/api tests/scripts/test_build_demo_bundle.py
uv run python scripts/gen_frontend_types.py --check
uv run python scripts/publish_process_scorecard.py --check
for s in replays/samples/9p2i replays/samples/4p1i replays/ml_corpus/9p2i replays/ml_corpus/4p1i; do uv run python scripts/build_sample_report.py --sample-dir "$s" --check; done
uv run python -c "import sys; sys.path.insert(0, 'scripts'); from pathlib import Path; import build_demo_bundle as b; print(b.bake_data(Path('$SCRATCH/bundle-before'), games=b.parse_featured_games()))"   # and bundle-after at the fix commit
uv run python -c "import hashlib; from pathlib import Path; r=Path('$SCRATCH/bundle-before/data'); fs=sorted(p for p in r.rglob('*') if p.is_file()); h=hashlib.sha256(); [h.update(str(p.relative_to(r)).encode()+b'\0'+hashlib.sha256(p.read_bytes()).hexdigest().encode()+b'\n') for p in fs]; print(len(fs), sum(p.stat().st_size for p in fs), h.hexdigest())"
diff -r "$SCRATCH/bundle-before/data" "$SCRATCH/bundle-after/data"
# items 3 and 4: the frozen side, count-only
git worktree add --detach "$SCRATCH/b8" 39a568c6420531b7e22adcd5827fc18094594006
(cd "$SCRATCH/b8" && uv sync --frozen && uv run pytest -q "tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run" "tests/scripts/test_counterfactual_phase21.py::test_the_memo_marks_every_advisory_cell")   # 2 passed; the same at 95fb894b: 2 failed
git worktree remove "$SCRATCH/b8"
uv run pytest -q tests/scripts/test_counterfactual_phase21.py
uv run pytest --collect-only -q tests/scripts/test_counterfactual_phase21.py | tail -1   # 112 at 95fb894b
git diff --numstat 95fb894b -- audits/audit-phase-21-counterfactual.md   # "<added> 0"
uv run python -c "import subprocess; from pathlib import Path; fs=subprocess.run(['git','ls-files','-z','audits'],capture_output=True,check=True).stdout.decode().split(chr(0))[:-1]; print(sum(Path(f).stat().st_size for f in fs), len(fs))"   # 26632967 329 at 95fb894b
uv run pytest -q "tests/scripts/test_verify_ml_evidence.py::test_every_counted_registry_row_matches_the_index" "tests/scripts/test_verify_ml_evidence.py::test_availability_rejects_exact_byte_drift_without_count_change"
uv run python scripts/verify_ml_evidence.py   # offline; in-tree family inventory OK
# the whole card
uv run python scripts/check_doc_facts.py && uv run python scripts/validate_task_docs.py
bash scripts/check.sh   # whole, clean worktree, after merging main
git diff --stat $(git merge-base origin/main HEAD) HEAD -- engine agents meetings observation orchestrator eval training frontend replays scripts   # empty
```

Results quotes these, whole:
- the two census scripts: the JSONL walk for game-deciding report ticks, and the `ReplayLoader`
  walk for the reporter's fog and the full-tuple diff;
- the history-line set comparison;
- each planted and perturbed run.

Each quoted figure is given with the host stamp (`uname -srm`) where it could depend on the
platform.

## Results

Not started.
