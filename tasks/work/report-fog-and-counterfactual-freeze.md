# Keep the reported body in view on a game-deciding tick, and freeze the Phase-21 counterfactual memo

**Status:** done

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

- [x] Review correction: the delivery state is Implemented, not Verified. The acceptance checks
  pass and the scoped gate holds (the red set at the head is main's minus this card's three ids),
  but `bash scripts/check.sh` exits 1 on card A's 41 ids and card B's 6, and `docs/workflow.md`
  defines Verified as the acceptance checks and the combined project gate passing. Proved by
  `bash scripts/check.sh` at the head, with its exit code captured directly, and the `comm` of the
  head's and main's red sets (Results, review corrections round 1).
- [x] Review correction: the demo-bundle tree digest is per-checkout, not a pin. It folds each baked
  replay's `created_at`, which the loader reads from the replay file's mtime
  (`api/replay_loader.py:2481`, `created_at=_iso_mtime(path)`), so two checkouts of one commit bake
  two digests on one host. The evidence is the file counts, the byte totals, a same-checkout
  `diff -r`, and a digest with every `created_at` value blanked that reads the same in two
  checkouts. Proved by `bake.py` and `digest.py` in two checkouts, and by `strip_diff.py`, which
  finds that the 9 files differing between the checkouts differ only in `created_at` (Results, the
  demo bundle).

**Item 1: the report-tick fog** (one commit).

- [x] **The loader re-opens a body reported on a game-deciding tick.**
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

- [x] **The test covers `samples/9p2i` and `samples/4p1i`, with a vacuity guard.**
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

- [x] **The served fog moves only at the three named frames.** Run the reporter-fog census before
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

- [x] **The demo bundle is measured before and after, and named first in the PR.**
  - Bake `data/` with the Validation command at the parent and at the fix commit, on one host.
  - Give both file counts, byte totals and tree digests, and `diff -r` the two trees.
  - The expected result is byte-identical. Whatever it reads, the PR's first line names the viewer
    change as a publication decision on merge and quotes that result.

  **Mechanism:** the digest command.
  **Perturbed proof:** bake `samples/9p2i` seed 13 alone (`games=(FeaturedGame("9p2i", 13),)`)
  before and after. Its tree must differ, which shows the diff would catch a featured frame that
  changed.

- [x] **The firewall and derived views are unchanged.** All of these pass unchanged:
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

- [x] **The frozen side is confirmed before it is cited.** In a detached worktree at
  `39a568c6420531b7e22adcd5827fc18094594006`, in a bare shell with no `AILIBI_*` export, both
  retiring tests pass. The same command at `95fb894b` fails on both. Results quotes the counts
  only: "2 passed" and "2 failed".

  If they do not both pass at `39a568c6`, stop and report. E.4 then has no commit to cite, and
  searching further back is the orchestrator's call.

  **Mechanism:** pytest, with the two exact node ids.
  **Perturbed proof:** the pair itself. The same command at two SHAs reads opposite outcomes, so
  the pointer E.4 quotes is shown to discriminate.

- [x] **The corroboration pins keep a test of their own.**
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

- [x] **The comparison and its coupled machinery are deleted (craft rule 3).**
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

- [x] **The docstrings argue the retirement, not the old gate.**
  - Items 4 and 5 of the module docstring (`:15-25`), the banner for section 5 (`:400`) and the
    `full_run` docstring (`:278`) state the current pins.
  - They say the memo is the frozen baseline-8 record, argued from `3eebc7d5`'s pair rule and from
    "no step re-issues the memo".
  - They say why `efcd43b8` does not apply (its graduation trigger does not hold) and why the
    `70e49468` fixture route was not taken (its cost).

  **Mechanism:** every test the docstring names as a current pin is collected.
  **Planted proof:** renaming one of those tests in a scratch copy makes that check report it.

- [x] **E.4 is appended, and nothing above it is rewritten.** `git diff --numstat` shows 0
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

- [x] **Registry row 109 is recomputed last.**
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

- [x] **The three ids leave the red list, and no new id appears.**
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

**Implemented on the branch `work/report-fog-and-counterfactual-freeze`, not merged.** Delivery
states (`docs/workflow.md`):
- Implemented: `1bd2180f` (item 1), `31b0a82b` (items 3 and 4), the Results commit `869526ac` and
  the round-1 review-correction commit.
- Verified: **no.** Every acceptance check below passes, and the scoped gate holds: the red set at
  the head is main's minus this card's three ids. But `docs/workflow.md` defines Verified as the
  acceptance checks *and* the combined project gate passing, and `bash scripts/check.sh` exits 1
  here on card A's 41 ids and card B's 6 (the gate section below).
- Independently reviewed: round 1 returned two blocking findings, both repaired (Review
  corrections, round 1, below); a re-review is pending.
- Owner reviewed and Merged: not yet.
- Adopted: not applicable (a viewer repair and a test retirement, no experimental behaviour).

The Status line stays `ready` for the orchestrator to flip with the task-index sentence.

Host for every figure below: `Darwin 24.6.0 arm64`, a bare shell with no `AILIBI_*` export
(`env | grep -c '^AILIBI_'` prints `0`). Base: `main` at `ff4c6bb8`, whose code, tests and
recordings are byte-identical to `95fb894b` (`git diff --stat 95fb894b ff4c6bb8` touches only
`tasks/`). Commands ran as `.venv/bin/python` / `.venv/bin/pytest` from a `uv sync --frozen`
environment, the same interpreter `uv run` selects. Scratch scripts lived outside the tree.

### Architecture and design references

- `docs/architecture.md` §Packages: `api/` is the privileged post-game reader and the only consumer
  of the served fog (`AgentVisibilityView`); agents, memory, eval and ML read engine packets, so no
  agent input moves. The frontend consumes generated types; no DTO shape changed
  (`gen_frontend_types.py --check` exits 0).
- `docs/architecture.md` §Enforced boundaries: the leak test's body clause
  (`tests/api/test_leak.py:1125-1132`, a visible body's room is always one the observer has seen)
  passes unchanged over the re-opened frames.
- `docs/architecture.md` §Determinism and the substrate ladder: the three Wave-2 levers are still
  live toggles, default-OFF, which is why the `efcd43b8` graduation trigger does not hold for the
  memo; no recorded byte moved (`verify_samples.sh` 100 of 100 clean).
- The measured/frozen pair rule of `3eebc7d5`, the phase close `509e92ed`, the memo's last
  amendment `608ae1f6` and the `70e49468` frozen-exhibit precedent are cited as the card argues
  them, in the module docstring and in E.4.

### Item 1: the report-tick fog (`1bd2180f`)

**The change.** `api/replay_loader.py` gains the investigation's `elif state.phase == "GAME_OVER"
and any(isinstance(event, MeetingTriggeredEvent) ...)` branch after the MEETING branch, taking
only the body from `_meeting_trigger_from_events`; `meeting_id` and `trigger_kind` stay `None`. An
emergency trigger returns no body, so it re-opens nothing. The comment and the
`_agent_visibility_map` docstring now say "on its report frame, including a game-deciding report
that convenes no meeting"; the comment's closing clause reads "an emergency trigger" instead of
"an emergency meeting", because the `None` now also covers an emergency trigger on a
game-deciding tick. No task id was added.

**The JSONL census of game-deciding report ticks** (count-only, at the head; the recordings are
unchanged from the base):

```python
"""Count-only census of game-deciding report ticks over the replay JSONL.

A game qualifies when its last ``tick`` row holds an applied ``report``, its
``game_over`` row carries that same tick, and no ``meeting`` row carries it.
Prints one count per set and, per qualifying game, only the seed, the tick,
the reporter, the body's player and the game-over reason.
"""

import json
import re
import sys
from pathlib import Path

SETS = ("samples/9p2i", "samples/4p1i", "ml_corpus/9p2i", "ml_corpus/4p1i")
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")


def seed_of(path: Path) -> int:
    match = re.fullmatch(r"replay-seed-(\d+)\.jsonl", path.name)
    assert match is not None, path.name
    return int(match.group(1))


for set_name in SETS:
    hits = []
    games = sorted((root / "replays" / set_name).glob("replay-seed-*.jsonl"), key=seed_of)
    for path in games:
        rows = [json.loads(line) for line in path.read_text().splitlines() if line]
        ticks = [row for row in rows if row["kind"] == "tick"]
        overs = [row for row in rows if row["kind"] == "game_over"]
        if not ticks or len(overs) != 1:
            continue
        last = ticks[-1]
        reports = [
            action
            for action, disposition in zip(
                last["actions"], last["action_dispositions"], strict=True
            )
            if action["type"] == "report" and disposition == "applied"
        ]
        meeting_ticks = {row["tick"] for row in rows if row["kind"] == "meeting"}
        if reports and overs[0]["tick"] == last["tick"] and last["tick"] not in meeting_ticks:
            assert len(reports) == 1, path.name
            body = reports[0]["payload"]["body_id"]
            victim = re.fullmatch(r"body-(p-\d+)-\d+", body)
            assert victim is not None, body
            hits.append(
                (seed_of(path), last["tick"], reports[0]["actor"], victim.group(1), overs[0]["reason"])
            )
    print(f"{set_name}: games={len(games)} game_deciding_report_ticks={len(hits)}")
    for seed, tick, reporter, victim, reason in hits:
        print(f"  headless-seed-{seed}: tick {tick}, reporter {reporter}, body {victim}, {reason}")
```

```
samples/9p2i: games=50 game_deciding_report_ticks=1
  headless-seed-13: tick 13, reporter p-9, body p-3, IMPOSTOR_PARITY
samples/4p1i: games=50 game_deciding_report_ticks=1
  headless-seed-3: tick 10, reporter p-2, body p-3, CREWMATE_TASKS
ml_corpus/9p2i: games=150 game_deciding_report_ticks=0
ml_corpus/4p1i: games=50 game_deciding_report_ticks=1
  headless-seed-1009: tick 7, reporter p-4, body p-2, CREWMATE_TASKS
```

This re-measures the card's baseline-9 column exactly.

**The reporter-fog census and the full-tuple diff** (count-only, through `ReplayLoader`):

```python
"""Count-only census of the reporter's served fog, through ``ReplayLoader``.

For every ``report_body`` event the loader serves, count the reporters whose
``visibility.visible_bodies`` lacks the body they reported. Every served
``(game, tick, agent, visible_bodies)`` tuple is written to ``OUT`` (one JSON
file per run, scratch only) for the before/after diff; stdout carries counts
and the ``(game, tick)`` of each miss only.

usage: python census_fog.py <repo-root> <out.json>
"""

import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2])
sys.path.insert(0, str(root))

from api.replay_loader import ReplayLoader  # noqa: E402

SETS = ("samples/9p2i", "samples/4p1i", "ml_corpus/9p2i", "ml_corpus/4p1i")
tuples: dict[str, list[list[object]]] = {}
for set_name in SETS:
    loader = ReplayLoader(replay_dir=root / "replays" / set_name)
    reports = 0
    misses: list[tuple[str, int]] = []
    served: list[list[object]] = []
    for meta in loader.list_replays():
        replay = loader.load_replay(meta.game_id)
        for tick in replay.ticks:
            for agent in tick.agent_states:
                if agent.visibility is None:
                    continue
                served.append(
                    [
                        meta.game_id,
                        tick.tick,
                        agent.agent_id,
                        sorted(
                            [body.id, body.room, body.victim_id]
                            for body in agent.visibility.visible_bodies
                        ),
                    ]
                )
            for event in tick.events:
                if event.type != "report_body":
                    continue
                reports += 1
                reporter = next(
                    a for a in tick.agent_states if a.agent_id == event.reporter_id
                )
                assert reporter.visibility is not None
                seen = {body.victim_id for body in reporter.visibility.visible_bodies}
                if event.body_of not in seen:
                    misses.append((meta.game_id, tick.tick))
    tuples[set_name] = served
    print(
        f"{set_name}: report_body={reports} reporters_missing_own_body={len(misses)} "
        f"served_tuples={len(served)}"
    )
    for game_id, tick_no in misses:
        print(f"  miss: {game_id} tick {tick_no}")
out.write_text(json.dumps(tuples, sort_keys=True), encoding="utf-8")
```

```python
"""Compare every served (game, tick, agent, visible_bodies) tuple across two runs.

Prints, per set, the tuple counts, the number of differing tuples, and the
distinct (game, tick) frames they lie on with the agents that moved. Stops
(exit 1) if a differing tuple lies outside the three named frames.
"""

import json
import sys
from pathlib import Path

ALLOWED = {
    ("samples/9p2i", "headless-seed-13", 13),
    ("samples/4p1i", "headless-seed-3", 10),
    ("ml_corpus/4p1i", "headless-seed-1009", 7),
}
before = json.loads(Path(sys.argv[1]).read_text())
after = json.loads(Path(sys.argv[2]).read_text())
assert before.keys() == after.keys()
outside = 0
for set_name in before:
    b = {(g, t, a): bodies for g, t, a, bodies in before[set_name]}
    a_ = {(g, t, a): bodies for g, t, a, bodies in after[set_name]}
    assert b.keys() == a_.keys(), set_name
    moved = sorted(key for key in b if b[key] != a_[key])
    frames: dict[tuple[str, int], list[str]] = {}
    for game, tick, agent in moved:
        frames.setdefault((game, tick), []).append(agent)
    print(f"{set_name}: tuples={len(b)} differing={len(moved)} frames={len(frames)}")
    for (game, tick), agents in sorted(frames.items()):
        where = (set_name, game, tick)
        flag = "" if where in ALLOWED else "  <-- OUTSIDE THE NAMED FRAMES"
        if flag:
            outside += 1
        print(f"  {game} tick {tick}: agents {agents}{flag}")
print(f"frames outside the named three: {outside}")
sys.exit(1 if outside else 0)
```

Before (base loader) and after (`1bd2180f`'s loader):

| set | `report_body` events | misses before | misses after | served tuples | differing tuples | frames |
|---|---|---|---|---|---|---|
| `samples/9p2i` | 136 | 1 (`headless-seed-13` tick 13) | 0 | 7,915 | 3 (p-4, p-5, p-9) | 1 |
| `samples/4p1i` | 37 | 1 (`headless-seed-3` tick 10) | 0 | 2,109 | 2 (p-2, p-4) | 1 |
| `ml_corpus/9p2i` | 416 | 0 | 0 | 25,415 | 0 | 0 |
| `ml_corpus/4p1i` | 37 | 1 (`headless-seed-1009` tick 7) | 0 | 2,037 | 2 (p-3, p-4) | 1 |

`fog_diff.py` printed `frames outside the named three: 0` and exited 0: all seven moved tuples lie
on the three named frames (the reporter plus co-located living agents). The before run is the
defect the census detects, at exactly those frames.

**Planted proof (the unfixed loader).** With the base `api/replay_loader.py` restored over the
fix and the new tests in place:

```
FAILED tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body[9p2i]
  AssertionError: p-9 does not see the body it reported (p-3) at tick 13 of headless-seed-13
FAILED tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body[4p1i]
  AssertionError: p-2 does not see the body it reported (p-3) at tick 10 of headless-seed-3
PASSED tests/api/test_view_model.py::test_the_game_deciding_report_guard_fails_on_a_set_without_one
2 failed, 1 passed
```

With the fix restored: `3 passed`.

**The vacuity guard.** The test is parametrized over `samples/9p2i` and `samples/4p1i` by a
`report_tick_sample` fixture. Both it and the kept `nine_p_two_i_loader` fixture build their loader
through one `_committed_sample_loader(set_dir, monkeypatch)` helper, which is the old fixture's body
moved, so the two are built identically. The pre-existing `AILIBI_EVIDENCE_QUALITY_LIFT` export
stays in that one place, uncleaned, as Expected scope says. The test's unused `monkeypatch`
parameter is gone. `_assert_reporters_keep_their_bodies` counts both report-frame shapes:
- `report_body` beside `meeting_triggered`, which keeps the old "at least one body-report meeting"
  assertion, now per set;
- `report_body` alone, the game-deciding shape. The new guard fails with "no game in <set> is
  decided on a body-report frame ... pin it with a frozen exhibit".

The docstring names the `70e49468` frozen-exhibit remedy. The committed planted case
`test_the_game_deciding_report_guard_fails_on_a_set_without_one` feeds the guard the synthetic
`meeting_loader`. That loader holds one body report that convenes a meeting and a parity win
decided by a kill, so the reporter check and the meeting-frame guard pass. `pytest.raises(...,
match="no game in synthetic is decided")` then confirms the loader holds no game-deciding frame
and that only this guard fires. Neutralizing the guard in a scratch edit (`> 0` to `>= 0`) turned
that case red with `Failed: DID NOT RAISE <class 'AssertionError'>`, and restoring it made the case
green again.

**The demo bundle** (bake with the card's Validation one-liner, as `bake.py`; digest with its
one-liner plus a second, `created_at`-blanked digest, as `digest.py`; compare two trees with
`strip_diff.py`).

The raw tree digest is **per-checkout, not a pin**:
- It folds each baked replay's `metadata.created_at` and each `replays.json` row's `created_at`.
- The loader sets that field from the replay file's mtime (`api/replay_loader.py:2481`,
  `created_at=_iso_mtime(path)`).
- A fresh checkout of one commit writes new mtimes, so it bakes a different raw digest on the
  same host.

The evidence is therefore:
- the file counts and the byte totals;
- a `diff -r` of the before and after bakes made in one checkout;
- a second digest with every `created_at` value blanked, which reads the same in two checkouts.

```python
"""Bake the demo bundle's data/ tree offline (the card's Validation command).

usage: python bake.py <repo-root> <out-dir> featured|seed13
``featured`` bakes the committed featured list; ``seed13`` bakes samples/9p2i
seed 13 alone (the perturbed proof).
"""

import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2])
mode = sys.argv[3]
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "scripts"))

import build_demo_bundle as b  # noqa: E402

if mode == "featured":
    games = b.parse_featured_games()
elif mode == "seed13":
    games = (b.FeaturedGame("9p2i", 13),)
else:
    raise SystemExit(f"unknown mode {mode}")
summary = b.bake_data(out, games=games)
print("games:", summary.games)
print("files:", summary.files, "bytes_written:", summary.bytes_written)
```

```python
"""The card's tree digest, plus the same digest with every created_at value blanked.

usage: python digest.py <data-dir>

``created_at`` is the replay file's mtime (``api/replay_loader.py`` sets it from
``_iso_mtime(path)``), so it differs between two checkouts of the same commit.
The second digest replaces the value of each ``"created_at":`` (or
``"created_at": ``) key with ``null`` before hashing; every other byte is hashed
as written. Prints: files, bytes, raw digest, created_at values blanked, and the
created_at-blanked digest.
"""

import hashlib
import re
import sys
from pathlib import Path

CREATED_AT = re.compile(rb'("created_at": ?)(?:"[^"]*"|null)')

r = Path(sys.argv[1])
fs = sorted(p for p in r.rglob("*") if p.is_file())
raw = hashlib.sha256()
blanked = hashlib.sha256()
hits = 0
for p in fs:
    data = p.read_bytes()
    name = str(p.relative_to(r)).encode() + b"\0"
    raw.update(name + hashlib.sha256(data).hexdigest().encode() + b"\n")
    stripped, n = CREATED_AT.subn(rb"\1null", data)
    hits += n
    blanked.update(name + hashlib.sha256(stripped).hexdigest().encode() + b"\n")
print(
    len(fs),
    sum(p.stat().st_size for p in fs),
    raw.hexdigest(),
    hits,
    blanked.hexdigest(),
)
```

```python
"""Name the files that differ between two data/ trees, raw and with created_at blanked.

usage: python strip_diff.py <data-a> <data-b>
Prints the count of files present in only one tree, the count of files whose raw
bytes differ, and the files that still differ once every created_at value is
blanked (the substitution digest.py makes). Exit 1 if any file differs after
blanking or the file sets differ.
"""

import re
import sys
from pathlib import Path

CREATED_AT = re.compile(rb'("created_at": ?)(?:"[^"]*"|null)')


def blank(data: bytes) -> bytes:
    return CREATED_AT.sub(rb"\1null", data)


a = Path(sys.argv[1])
b = Path(sys.argv[2])
fa = {str(p.relative_to(a)) for p in a.rglob("*") if p.is_file()}
fb = {str(p.relative_to(b)) for p in b.rglob("*") if p.is_file()}
only = sorted(fa ^ fb)
raw_diff = []
blank_diff = []
for name in sorted(fa & fb):
    da = (a / name).read_bytes()
    db = (b / name).read_bytes()
    if da != db:
        raw_diff.append(name)
        if blank(da) != blank(db):
            blank_diff.append(name)
print(f"in one tree only: {len(only)}")
print(f"raw differing files: {len(raw_diff)}")
print(f"differing once created_at is blanked: {len(blank_diff)}")
for name in blank_diff:
    print(f"  {name}")
sys.exit(1 if only or blank_diff else 0)
```

**Where and how it was measured** (round 1, 2026-09-23, `Darwin 24.6.0 arm64`), in two checkouts:
- **Checkout 1:** this worktree at `869526ac`.
- **Checkout 2:** a fresh detached scratch worktree at `ff4c6bb8`, removed afterwards.

In each checkout the base loader (`ff4c6bb8:api/replay_loader.py`, which is `1bd2180f^`'s) and the
fixed loader (`1bd2180f`'s, byte-identical at `869526ac`) were written in turn over the checkout's
own `api/replay_loader.py` for a bake, and restored after it. No replay byte or mtime was touched.
The raw digest is given in full once, because it is not a pin.

| bake | checkout | files | bytes | raw digest (per-checkout) | `created_at` values | blanked digest |
|---|---|---|---|---|---|---|
| featured list, base loader | 1 | 156 | 4,808,974 | `015546b7…` | 14 | `dc2fcae1…` |
| featured list, fixed loader | 1 | 156 | 4,808,974 | `015546b7…` | 14 | `dc2fcae1…` |
| featured list, base loader | 2 | 156 | 4,808,974 | `3ebdb092…` | 14 | `dc2fcae1…` |
| featured list, fixed loader | 2 | 156 | 4,808,974 | `3ebdb092…` | 14 | `dc2fcae1…` |
| perturbed: `FeaturedGame("9p2i", 13)` alone, base loader | 1 | 16 | 389,688 | `d1c30b2e…` | 2 | `2e95cbbb…` |
| perturbed: `FeaturedGame("9p2i", 13)` alone, fixed loader | 1 | 16 | 389,857 | `f03c7b2d…` | 2 | `45146872…` |
| perturbed: `FeaturedGame("9p2i", 13)` alone, base loader | 2 | 16 | 389,688 | `24d165e2…` | 2 | `2e95cbbb…` |
| perturbed: `FeaturedGame("9p2i", 13)` alone, fixed loader | 2 | 16 | 389,857 | `d091e4c4…` | 2 | `45146872…` |

The full blanked digests:
- featured list, both loaders, both checkouts:
  `dc2fcae1df296338bbf54bbf042f3b0fb4a9e35d9bdf49f2bee6a88cbf7aeb66`;
- seed 13 alone, base loader: `2e95cbbb59b17a191d06abc5fa1c0fbdb345af893754a04043e19cb2e4ca5457`;
- seed 13 alone, fixed loader: `451468727f8ca2927e43982a14b70f39cc6286a7e1bd1b5e624a41599c6b3c3c`.

What the measurements show:
- **Same checkout, before and after.** In each checkout, `diff -r` of the base-loader and
  fixed-loader featured trees printed nothing and exited 0. **The featured bake is byte-identical
  before and after the fix**, in both checkouts.
- **Across checkouts, the raw digest moves on `created_at` alone.** `strip_diff.py` over the two
  checkouts' featured trees (fixed loader, and again for the base loader) printed:
  - `in one tree only: 0`;
  - `raw differing files: 9`;
  - `differing once created_at is blanked: 0`;
  - exit 0.

  The 9 files are exactly the 9 that carry `created_at`: the seven featured replays
  (`<set>/replays/headless-seed-<n>.json`) and the two `replays.json` listings.
- **The perturbed proof.** In checkout 1, `diff -rq` of the two seed-13 trees exited 1 and named
  exactly one file, `9p2i/replays/headless-seed-13.json` (+169 bytes). `strip_diff.py` names the
  same file after blanking, in both checkouts, and the blanked digests differ (`2e95cbbb…` vs
  `45146872…`) identically in both. So both the same-checkout diff and the blanked digest would
  catch a featured frame that changed.
- **The earlier digests were other checkouts' raw digests.** Round 0's `d8e619ea…` (featured) and
  `68928ac5…` / `db7e0e78…` (seed 13) are withdrawn as figures, and so is its explanation that the
  card's `37afc888dd22ecc4…` failed "on this host". Each of those was a raw digest read in another
  checkout, and they differ from these for the same reason. Neither is a host effect, and none of
  them is a pin. The card's file count and byte total do reproduce.
- **The Pages rebuild.** It bakes in a fresh `actions/checkout` of each push
  (`.github/workflows/pages.yml:46`, `:77`), so its served `created_at` values are its own
  checkout's and move on every rebuild, whether or not this card merges. The same-checkout
  comparison above shows that this card changes no byte of the featured payload.

**Firewall and derived views, unchanged:**
- `pytest -n auto tests/api tests/scripts/test_build_demo_bundle.py`: `476 passed, 2 skipped` (the
  investigation's 474 plus this card's two new ids);
- `gen_frontend_types.py --check`: exit 0;
- `publish_process_scorecard.py --check`: "consistent with the committed recordings", exit 0;
- the four `build_sample_report.py --sample-dir <set> --check` runs: each "is consistent with its
  replays", exit 0;
- `git diff --name-only ff4c6bb8 HEAD` lists only `api/replay_loader.py`, `tests/api/test_view_model.py`,
  `tests/scripts/test_counterfactual_phase21.py`, `audits/audit-phase-21-counterfactual.md`,
  `docs/artifacts.md` and this card, so nothing under `engine/ agents/ meetings/ observation/
  orchestrator/ eval/ training/ frontend/ replays/ scripts/` moved.

### Items 3 and 4: the counterfactual memo freeze (`31b0a82b`)

**The frozen side, confirmed before E.4 cites it.** In a detached scratch worktree at
`39a568c6420531b7e22adcd5827fc18094594006` (`uv sync --frozen`, bare shell), the card's two-node-id
command printed `2 passed`. The same command at the base printed `2 failed`. The pointer E.4
quotes therefore discriminates.
- Its second command, `uv run python scripts/counterfactual_phase21.py --sets all`, exited 0 there
  and printed 383 lines under five `==` headers (four sets and POOLED).
- A count-only check, run inside that checkout with that checkout's own test-module parsers (the
  errata fold included), compared its `--json` output with the memo:
  - at `39a568c6`: pooled cells 43 of 43 equal, per-set cells 172 of 172 equal;
  - the same check on the baseline-9 bytes: pooled 1 of 43, per-set 42 of 172. This re-measures the
    investigation's 42 of 43 and 130 of 172 differing.
- `git log --first-parent --oneline 3eebc7d5..39a568c6 -- 'replays/samples/*/replay-seed-*.jsonl'
  'replays/ml_corpus/*/replay-seed-*.jsonl'` printed 0 lines, and `39a568c6` is the first parent of
  `acf6c604`.
- The scratch worktree was removed afterwards.

**The corroboration pins, in a test of their own.**
- `test_the_corroboration_cells_equal_the_committed_record` (`@pytest.mark.slow`, over `full_run`)
  calls `_assert_corroboration_pins(payload, committed)`, which asserts `pins["checked"] is True` and
  each of the four cells against `cf.COMMITTED_CORROBORATION_CELLS`.
- Planted cases, committed:
  - `test_the_corroboration_pin_bites_on_a_moved_cell`, parametrized over all four cells, moves one
    committed numerator by one and requires an `AssertionError` naming that cell;
  - `test_the_corroboration_pin_refuses_an_unchecked_payload` feeds the real one-set `fast_run`
    payload, whose pins read `checked: False`.
- All six pass.
- Neutralizing both helper assertions in a scratch edit turned the five planted cases red and left
  the main test green: `5 failed, 1 passed`. Restoring the helper made them green again.

**Where each assertion of the deleted drift gate that did not read the memo now lives:**

| deleted assertion | new home |
|---|---|
| `isinstance(pins, dict) and pins["checked"] is True` | `_assert_corroboration_pins`, via `test_the_corroboration_cells_equal_the_committed_record` |
| `tuple(pins["measured"][cell]) == expected` for the four cells | the same helper and test, with the moved-cell plants |
| `isinstance(...)` on `pooled_ballot_census`, `pooled_testimony_census`, `pooled_render_census`, `sets`, and inside `_totals`, `_run_ledger_rows` and `_run_tables` | These were mypy narrowings that typed the memo joins, not claims about the instrument. The payload keys are still read by the script's own table print, which `test_the_cli_runs_one_set_and_prints_the_table` exercises (a missing key fails it). `sets` and `pooled` are still narrowed in the retained `_rows` / `_set_block` readers of `test_the_baseline_9_tripwire_readings` and `test_the_block_level_cells_equal_the_byte_cells_on_the_committed_bytes`. |
| the advisory-marks test's vacuity assertion (the fast slice flags an advisory row) | `test_the_advisory_label_keys_on_the_rows_own_denominator` asserts `T-8` advisory on the fast slice |

Every other assertion (the `len(memo) == len(live) > 0` join sizes and the equalities) read the
memo and retires with it.

**The deletions.**
- Ten test functions (13 collected ids) and 29 helpers and constants with no caller left, exactly
  the card's list.
- `grep -n -w <name> tests/scripts/test_counterfactual_phase21.py` finds nothing for each of the 29.
- The retained helpers (`_memo_tables`, `_parse_tables`, `_values`, `_value`, `_set_block`, `_rows`,
  `_PAIR`, `_CELL_ID`, `_bar_language`) each still have a caller.
- `ruff check`, `ruff format --check` and `mypy` are clean on the file; no import went unused.
- Collected: **112 - 13 + 6 = 105**. The six added are the corroboration test, its four moved-cell
  ids and the unchecked-payload case. The whole module reads `105 passed`.

**The history block.** The module docstring ends with ten lines, one per deleted test. Each line
names what the test compared and "memo frozen (E.4)", and the drift gate's line names
`test_the_corroboration_cells_equal_the_committed_record`. The lines are one physical line each, so
some exceed 88 columns. Ruff's selected rules do not include E501, and the formatter leaves
docstrings alone. The set comparison and the current-pin check:

```python
"""The history-line set comparison, and the current-pin check.

usage: python history_check.py <base-module> <head-module>

1. ``def test_`` names in the base module that are missing at the head must
   equal the names the head's history block carries (one ``- ``name``...`` line
   each).
2. Every test the head's module docstring names OUTSIDE the history block (a
   current pin) must be a ``def test_`` in the head module.
Prints both comparisons; exit 1 if either differs.
"""

import ast
import re
import sys
from pathlib import Path

base = Path(sys.argv[1]).read_text(encoding="utf-8")
head = Path(sys.argv[2]).read_text(encoding="utf-8")


def test_names(source: str) -> set[str]:
    return {
        node.name
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }


docstring = ast.get_docstring(ast.parse(head), clean=False) or ""
marker = "Retired when the memo froze"
current_part, _, history_part = docstring.partition(marker)
history = {
    match.group(1)
    for line in history_part.splitlines()
    if (match := re.match(r"^- ``(test_\w+)``", line))
}
history_lines = [line for line in history_part.splitlines() if line.startswith("- ``")]
missing = test_names(base) - test_names(head)
print(f"deleted since base: {len(missing)}; history lines: {len(history_lines)}")
print(f"deleted but no history line: {sorted(missing - history)}")
print(f"history line but not deleted: {sorted(history - missing)}")
named = set(re.findall(r"``(test_\w+)``", current_part))
not_collected = sorted(named - test_names(head))
print(f"current pins named in the docstring: {len(named)}; not defined: {not_collected}")
sys.exit(0 if missing == history and not not_collected else 1)
```

- At the head, against `git show 95fb894b:tests/scripts/test_counterfactual_phase21.py`, it printed
  `deleted since base: 10; history lines: 10`, both difference lists empty, and
  `current pins named in the docstring: 5; not defined: []`. Exit 0.
- Planted, in a scratch copy with the `test_a_deleted_testimony_kind_row_is_caught` line dropped:
  `deleted but no history line: ['test_a_deleted_testimony_kind_row_is_caught']`, exit 1.
- Planted, in a scratch copy with `test_the_memo_table_parses_into_rows` renamed:
  `not defined: ['test_the_memo_table_parses_into_rows']`, exit 1.
- `pytest --collect-only` collects all five named current pins, as 12 ids (the no-bar plant is
  eight).

**The docstrings.**
- Item 4 now names the corroboration test and its plants.
- Item 5 states the current pins and argues the retirement:
  - from `3eebc7d5`'s measured/frozen pair rule, and from "no step re-issues the memo" (`509e92ed`,
    `608ae1f6`);
  - why `efcd43b8` does not apply: its graduation trigger does not hold, because the levers are live
    toggles that read OFF under an empty environment;
  - why the `70e49468` fixture route was not taken: committing 115,886,311 bytes of baseline-8
    replay JSONL in 300 files, re-measured with `git ls-tree -r -l 39a568c6`.
- The section-5 banner and the `full_run` docstring state the current pins. The title reads "the
  memo it published".

**E.4.**
- `git diff --numstat 95fb894b -- audits/audit-phase-21-counterfactual.md` prints `36 0`.
- The dated `### E.4` heading carries "No figure in this memo moves" and says the tables are the
  baseline-8 record, frozen, with no test comparing them from the commit that carries it. It also
  says §10's introduction and the Errata preamble describe the mechanism as it stood through
  `39a568c6`.
- It gives the full SHA and the exact commands (`uv sync --frozen`, the two-node-id pytest run,
  `uv run python scripts/counterfactual_phase21.py --sets all`) in a checkout of that commit, in a
  shell exporting no `AILIBI_*`.
- It carries no table row, no bar language and no task id, and names commits by SHA, with PR
  numbers beside them as E.3 does.
- Over the amended memo, the parse pin, the two no-bar pins and the eight no-bar plants pass
  (`11 passed`): the plants still bite. The pointer reproduces, as shown above.

**Registry row 109, recomputed last.**
- With the memo staged, the card's one-liner printed `26635440 329`. That is 26,632,967 + 2,473
  E.4 bytes, over the same 329 files.
- Planted, with the row left at 26,632,967: `test_every_counted_registry_row_matches_the_index`
  FAILED with "audits/: docs/artifacts.md promises 26,632,967 tracked bytes, the tracked files
  contain 26,635,440 bytes", and `test_availability_rejects_exact_byte_drift_without_count_change`
  PASSED.
- After the row was set to `26,635,440 tracked bytes / 329 files`, touching only row 109: `2 passed`.
- The offline `scripts/verify_ml_evidence.py` (never `--complete`) exits 1 at the head and at the
  base with identical verdict rows:
  - `audits/ [(b)]` and `in-tree family inventory` are OK;
  - the 12 FAIL rows are card A's ML rows (fit-corpus identity, ML grounding, surrogate ×3,
    conviction ×3, composed ×4), and this card adds none.

### The whole card: the gate

- **Merging `main`.** `git fetch origin` left `origin/main` at `ff4c6bb8`, the branch's base, so
  there was nothing to merge.
- **`bash scripts/check.sh`**, run whole in this clean worktree at `31b0a82b`, **exited 1**:
  - ruff check and format, lint-imports (4 kept, 0 broken), `validate_task_docs.py`,
    `generate_prompts.py --check` and mypy (493 files) all passed;
  - pytest read `38 failed, 8244 passed, 20 skipped, 3 xfailed, 9 errors`;
  - `set -e` then stopped the script before the frontend legs.
- **The base.** The same pytest leg in a clean scratch worktree at `ff4c6bb8` read
  `41 failed, 8246 passed, 20 skipped, 3 xfailed, 9 errors`.
- **The red sets.** `comm` of the two sorted id lists:
  - base minus head is exactly this card's three ids: `test_report_tick_fog_keeps_the_reported_body`,
    `test_the_memo_marks_every_advisory_cell` and `test_the_memo_table_equals_a_live_four_set_run`;
  - head minus base is empty.
- **The frontend legs, run separately:**
  - `npm run lint` exit 0 and `npm run tsc:check` exit 0;
  - `npm run test`: 20 files, `558 passed`;
  - `npm run build` exit 0;
  - `CI=1 npm run e2e`, with CI set so Playwright cannot reuse another session's server: `13 passed,
    3 skipped` (the opt-in README media capture), exit 0.
- **Other checks:** `scripts/verify_samples.sh` exit 0 (50 and 50 clean), `check_doc_facts.py`
  exit 0, `validate_task_docs.py` passed, and the tree stayed clean after every leg.

**The 47 ids still failing, with their owners** (card B has not merged at this head, so its six
remain; after B merges the red set is card A's 41 alone):

- Card A (`tasks/work/ml-reground-baseline-9.md`), 41 ids: 32 failed plus 9 errors.
  - errors (9): `tests/training/test_goodhart_probe.py::` `test_carried_4p1i_reread`,
    `test_carried_reread_requires_the_reference_roster`,
    `test_champion_genome_is_additive_for_old_report_json`,
    `test_conviction_path_consumption_is_metered_and_quoted`,
    `test_conviction_path_report_round_trips_json`, `test_conviction_path_report_shape`,
    `test_conviction_path_verdict_composes_blockers`;
    `tests/training/test_surrogate_runner.py::` `test_belief_fold_consumes_surrogate_ballot_roster`,
    `test_full_surrogate_driven_game_meetings_are_real_tallies`.
  - `tests/eval/test_balance_eval_meeting_runner.py::test_surrogate_runner_factory_drives_zero_cost_diagnostic_tournament`;
    `tests/experiments/test_torch_probe_excluded.py::test_stub_entrant_trains_through_env_and_lands_experiment_tier`.
  - `tests/scripts/test_verify_ml_evidence.py::` `test_a_perturbed_weight_hash_fails_and_is_named_corpus_independent`,
    `test_a_record_keyed_to_other_weights_fails_the_grounding_row`,
    `test_an_undeclared_corpus_still_fails_the_grounding_row`,
    `test_historical_verifier_refuses_relabeled_fit_version`, `test_perturbed_replay_fails_the_corpus_leg`,
    `test_recompute_reads_every_committed_verdict_against_the_live_corpus`.
  - `tests/training/test_bakeoff_harness.py::` `test_evaluate_candidate_experiment_tier`,
    `test_evaluate_candidate_full_row`, `test_evaluate_candidate_go_serves_the_term_live`,
    `test_evaluate_candidate_multi_seed_stamps_the_composed_mean`, `test_goodhart_surrogate_rerun_ci_budget`;
    `tests/training/test_bakeoff_methods.py::test_the_committed_map_elites_pool_is_historical_and_structurally_untouched`.
  - `tests/training/test_conviction_model.py::` `test_committed_artifact_round_trips_and_the_refit_no_longer_matches`,
    `test_the_committed_verdict_is_the_baseline8_first_evaluation`;
    `tests/training/test_goodhart_probe.py::` `test_conviction_reader_determinism_at_unit_level`,
    `test_probe_reruns_end_to_end_on_the_regrounded_surrogate`;
    `tests/training/test_model_evidence_provenance.py::test_historical_diagnostic_restores_committed_models`.
  - `tests/training/test_surrogate_runner.py::` `test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers`,
    `test_cap_is_cumulative_across_fresh_runner_instances`,
    `test_committed_artifact_round_trips_and_the_refit_no_longer_matches`,
    `test_factory_rejects_a_loosened_or_foreign_shared_counter`,
    `test_fallback_a_trains_today_regardless_of_verdict`,
    `test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift`,
    `test_impostor_ballot_never_names_a_fellow_impostor`,
    `test_missing_artifact_and_malformed_meeting_id_fail_loud`,
    `test_runner_satisfies_meeting_runner_protocol`, `test_surrogate_game_is_byte_deterministic`,
    `test_the_committed_surrogate_is_a_baseline8_fit_on_the_baseline8_corpus`,
    `test_the_committed_verdict_is_keyed_on_the_weights_and_reproduces`,
    `test_the_install_gate_refuses_the_committed_no_go_as_a_training_runner`.
- Card B (`tasks/work/committed-channel-rederivation.md`), 6 ids:
  - `tests/agents/test_reported_testimony.py::test_reported_rows_survive_in_every_candidate_bucket`;
  - `tests/eval/test_evidence_honesty.py::test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage`
    and `::test_the_instrument_and_the_detector_read_one_adjacency_rule`;
  - `tests/meetings/test_contradictions.py::TestGroundedProsecutionCommittedCensus::test_the_fully_grounded_leg_drops_the_whole_class`
    and `::TestGroundedProsecutionInjusticeShapes::test_no_committed_ejection_rides_a_strong_sighting_flag`;
  - `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites`.

### Decisions

1. **The moved-cell plant covers all four cells.** It is parametrized over the four, where the card
   asks for one moved cell. The four extra ids cost nothing because `full_run` is module-scoped.
   The unchecked-payload plant uses the real one-set run rather than a hand-built dict.
2. **The per-set meeting-frame guard is kept.** The old test's only guard, "at least one body-report
   meeting", stays as a per-set assertion beside the new game-deciding guard, so no assertion was
   relaxed.
3. **One shared loader builder.** It keeps the no-op `AILIBI_EVIDENCE_QUALITY_LIFT` export in one
   place rather than copying it into a second fixture, and does not remove it: that is out of scope.
4. **Figures are pinned as measured.**
   - The bundle: the counts, the bytes, the same-checkout `diff -r` and the `created_at`-blanked
     digest are the evidence. The raw tree digest folds replay mtimes, so it is per-checkout and
     is not pinned (see above).
   - The decision memo's "233,746,908 bytes with the tournament reports" is every tracked file
     under `replays/samples` and `replays/ml_corpus` at `39a568c6` (316 files). The 300 replay files
     plus the 4 tournament reports come to 233,481,619 bytes. The docstring cites only the replay
     figure, which reproduces.
5. **E.4 states its own discrimination** ("the same pytest run at `95fb894b` ... fails on both").
   It was measured at `ff4c6bb8`, whose tests, scripts and recordings are `95fb894b`'s.
6. **No held-out manifest is touched.** None of `audits/deduction-candidate/held-out/manifest*.json`
   hashes `api/replay_loader.py`, so the restamp rule of `tasks/post-merge-plan.md` does not apply.

### Limitations

- **`bash scripts/check.sh` does not pass, so this card is not Verified.** It exits 1 on 47 ids,
  card A's 41 and card B's 6, which this card inherits from `main` and does not touch. By
  `AGENTS.md` a card is done only when `check.sh` passes, and `docs/workflow.md` defines Verified as
  the combined gate passing. What this card shows instead is the scoped gate the Constraints
  define: its three ids are green, the red set at its head is main's minus those three, and every
  other gate step is green. The last-merging card owes the fully green `main`.
- **Host and checkout.** The bundle measurements and the e2e run are Darwin arm64 only; the Pages
  rebuild runs on Linux. The byte-identity claim is a same-checkout before/after comparison, plus a
  `created_at`-blanked digest that is equal across two checkouts on one host. The raw tree digest
  is per-checkout (it folds replay mtimes through `created_at`) and is not a pin; no Linux digest
  was taken.
- **What is no longer pinned.**
  - Whole-run drift in the instrument's census and ledger output is caught only by the retained
    readings (tripwires, block-level cells, corroboration cells, OFF-equals-record, the refusals).
    The card's Record impact accepts this.
  - The census payload keys are exercised only through the CLI print path.
- **The frontend legs.** `check.sh` stops at the pytest leg under `set -e` while other cards' ids
  are red, so its frontend legs were run separately, with the results above.
- **Card B's ids.** The red set at this head includes card B's six ids, because B has not merged. The
  last-merge proof of a fully green `main` belongs to whichever PR merges last.
- **`docs/artifacts.md` has two writers.** This card changed row 109 and card A writes rows 103-104.
  Whichever merges second merges `main` first and re-runs
  `test_every_counted_registry_row_matches_the_index`.

### Review corrections, round 1 (2026-09-23)

Two review lenses each returned one blocking finding over the head `869526ac`. Both are valid.
Both are repaired in this card's prose and in the PR body alone:
- no code, test, `audits/`, recorded or generated byte moved in this round;
- so registry row 109 stays at `26,635,440 tracked bytes / 329 files`;
- every figure above that this round does not name stands as measured.

**1. Results claimed the delivery state Verified while the combined gate exits 1** (the scope,
policy and record-integrity lens).
- *What was true at `869526ac`.* The Results head read "Verified (every acceptance item below, and a
  gate whose red set is main's minus this card's three ids)". `docs/workflow.md:64` defines Verified
  as the acceptance checks and the combined project gate passing, and `bash scripts/check.sh` exits
  1 at that head. `c4deaa43` withdrew the same claim from `tasks/work/rubric-genuine-class-selfcheck.md`
  for the same reason.
- *Repaired.* The Results head now states Implemented, with Verified answered "no" and the reason.
  A new first Limitations item states the rule and the scoped gate that holds instead. The Status
  line stays `ready`, as the Constraints require.
- *Proof.* The gate re-run below: `bash scripts/check.sh` still exits 1, and the red set at the
  head is main's minus exactly this card's three ids.

**2. The demo-bundle digests did not reproduce, and the stated cause (the host) was wrong** (the
documentation lens).
- *What was true at `869526ac`.* Results and the PR quoted digests as if they were pins: `d8e619ea…`
  for the featured tree (three times), and `68928ac5…` / `db7e0e78…` for seed 13. They also said the
  card's `37afc888dd22ecc4…` did not reproduce "on this host". On the same Darwin arm64 host, with
  the same scripts, the reviewer read other digests in other checkouts, with the same counts and
  bytes. The reviewer traced the difference to `api/replay_loader.py:2481`.
- *Confirmed.* The loader sets `created_at=_iso_mtime(path)`, the replay file's mtime. Nine baked
  files carry it: the seven featured replays and the two `replays.json` listings. The re-measurement
  in two checkouts (the demo-bundle block above) found:
  - the raw digests differ by checkout: `015546b7…` in one, `3ebdb092…` in the other;
  - the 9 differing files differ only in `created_at` (`strip_diff.py`: 0 after blanking);
  - the `created_at`-blanked digest is equal across the two: `dc2fcae1…`.

  The reviewer's own digests (`9ad2b6d2…`, `6498ce41…`, `39cca46a…` / `2ade25a9…`) are per-checkout
  in the same way, and are not re-cited as figures.
- *Repaired.* The demo-bundle block, Decision 4 and Limitations now say that the raw digest is
  per-checkout and is not a pin. They also withdraw the host explanation. The PR's Summary,
  Definition of done and Decisions say the same.
- *What still stands, now shown in two checkouts:*
  - the featured bake is byte-identical before and after the fix within one checkout;
  - the perturbed seed-13 bake differs in exactly one file, `9p2i/replays/headless-seed-13.json`
    (+169 bytes).

**The gate, re-run after these edits** (card prose only; `Darwin 24.6.0 arm64`, bare shell):

- **`bash scripts/check.sh`**, run whole in this worktree with this round's card edits in place
  (the only change against `869526ac`), **exited 1**, captured directly:
  - these steps passed: ruff check ("All checks passed!"), ruff format (522 files), lint-imports (4
    kept, 0 broken), `validate_task_docs.py` (390 phase tasks, 390 prompts, 77 work cards),
    `generate_prompts.py --check` (390 in sync) and mypy (493 source files);
  - pytest read `38 failed, 8244 passed, 20 skipped, 3 xfailed, 9 errors`, which is 47 red ids;
  - `set -e` then stopped the script before the frontend legs.
- **Main, re-measured.** The same pytest leg (`-n auto --dist loadfile`) ran in a fresh detached
  scratch worktree at `ff4c6bb8`. That is `origin/main`, unchanged since the branch was cut. It read
  `41 failed, 8246 passed, 20 skipped, 3 xfailed, 9 errors`, which is 50 red ids.
- **The red sets.** `comm` of the two sorted id lists:
  - main minus head is exactly this card's three ids:
    - `tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body`;
    - `tests/scripts/test_counterfactual_phase21.py::test_the_memo_marks_every_advisory_cell`;
    - `tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run`;
  - head minus main is empty;
  - the head's 47 are the ids listed with their owners in the gate section above: 41 in card A's
    files and 6 in card B's.
- **The other legs, run separately:**
  - the frontend: `npm run lint`, `npm run tsc:check`, `npm run test` (20 files, `558 passed`) and
    `npm run build`, each exit 0;
  - `CI=1 npm run e2e`: `13 passed, 3 skipped` (the opt-in README media capture), exit 0;
  - `scripts/verify_samples.sh`: exit 0, 50 and 50 clean;
  - the four `build_sample_report.py --sample-dir <set> --check` runs, `publish_process_scorecard.py
    --check`, `gen_frontend_types.py --check` and `check_doc_facts.py`: each exit 0;
  - the offline `verify_ml_evidence.py` (never `--complete`): exit 1. `audits/ [(b)]` and the
    in-tree family inventory are OK, and the same 12 FAIL rows remain, all card A's ML rows;
  - the two registry-row tests: `2 passed`.
- **After the commit.** This subsection was filled in afterwards (prose only). At the commit,
  `validate_task_docs.py`, `generate_prompts.py --check` and `check_doc_facts.py` were re-run and
  passed. The tree was clean after every leg, and the scratch worktree was removed.
