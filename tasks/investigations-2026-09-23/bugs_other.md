# Investigation: bugs_other (four of the nine non-ML red tests on baseline 9)

Investigator memo, 2026-09-23. Read-only on the repository. All citations are at
`95fb894b` (main after the baseline-9 re-record merge `acf6c604`). Every probe edit was
made in the worktree, measured, and restored from a copy; the worktree ended clean
(`git status --short` empty). No commit, no push, no PR comment, no provider call, no
recorder, nothing written under `training/artifacts`, no `.env` read. Censuses below are
count-only.

Owner context: the answer to the re-ground card's Q5 (`tasks/work/ml-reground-baseline-9.md:301-303`)
was "Look into why the tests would still fail, if they are necessary at all, or a separate
potential path forward. Go with the recommended idea from that." This memo gives that
recommendation for four of the nine.

## Summary

| # | test | root cause | recommendation | record impact |
|---|---|---|---|---|
| 1 | `tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body` | LOADER. Task 21.6 made a game-deciding trigger tick end the game without a meeting. The event projection was updated for that case; the fog re-open was not. | 6-line `elif` in `api/replay_loader.py` (fix below), in a small non-ML card | Served `/replays/{id}` fog changes on 3 final frames across the 4 sets (none featured). No recorded byte, state hash, golden, demo-bundle byte or eval figure moves. |
| 2 | `tests/eval/test_evidence_honesty.py::test_the_instrument_and_the_detector_read_one_adjacency_rule` | TEST RESTATEMENT. The drift guard restates the detector's tick term against the STAY window. The detector moved to the ROUTE's outer ends in `301993f7`. | Test-only: read the route's outer ends, and fix a 0-as-unset sentinel (diff below) | No `eval/` byte and no census figure moves. Only the guard's min-gap reading moves, 0 -> 2. |
| 3, 4 | `tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run`, `::test_the_memo_marks_every_advisory_cell` | They hold a dated baseline-8 memo to a live run on baseline-9 bytes. Every compared surface drifts, and the errata fold cannot delete rows. | RETIRE the memo-vs-live comparison, as the Phase 20 precedent did (`efcd43b8`): freeze the memo; keep the live corroboration-pin assertion as its own test; delete the coupled fold and perturbation cases; append a dated E.4 provenance note | One `audits/` byte change, so the `audits/` row at `docs/artifacts.md:109` is recomputed. The file count (329) is unchanged. |

---

## 1. `test_report_tick_fog_keeps_the_reported_body`

### Reproduction

`uv run pytest -q tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body`
fails with `p-9 does not see the body it reported (p-3) at tick 13 of headless-seed-13`
(`tests/api/test_view_model.py:1267`).

The recording, `replays/samples/9p2i/replay-seed-13.jsonl`, has 16 rows. At tick 13 the
applied actions are, in order:
1. `p-1 kill p-6` (applied);
2. two moves (applied);
3. `p-6 do_task` (rejected, since p-6 is dead);
4. `p-9 report body-p-3-7` (applied).

The next row is a `game_over` row at tick 13. There is no `meeting` row at tick 13.

### Root cause: the loader (not the engine, not the recording)

- **Engine order, by design.** `engine/tick.py:632-658` handles the report first.
  `_apply_report` (`engine/tick.py:453-460`) sets `discovered_by` and `phase="MEETING"`. The
  win check then runs inside the MEETING branch, and "A tick that decides the game does not
  open a meeting" (`:642-646`, Task 21.6, commit `9af1bf3d`). So the events are `Killed ...
  MeetingTriggered, GameOver`, and the returned phase is `GAME_OVER`. That is the intended
  §3.5 order. The recording replays byte-identically, since the loader's state-hash check at
  `api/replay_loader.py:1640-1647` passes.
- **The event projection was updated for Task 21.6.** `api/replay_loader.py:2223-2251`
  suppresses the `meeting_triggered` chip when `state.phase == "GAME_OVER"`, and still
  projects `report_body`, "because the body was still found". That is why the served tick
  carries a `report_body` event and no `meeting_triggered`.
- **The fog re-open was not updated.** `body_id` is only derived inside
  `if state.phase == "MEETING":` (`api/replay_loader.py:1683-1692`), and it is passed as
  `reopened_body_id` at `:1702-1705`. On the game-deciding tick it stays `None`. The body keeps
  its `discovered_by`, and `compute_visibility_for_player` excludes discovered bodies (see the
  docstring at `:2027-2036`), so the reporter's served `visible_bodies` drops it.

### Why it was green before

The defect has been latent since Task 21.6. A count-only census counted game-deciding report
ticks: the last tick row has an applied `report`, a `game_over` at the same tick, and no
`meeting` row at that tick.

| set | baseline 8 (`39a568c6`) | baseline 9 (`95fb894b`) |
|---|---|---|
| samples/9p2i | 0 | 1 (seed 13) |
| samples/4p1i | 1 | 1 |
| ml_corpus/9p2i | 0 | 0 |
| ml_corpus/4p1i | 1 | 1 |

The test iterates only the 9p2i sample set (fixture at `tests/api/test_view_model.py:127-135`).
Both 4p1i sets already carried the case at baseline 8, where it went unobserved.

### Minimal fix (probed, then restored)

```diff
@@ api/replay_loader.py:1692
                     trigger_kind_by_meeting_id[meeting_id] = trigger_kind
+                elif state.phase == "GAME_OVER" and any(
+                    isinstance(event, MeetingTriggeredEvent) for event in events
+                ):
+                    # A trigger tick that decided the game convenes no meeting,
+                    # but a reported body was still found on this frame.
+                    _, body_id = _meeting_trigger_from_events(events)
```

`meeting_id` and `trigger_kind` stay `None`, which matches the event projection's no-chip
rule. `_meeting_trigger_from_events` (`:2926-2939`) returns `None` for an emergency trigger, so
nothing is re-opened then. In the same change, update the comment at `:1698-1701` and the
docstring at `:2027` ("on its meeting frame") so they say "on its report frame, including a
game-deciding report that convenes no meeting".

Verification with the probe in place:
- `tests/api/test_view_model.py` and `tests/api/test_leak.py`: 59 passed, 1 pre-existing skip.
- `tests/api` plus `tests/scripts/test_build_demo_bundle.py`: 474 passed, 2 pre-existing skips.
- A count-only walk of every `report_body` event through `ReplayLoader` found this many
  reporters missing their own body (misses before the fix -> after):
  - samples/9p2i: 136 reports, 1 -> 0;
  - samples/4p1i: 37 reports, 1 -> 0;
  - ml_corpus/4p1i: 37 reports, 1 -> 0.
- Perturbed proof: the unfixed loader fails the test on seed 13, which is today's red.

### Blast radius

- **Served bytes.** Only the `visibility.visible_bodies` of living agents on the final frame
  of the 3 games above: the reporter plus anyone whose seen rooms include the body's room. The
  fog feeds only the API DTO, as `AgentVisibilityView` (`api/replay_loader.py:3427-3445`,
  `api/schemas.py:272-286`).
- **Not affected.** `eval/funnel.py:377-395` re-runs its own observation walk and does not read
  the loader's fog. Agents, memory, evals and ML read engine packets, not this DTO.
- **Leak test.** `tests/api/test_leak.py:1119-1126` only requires a visible body's room to be in
  the observer's seen set. The reporter's own room always is, and the test stays green.
- **Goldens.** None: no committed JSON fixture carries `visible_bodies`.
- **Demo bundle.** It bakes loader payloads for the featured games only
  (`scripts/build_demo_bundle.py:319-364`). The featured list is 9p2i seeds 23, 0, 29, 2 and
  4p1i seeds 2, 11, 29 (`frontend/src/components/ReplayPicker.tsx:111-148`), and none of them
  has a game-deciding report tick. The baked JSON is byte-identical, so the Pages rebuild on
  merge publishes no changed payload. The PR should still say so, because `AGENTS.md` treats
  viewer changes as publication decisions.

### Where it belongs

Put it in a card, not the re-ground card. `AGENTS.md` delivers implementation via a
`work/<slug>` branch with one PR. The re-ground card's expected scope is ML artifacts and
their tests (`tasks/work/ml-reground-baseline-9.md` "Expected scope"), and `api/` is outside
it. The re-record card classified this as a "product gap ... out of this record's scope"
(`tasks/work/process-rerecord.md:1394`; `audits/audit-2026-09-22-process-rerecord.md:1157`).

Recommended: one small non-ML card for the baseline-9 non-ML red repairs, coordinated with
the sibling investigations, with one commit per item. Optional hardening: parametrize the test
over `samples/4p1i` too, which has carried the case since baseline 8, so the gate does not
depend on one 9p2i recording.

---

## 2. `test_the_instrument_and_the_detector_read_one_adjacency_rule`

### Reproduction

The test fails at `tests/eval/test_evidence_honesty.py:3834` with `assert 0 >= (1 + 1)`. The
other two checks pass:
- direction 1, `demoted_but_not_adjacent == 0`;
- `kept == 29`.

### Root cause: the drift guard's restatement is stale; the detector is right

- **The detector** (`meetings/transcript.py:3357-3387`, `_adjacent_within_one_tick`) measures
  the sighting's gap to the route's OUTER ends, `alibi.route_from_tick` and
  `alibi.route_to_tick` (`:2496-2513`). An interior stay boundary is a transition the speaker
  declared, not movement fuzz (docstring at `:3362-3376`). This is the alibi-as-route design,
  from review round 3, commit `301993f7`
  ("fix: measure a route's movement fuzz at its outer endpoints, not a leg's";
  `tasks/work/alibi-as-route.md:338-348`). The endpoint-tick band reads the same outer ends
  (`meetings/transcript.py:3283-3299`).
- **The instrument** resolves a flag to the STAY under the sighting.
  `eval/evidence_honesty.py:2278-2312` (`_leg_under_sighting`) and `:2315-2381`
  (`_resolve_flag`) put the stay's `from_tick`/`to_tick` on `_ResolvedFlag` (`:2049-2071`).
  That is correct for what the instrument publishes:
  - the room compared;
  - the I-6 cell's gap OUTSIDE the window (`_fold_geometry`, `:2384-2425`), which is 0 on any
    minted flag either way.
- **The test's restatement is the stale part.** `_endpoint_gap`
  (`tests/eval/test_evidence_honesty.py:3566-3578`, written in Task 20.27, `ddc1b2fb`) restates
  the detector's tick term against `resolved.from_tick`/`to_tick`, which is the STAY. On a
  one-stay account the stay is the route. Every baseline-8 claim was one segment, so the two
  readings coincided. Baseline 9 is the first recording with multi-stay routes.

Count-only probe over the 29 adjacent flags the detector keeps STRONG (all four sets; the 4p1i
sets hold none):

| measure | result |
|---|---|
| on a multi-stay route | 29 of 29 |
| stay-relative gap histogram | 0: 26, 3: 1, 4: 2 |
| route-relative gap histogram | 2: 5, 3: 10, 4: 7, 5: 2, 6: 1, 7: 2, 8: 2 |

With the route reading the minimum is 2, which meets `MAP_ARBITRATION_MAX_TICK_GAP + 1`. This
matches the record audit's measured reason (`audits/audit-2026-09-22-process-rerecord.md:1155`).

### Which side changes

The instrument side, and only its test-local restatement. The detector is the design, so it
does not change. No production code reads this tick term: a `git grep` for
`MAP_ARBITRATION|_endpoint_gap|adjacent_kept` in `eval/`, `scripts/` and `api/` finds nothing.
`eval/evidence_honesty.py` therefore needs no edit either.

### Second defect: the minimum can be masked

`_corridor_census` uses `0` as its "unset" sentinel: `min_gap = 0` (`:3641`) and
`min_gap = gap if min_gap == 0 else min(min_gap, gap)` (`:3677`). A genuine 0 followed by any
non-zero gap overwrites the 0. The guard could therefore pass while a zero-gap kept flag
exists, which is exactly the defect it exists to catch. It went red here only because the
last-processed gaps happened to be 0.

### Minimal fix (probed, then restored)

This is a test-only change:
1. Import `maximal_stays`.
2. Add `_route_window(resolved, index=...)`, which returns the account's outer ends:
   - `maximal_stays(route)[0].from_tick` and `[-1].to_tick` for an `AlibiClaim`;
   - `tick` for a whereabouts claim;
   - an `AssertionError` otherwise.
3. Give `_endpoint_gap` a `route=` argument.
4. Make the sentinel `None` (the census field becomes `int | None`).
5. Rewrite the final assertion as `gaps = [...not None]; assert gaps and min(gaps) >= ...` so
   mypy is clean.
6. Update the one synthetic caller at `:3754` to `route=(4, 8)`.

The full diff is 43 insertions and 15 deletions. In the same change, refresh the stale comment
at `:3825-3828` ("8 of the 148 ... 148 - 140 = 8", a baseline-6 statement). The lever is now
unconditional, so `demoted` is 0 and the enumerated difference reads: every adjacent flag the
detector keeps STRONG sits two or more ticks from its route's outer ends.

Verification with the probe in place:
- The target test, the endpoint-gap test, the corridor, I-6 and sole-flag tests: 8 passed.
- The whole file: 106 passed, 1 failed. The failure is the separately listed
  `test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage`, which is out of this
  topic.
- `ruff check` clean, `ruff format` applied, `mypy` on the file clean.
- Perturbed proof: pointing the census back at the stay window
  (`route=(resolved.from_tick, resolved.to_tick)`) turns the guard red with `assert 0 >= (1 + 1)`.

### What the honesty census figures do after it

Nothing moves. Every pinned figure re-derives identically:

| figure | value |
|---|---|
| STRONG sighting flags | 42 |
| adjacent, per set | 5 / 24 / 0 / 0, pooled 29 |
| demoted | 0 |
| kept | 29 |
| direction 1 | 0 |
| sole-flag ejections | unchanged |

The published I-6 cells in `eval/evidence_honesty.py` are untouched. The only reading that
changes is the guard's min gap, 0 -> 2.

---

## 3 and 4. `test_the_memo_table_equals_a_live_four_set_run` and `test_the_memo_marks_every_advisory_cell`

### What the tests and the memo say

- **The memo's substrate.** `audits/audit-phase-21-counterfactual.md:1-14` declares
  "Every number here is recomputed on the baseline-8 bytes" and "Substrate: baseline 8".
  Its date is 2026-09-01, and it was published before the pre-registration.
- **§10's intro** (`:606-608`) says every row is compared against this document by the test,
  "so the memo cannot drift from the script".
- **The Errata rule** (`:893-899`): "Nothing above is rewritten". A later change that moves a
  figure is re-derived in a dated erratum, and the test reads the errata as the authoritative
  pin, row by row.
- **The errata fold** (`tests/scripts/test_counterfactual_phase21.py:3009-3034`) overrides
  pooled and per-set rows and render-census rows only. The ballot, kind, ledger and
  class-total parsers (`:3105`, `:3189`, `:3236`, `:3281`) read the whole text, last row wins.
  None of the parsers can DELETE a row.
- **The drift gate** (`:705-779`) first asserts the live corroboration pins against
  `cf.COMMITTED_CORROBORATION_CELLS`. These are re-pinned to the baseline-9 record by `948abae1`
  and pass. It then compares every memo surface with the live run and fails at the first,
  `memo_pooled == live_pooled` (`:726`).

### Measured drift on baseline 9 (count-only; test helpers against `cf.run(all sets)`)

| surface | memo keys | live keys | differing |
|---|---|---|---|
| pooled cells | 43 | 43 | 42 |
| per-set cells | 172 | 172 | 130 |
| ballot census | 16 | 16 | 15 |
| kind census (two tables) | 8 + 8 | 8 + 8 | 5 + 7 |
| render census | 18 | 18 | 18 |
| ledger rows | 46 | 42 | 81 (nearly disjoint) |
| class totals | 7 | 6 | 7 |
| advisory marks | 27 marked | 33 flagged | 6 flagged but unmarked (5 on samples/4p1i: C-2, P-2, C-3, C-4, P-4) |

The corroboration pins hold (checked, matching).

### Precedents

- **Errata E.1, E.2 and E.3** (`:901`, `:1070`, `:1224`). E.1 and E.2 were instrument or lever
  changes before the record, on the SAME baseline-8 population, and republished only the moved
  rows. E.3 is a provenance-only erratum: "No figure in this memo moves".
- **The Phase 20 counterfactual at the baseline-7 record** (`efcd43b8`).
  `tests/scripts/test_counterfactual_phase20.py` deleted 836 lines, including
  `test_the_memo_table_equals_the_scripts_output` and its perturbation cases. It kept
  `test_the_memo_is_committed_and_still_carries_its_table` (`:87-91`), "frozen as the
  pre-record prediction it was" (`:15-16`). The memo itself was not edited.
- **This script's own refusal text** (`scripts/counterfactual_phase21.py:4130-4153`) already
  names the doctrine: "the memo's table is FROZEN as the pre-record prediction it was".
- **The baseline-8 re-record** (`3eebc7d5`) predates this memo, so it offers no precedent for
  it. The baseline-9 re-pin (`948abae1`) re-pinned the live instrument readings in the test
  (`test_the_baseline_9_tripwire_readings`, the corroboration constants) and left these two red
  pending an owner call.

### Options

- **A. A dated erratum E.4 republishing on baseline 9 through the memo's own mechanism.**
  Rejected, for three reasons:
  1. It is semantically wrong. An erratum corrects a figure about the memo's declared
     baseline-8 substrate, and a baseline-9 table is a new measurement on a new population.
  2. It is mechanically insufficient. The fold cannot delete the 46 baseline-8 ledger rows or
     the extra class total, so the gate stays red unless the test's fold grows whole-table
     replacement.
  3. It republishes essentially the whole memo (215 cells plus every census and the ledger),
     and must be repeated at every future re-record, with no pending decision reading those
     numbers. Phase 21 closed FINDING at #430.
- **B. Re-anchor the tests to a new dated baseline-9 memo.** It keeps a whole-run pin, but it
  publishes a new audit nobody asked for, needs the same full-table authoring, and recurs at
  every re-record.
- **C. Retire the memo-vs-live comparison as a test of a historical document.** This follows
  `efcd43b8` and the script's FROZEN doctrine. The memo keeps its value as the dated pre-record
  prediction the pre-registration and the Phase 21 close read against. The instrument keeps its
  live regression pins (tripwire readings, corroboration cells, OFF-equals-record, refusals,
  planted cases).
- **D. Keep them red.** Rejected: it blocks "done" under `AGENTS.md`, and every future
  re-record inherits it.

### Recommendation: C, with the smallest honest retirement

Changes to `tests/scripts/test_counterfactual_phase21.py`:

1. **Split the live corroboration-pin loop** out of the drift gate into its own `@slow` test
   over `full_run`, e.g. `test_the_corroboration_cells_equal_the_committed_record`. This is the
   one instrument-vs-record assertion the gate carried (its docstring: "where the four
   corroboration cells become an assertion").
2. **Delete the memo comparisons**, i.e. the rest of `test_the_memo_table_equals_a_live_four_set_run`
   and all of `test_the_memo_marks_every_advisory_cell`.
3. **Delete the coupled consumers that exist only for that gate** (craft rule 3, retire means
   delete). These are:
   - the errata-fold tests: `test_an_erratum_overrides_the_row_it_republishes`,
     `test_a_memo_with_no_errata_folds_to_the_recorded_tables`,
     `test_a_wrong_erratum_cannot_pass_the_drift_gate`;
   - the planted perturbation cases: `test_the_table_comparison_bites_on_a_perturbed_memo`,
     `test_the_census_comparisons_bite_on_a_perturbed_memo`,
     `test_the_ledger_comparison_covers_the_recorded_tally`,
     `test_a_deleted_testimony_kind_row_is_caught`,
     `test_the_advisory_marker_check_bites_on_a_stripped_memo`;
   - the helpers that are then dead: `_published_tables`, `_split_errata`,
     `_published_render_census`, `_published_parses`, `_bump_last_number`,
     `_perturb_first_published_value`, `_strip_one_advisory_marker`, `_advisory_cells`,
     `_memo_advisory_cells`, `_memo_ballot_census`, `_memo_kind_census`, `_memo_render_census`,
     `_memo_ledger_rows`, `_memo_class_totals`, `_run_tables`, `_columns`,
     `_flatten_*_census`, `_run_ledger_rows`, `_run_kind_census`, `_totals`, the label
     constants and `_ERRATA_HEADING`.

   Delete each only after confirming it has no remaining caller. `_set_block` and `_rows` stay.
4. **Keep the frozen-document pins, which pass and are true of a dated record.** These are
   `test_the_memo_table_parses_into_rows` (the Phase-20-style "still carries its table" pin)
   and the no-bar checks (`:404-452`).
5. **Rewrite the module docstring** to say the memo is the frozen baseline-8 record and why.

Change to the memo: append a dated provenance erratum E.4, in the E.3 style ("No figure in
this memo moves"). It states that the tables above are the baseline-8 record, frozen, and that
from the baseline-9 re-record (`acf6c604`) no test compares them with a live run. Otherwise
§10's claim (`:606-608`) and the Errata preamble would name an enforcing mechanism that no
longer exists (craft rule 5).

Record impact: this one `audits/` byte change moves the `audits/` row at `docs/artifacts.md:109`
(now "26,632,967 tracked bytes / 329 files", measured equal at HEAD). Recompute the bytes; the
file count is unchanged. `scripts/verify_ml_evidence.py:2867-2901` (`inventory_problems`)
enforces that row, so the recompute must be the LAST `audits/` write in the PR. If another
branch also writes `audits/`, coordinate a single writer.

Zero-byte alternative, the strict `efcd43b8` precedent: leave the memo untouched, with no
registry recompute, at the cost of the stale §10 sentence.

No other gate breaks. The deleted test ids are cited only by the dated re-record audit and
card (`audits/audit-2026-09-22-process-rerecord.md:1158`,
`tasks/work/process-rerecord.md:1402-1403`), which are not rewritten, and
`scripts/check_doc_facts.py` resolves no test ids.

---

## Implementation steps

1. Open one small non-ML card, `tasks/work/<slug>.md`, for these repairs. Coordinate with the
   sibling investigations of the other five non-ML reds. Deliver it on `work/<slug>` with one
   PR into `main` and one commit per item.
2. Item 1: add the `elif` in `api/replay_loader.py` after `:1692` and update the comments at
   `:1698-1701` and `:2027`. Optionally parametrize the view-model test over `samples/4p1i`.
   Run `tests/api` and `tests/scripts/test_build_demo_bundle.py`.
3. Item 2: apply the test-only diff (the route window, the `None` sentinel, the assertion
   shape, the synthetic caller) and refresh the stale comment. Run
   `tests/eval/test_evidence_honesty.py` and mypy on the file.
4. Items 3 and 4:
   - split the corroboration pins into their own test;
   - delete the memo comparisons, the errata-fold tests, the perturbation cases and the dead
     helpers;
   - keep the parse and no-bar pins, and rewrite the module docstring;
   - append E.4 to the memo;
   - recompute the `audits/` row at `docs/artifacts.md:109` last.
5. Run `bash scripts/check.sh` whole in a clean worktree. Expect exactly these four ids to leave
   the red list, and no new red.

## Risks

- **Item 1.** A future game-deciding EMERGENCY trigger re-opens nothing, which is correct. The
  3 affected games' final-frame fog changes for any spectator bookmark of them. The Pages
  rebuild on merge re-walks the featured games through the changed loader, but they are
  unaffected.
- **Item 2.** `_route_window` reads the claim through the transcript index. A future
  alibi-artifact type other than an `AlibiClaim` or a whereabouts claim raises loudly instead of
  being mis-measured, which is intended.
- **Items 3 and 4.** The instrument loses its whole-run memo pin. Future output drift is caught
  only by the retained readings (tripwire rows, corroboration cells, OFF-equals-record and the
  refusal cases). Deleting the fold machinery is irreversible in-tree, although git history keeps
  it. If the owner wants a baseline-9 counterfactual table later, that is option B, a new dated
  memo.
- **Record ordering.** The `audits/` registry row must be recomputed after every other
  `audits/` byte in the PR, or `test_every_counted_registry_row_matches_the_index` goes red.

## Could not establish

- The 4p1i seed numbers of the two game-deciding report ticks. The census was count-only and did
  not name them.
- Whether frontend Vitest or Playwright assertions depend on a final-frame fog. They were not
  run; the Python API and bundle-builder suites were.
- A full `bash scripts/check.sh` run with the three fixes applied together. Only targeted suites
  were run, on macOS rather than the Linux container.
- Whether the owner prefers the E.4 note (honest mechanism claim, one registry recompute) or the
  zero-byte `efcd43b8` variant. Both are given with their impact.

## Reproduction

The probe and census scripts were kept outside the tree, in the session scratchpad. What they
do:

- **Game-deciding report census** (JSONL only, count-only). For each
  `replays/{samples,ml_corpus}/{9p2i,4p1i}/replay-seed-*.jsonl`, count the games where all of
  the following hold:
  - the last `tick` row has an applied `report`;
  - `game_over.tick` equals that tick;
  - no `meeting` row carries that tick.

  Baseline 8 was read from `git archive 39a568c6 replays/samples replays/ml_corpus` extracted
  to scratch.
- **Reporter-fog census.** Set `AILIBI_EVIDENCE_QUALITY_LIFT=1` in the probe process only, as
  the test fixture does. Build `ReplayLoader(replay_dir=...)`. For every `report_body` event,
  count reporters whose `visibility.visible_bodies` lacks `body_of`.
- **Adjacency probe.** Re-run `_corridor_census`'s loop using the test module's helpers, and
  histogram `_endpoint_gap(resolved)` against the route gap
  `min(tick - maximal_stays(route)[0].from_tick, maximal_stays(route)[-1].to_tick - tick)`.
- **Memo drift.** Run `cf.run(list(cf.CANONICAL_SETS))`, then compare each surface with the test
  module's own parsers: `_published_tables`, `_memo_ballot_census`, `_memo_kind_census`,
  `_published_render_census`, `_memo_ledger_rows`, `_memo_class_totals` and `_advisory_cells`.
  No `AILIBI_*` variable was exported, which the script requires.
- **Registry row.** `git ls-files -z audits | xargs -0 stat -f %z | awk '{s+=$1; n+=1} END {print s, n}'`
  prints `26632967 329`.
