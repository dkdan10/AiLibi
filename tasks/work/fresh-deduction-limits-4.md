# Move the fresh-model deduction instrument to the fourth authorization's limits

**Status:** active

## Outcome

The instrument's authorized constants and the execution manifest's limits
table carry the fourth authorization's values — the raised turn cap and the
calibrated token ceilings — the feasibility gate accepts them, the Inputs
table binds the fourth held-out band, and a dated amendment records the
change before any unit of the fourth run exists. The frozen analysis does not
move.

## Evidence

[The fourth authorization](fresh-deduction-authorization-4.md) carries the
values with their basis: the live development calibration of 2026-09-14
(`audits/deduction-candidate/calibration-2026-09-14/calibration.json`) and the
near-cap candidate turn it recorded (2,036 output tokens against a 2,048 cap).
Today the instrument pins `AUTHORIZED_TURN_MAX_TOKENS = 2048`,
`AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS = 4000`, `AUTHORIZED_UNIT_MAX_INPUT_TOKENS =
45000`, `AUTHORIZED_RUN_MAX_INPUT_TOKENS = 2400000` and
`AUTHORIZED_RUN_MAX_OUTPUT_TOKENS = 200000`
(`experiments/fresh_deduction_instrument.py:205-210` and the sampling block
around `:389`), and `assert_limits_are_feasible` refuses them because one
unit's reservation schedule (`living_voters x (turn cap + vote cap)`,
`:463`) exceeds the per-unit output ceiling. The manifest's limits table
(`audits/deduction-candidate/execution-manifest.md`, "Sampling configuration,
caps and limits") quotes the constants and a test holds the two together; the
Inputs table binds band 6000-6999, which [the fourth freeze](held-out-prefix-freeze-4.md)
converts to development.

## Acceptance

- [x] Review correction: the Limitations no longer claim the re-sized run
  ceilings clear both per-unit output figures. They clear the archived 3,116
  (315,696 <= 459,000) and not the calibration's 4,590 (463,096 > 459,000), so
  the stale usage profile is load-bearing; the residual is recorded in the
  manifest's dated section, held by
  `test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit`
  and handed back to the authorization card and the owner, since 459,000 is not
  this card's to move.
- [x] Review correction: the fourth freeze is merged into this branch and the
  pull request is retargeted onto `work/held-out-prefix-freeze-4`, so the
  raised ceilings cannot reach `main` ahead of the band they are authorized
  against. The card's Constraints asked for exactly this and the delivery was
  based on `main` instead.
- [x] Review correction: the live path is closed on the merged tree by a
  mechanism rather than by the ordering of two pull requests. The Inputs row
  binds 6000-6999, the freeze record now holds 7000-7999, and
  `assert_manifest_binds_the_live_band` refuses the pair — which
  `test_the_committed_manifest_binds_the_live_band_or_is_refused` takes as its
  refusal branch on this tree, so no live invocation can spend the band the
  stopped third run already rendered.
- [x] Review correction: `assert_limits_are_feasible` adds the per-call
  reservation its parent budget pre-flights to the run-level OUTPUT
  comparison — 315,696 needed against the 459,000 this authorization binds —
  with a planted case at exactly 311,600, the figure the old comparison
  accepted. The INPUT comparison deliberately keeps no such term.
- [x] Review correction: the Results' planted cases and Verification table are
  repinned to `c97cc075` and re-run there, so every quoted figure reproduces at
  the commit the preamble names and the list of what moves after it is this
  card alone.
- [x] `AUTHORIZED_TURN_MAX_TOKENS` is 4,096, the vote cap stays 1,024, and the
  four token ceilings are 106,000 / 16,000 per unit and 3,710,000 / 459,000
  run-level, copied from the authorization card's Constraints table; the
  reservation schedule under the new caps is 15,360 and
  `assert_limits_are_feasible` accepts `AUTHORIZED_LIMITS` (a planted test
  with the old ceiling still goes red). The turn cap reaches the meeting
  layer's per-call `max_tokens` through the instrument's own sampling
  configuration, not through a default-path change; the default meeting
  path's recorded prompts and caps are unchanged (`verify_samples.sh`, the four
  `--check` runs).
- [x] The manifest's limits table carries the same values verbatim with the
  authorization card named as their source, the reservation-policy text states
  the new schedule, and a dated section "Fourth authorization (2026-09-14)"
  records the change and its basis; the test that pins the table to the
  constants passes and the frozen analysis strings are byte-identical (test).
- [ ] After [the fourth freeze](held-out-prefix-freeze-4.md) is merged into
  this branch, the Inputs table binds band 7000-7999 (band, accepted range,
  skip count from the new `audits/deduction-candidate/held-out/manifest.json`),
  names all three converted bands as development data with their dates and
  their record paths, including
  `audits/deduction-candidate/held-out/manifest-band-6000-6999.json`, which
  this row binds until then, and
  `assert_manifest_binds_the_live_band` passes against the merged record.
- [ ] The replay-double rehearsal of the full pipeline under the new limits
  clears the feasibility gate and completes at $0, and Results records its
  aggregate counts only.
- [x] Every new gate has a planted failure proving it detects the claimed
  defect.

## Constraints

No live provider call. The primary outcome, decision rule, minimum actionable
effect, tradeoff bound and stop rule do not change. The reservation policy of
the shared budgeted client does not change. Do not edit
`experiments/held_out_prefixes.py`; this card lands after
[the fourth freeze](held-out-prefix-freeze-4.md) and merges that branch in
before re-binding the Inputs table. If the turn cap can only reach the meeting
layer through `orchestrator/game.py`, stop and report rather than editing a
hashed default-path file. No band prefix is printed or opened; the rehearsal
writes to a temporary directory. Any `audits/` byte change recomputes the
`docs/artifacts.md` audits row.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`audits/deduction-candidate/execution-manifest.md`, `docs/artifacts.md` (the
`audits/` row), `tasks/README.md`'s derived inventory sentence, this card.
Delivered on `work/fresh-deduction-limits-4`, stacked on
`work/held-out-prefix-freeze-4`, one pull request into `main`.

## Record impact

Amends the execution manifest (an `audits/` document) with a dated section, a
re-bound Inputs table and new limit rows; no recording, report, DTO or weight
byte moves; no experiment becomes ON; no adopting record is created.

## Validation

`uv run pytest tests/experiments -q` (fake and replay providers only), then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, `bash scripts/verify_samples.sh`,
the four `uv run python scripts/build_sample_report.py --sample-dir <set>
--check` runs, and `bash scripts/check.sh`. Do not run the live evaluation as
a check.

## Results

The five review-correction items and the three original items 1, 2 and 5 are
done; items 3 and 4 are open, so the card is `active`.
[The fourth freeze](held-out-prefix-freeze-4.md) is now merged into this branch
and the pull request is retargeted onto `work/held-out-prefix-freeze-4`, which
is what the two open items were waiting for: the Inputs table's re-binding to
7000-7999 and the replay-double rehearsal on the band the run will draw land in
one further round and the card closes. Until they do, the committed tree binds
one band in the manifest and holds another in the freeze record, and
`assert_manifest_binds_the_live_band` refuses that pair — the live path fails
closed on this branch, which is the state the round-1 corrections below were
asked for.

**What moved.** `AUTHORIZED_TURN_MAX_TOKENS` is 4,096 (written as a number, no
longer read from `meetings.manager`), the vote cap is still the shipped 1,024,
and the four ceilings are 106,000 / 16,000 per unit and 3,710,000 / 459,000
run-level — every figure copied from
[the fourth authorization card](fresh-deduction-authorization-4.md)'s
Constraints table. `unit_output_reservation()` is therefore 15,360 and
`assert_limits_are_feasible()` accepts `AUTHORIZED_LIMITS`, which is the first
time the gate the diagnosis of 2026-09-13 installed has passed on the committed
numbers.

**The turn cap reaches the meeting layer through the instrument's own sampling
configuration**, not through a default-path file. `run_unit` already built its
runner with `config=sampling.meeting_config()`
(`experiments/fresh_deduction_instrument.py`, the `build_default_meeting_runner`
call), and `MeetingConfig.turn_max_tokens` is what `meetings/manager.py` passes
as each turn's `max_tokens`; raising `AUTHORIZED_TURN_MAX_TOKENS` moves that
value and nothing else. `meetings/manager.py`'s `DEFAULT_TURN_MAX_TOKENS` is
still 2,048 and `orchestrator/game.py` is untouched, so no recorded campaign
and no default meeting path draws differently. The four `--check` runs and
`verify_samples.sh` below confirm it against the recorded samples.

**The refusal is kept as a plant rather than retired with the defect.** The
4,000 ceiling merged on 2026-09-07 is still red — now against the wider
schedule — and the two gate tests that used to rely on the committed limits
being infeasible plant those ceilings as the authorized set instead of
asserting the tree's own numbers
(`test_the_live_run_path_fails_closed_under_infeasible_limits`,
`test_the_gate_runs_before_the_frozen_set_is_read`). The
`_authorize_feasible_limits` helper those tests shared existed only to work
around the committed limits being unpayable and is deleted.

**The calibration mode keeps the caps it drew at.** `CALIBRATION_LIMITS` is
untouched, as the card requires, and that is exactly why the calibration's draw
had to be frozen beside it: its 12,000 per-unit output ceiling pays for the
9,216-token schedule the 2,048 cap reserves and not for the 15,360 the raised
cap reserves, so following the run to 4,096 would have authorized six calls the
calibration's own ceilings cannot pay for — the defect
`assert_limits_are_feasible` exists to refuse, one authorization down. A new
`CALIBRATION_SAMPLING` holds the calibration's caps,
`assert_calibration_is_authorized` now requires it, and the committed
`calibration-2026-09-14/calibration.json` stays re-derivable from this tree (a
test compares its recorded `sampling` block to the constant). No second
calibration is authorized by anything here; sizing a run that draws at 4,096
would need its own calibration and its own ceilings, on a card.

### Planted and perturbed cases (pinned to `976f7a6b`)

Each is the claimed defect reintroduced, and each turns the gate red. Run from
the repository root with the change applied, then reverted.

1. The committed per-unit output ceiling put back to the 4,000 merged on
   2026-09-07 (`AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS: Final[int] = 4_000`):

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly -k test_the_gate_accepts_the_fourth_authorizations_limits
   ```

   ```
   E  experiments.fresh_deduction_instrument.LimitsInfeasible: the per-unit output ceiling is 4,000 tokens and one unit reserves 15,360 (3 x 4,096 + 3 x 1,024): this run authorizes calls it cannot pay for, and the budget would refuse one of them on the reservation rather than on the spend
   FAILED ...::TestFeasibility::test_the_gate_accepts_the_fourth_authorizations_limits
   1 failed, 311 deselected
   ```

   The same defect is held from the other side by
   `test_the_ceilings_merged_on_2026_09_07_are_still_refused`, which plants that
   ceiling and requires the refusal to name both 4,000 and 15,360.

2. `CALIBRATION_SAMPLING` made to follow the run's raised cap
   (`turn_max_tokens=AUTHORIZED_TURN_MAX_TOKENS`):

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly -k "calibration_at_its_own_caps or kept_the_caps_it_drew_at"
   ```

   ```
   E  experiments.fresh_deduction_instrument.LimitsInfeasible: the per-unit output ceiling is 12,000 tokens and one unit reserves 15,360 ...
   E  assert 4096 == 2048
   FAILED ...::TestCalibrationGate::test_the_feasibility_gate_accepts_the_calibration_at_its_own_caps
   FAILED ...::TestAuthorizedConstants::test_the_calibration_kept_the_caps_it_drew_at
   2 failed, 310 deselected
   ```

3. The dated manifest section's reservation arithmetic replaced by a phrase
   ("`3 x 4,096 + 3 x 1,024 = 15,360`" to "the raised reservation schedule"):

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly -k fourth_authorization_section
   ```

   ```
   E  AssertionError: 3 x 4,096 + 3 x 1,024 = 15,360
   FAILED ...::TestExecutionManifest::test_the_fourth_authorization_section_records_the_change_and_its_basis
   1 failed, 311 deselected
   ```

4. The run-level reservation term removed from the feasibility gate
   (`needed = calibrated * planned + in_flight` back to `needed = calibrated *
   planned`), which is the defect the round-1 correction below repairs:

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly \
     -k "run_output_ceiling_sized_at_exactly_its_units or run_ceiling_below_its_own_units \
         or calibrations_largest_unit"
   ```

   ```
   E  Failed: DID NOT RAISE <class 'experiments.fresh_deduction_instrument.LimitsInfeasible'>
   FAILED ...::TestFeasibility::test_a_run_ceiling_below_its_own_units_is_refused[run_max_output_tokens-output-4096]
   FAILED ...::TestFeasibility::test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused
   FAILED ...::TestFeasibility::test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit
   3 failed, 1 passed, 308 deselected
   ```

   The INPUT case of the same parametrisation stays green under the
   perturbation, which is what says the term belongs to the output dimension
   alone rather than to both. The third failure is round 2's case, below: it
   plants the usage profile refreshed to the calibration's own figures, and the
   same missing term is what would let 459,000 pay for a hundred units at
   4,590.

5. The manifest's reservation-policy quotation paraphrased (the run-level
   turn-cap sentence replaced by "the run-level OUTPUT ceiling also carries
   some headroom for the call in flight"):

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly -k enforcement_section_quotes_the_reservation_policy
   ```

   ```
   E  assert "The token ceilings are enforced on RESERVED spend ... rather than a cap." in '### How each limit is enforced ...'
   FAILED ...::TestExecutionManifest::test_the_enforcement_section_quotes_the_reservation_policy
   1 failed, 311 deselected
   ```

A sixth case is already committed rather than demonstrated by hand: the
per-call cap gate is parametrized over 8,192, 2,048 and 512, and 2,048 — the
shipped turn default, an authorized cap until 2026-09-14 — is now refused by
`_InstrumentClient`, so a caller still drawing at the old cap is a stop rather
than a silent second distribution.

### Verification

Every command below was re-run on this branch at `976f7a6b`, round 2's commit,
which carries the whole change: the merge of
[the fourth freeze](held-out-prefix-freeze-4.md), every instrument, test and
manifest byte, the recomputed `docs/artifacts.md` audits row and the recomputed
task index. The ONLY bytes that move after it are this card's `## Acceptance`
and `## Results`, so every figure in the table reproduces at `976f7a6b` and
again at the head; `validate_task_docs.py` and `check.sh` were re-run after this
card's own commit and returned the same results. The two counts that moved from
round 1's table are the test the round-2 correction adds (392 to 393 in
`tests/experiments`, 7,704 to 7,705 under `check.sh`). No command below reads a
held-out prefix.

| Command | Result |
| --- | --- |
| `uv run pytest tests/experiments -q` | 393 passed (fake and replay providers only; no live call) |
| `uv run python scripts/validate_task_docs.py` | pass (55 work cards) |
| `uv run python scripts/check_doc_facts.py` | pass |
| `uv run python scripts/verify_ml_evidence.py` | 60 checks, 48 OK, 0 FAIL, 7 EVIDENCE-BRANCH-ABSENT, 5 INFO |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/verify_samples.sh` | 4p1i and 9p2i, all 50 samples each, clean |
| `scripts/build_sample_report.py --sample-dir <set> --check` x 4 | `replays/samples/{4p1i,9p2i}` and `replays/ml_corpus/{4p1i,9p2i}` all consistent with their replays |
| `bash scripts/check.sh` | exit 0: 7,705 passed / 20 skipped / 3 xfailed, 515 frontend tests, strict mypy over 477 files, ruff clean, production build |

`docs/artifacts.md`'s `audits/` row is recomputed for the merged tree and the
manifest's changed bytes — round 1's and round 2's: 15,091,970 tracked bytes
over 211 files, the file count moving because the freeze merged in adds
`held-out/manifest-band-6000-6999.json` and the byte count moving again with the
round-2 paragraph the manifest's dated section gains. The task index's derived
inventory is recomputed for the same merge (1 ready, 2 active, 52 done) and does
not move in round 2, because no card's Status flips.

### Limitations

- The Inputs table still binds 6000-6999 and the verification section's dry-run
  and rehearsal figures are still the third band's, labelled as such in the
  document. Both are items 3 and 4, in the later round. With the freeze merged
  in, that stale binding is no longer only a documentation gap: it is what
  `assert_manifest_binds_the_live_band` refuses, so the live path is shut until
  the row moves.
- The manifest's headroom figures are re-expressed against the new ceilings
  from the SAME committed rehearsal rather than from a fresh one: the replay
  double's spend does not depend on a cap it never reaches, so the arm totals
  are byte-identical and only the percentages move. The rehearsal item 4 owes
  is a new run on the new band, and it is not claimed here.
- `tests/experiments/deduction_usage_profile.json` is unchanged, so
  `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` are still
  the three stopped live runs' largest unit (24,282 / 3,116) rather than the
  calibration's (35,232 / 4,590). The stale profile is LOAD-BEARING, not
  neutral: the run-level OUTPUT ceiling clears the archived figure
  (100 x 3,116 + 4,096 = 315,696 against 459,000) but NOT the calibration's
  (100 x 4,590 + 4,096 = 463,096 against the same 459,000), so the corrected
  gate accepts `AUTHORIZED_LIMITS` on the archived figure alone. 459,000 is a
  hundred units at 4,590 to the token — exactly the shape this card's own
  `test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused` declares
  infeasible. The INPUT dimension clears either figure (100 x 35,232 =
  3,523,200 against 3,710,000), so the residual is one comparison wide. This
  card may not move 459,000 — it is the owner's, on
  [the fourth authorization card](fresh-deduction-authorization-4.md) — so the
  residual is handed back there and to the owner, alongside the profile refresh
  [the calibration card](fresh-deduction-calibration.md)'s Results already left
  open; `test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit`
  holds it so it cannot be lost. Codex's second P1 is therefore repaired in the
  gate but not fully closed in the numbers, and round 2 below says which half is
  which.
- `assert_calibration_is_authorized` now refuses a live calibration drawn at the
  run's cap. Nothing is authorized to run one, so this is a closed door rather
  than a regression, but it is stated: a future calibration needs a card that
  carries both a draw and ceilings that pay for it.

### Review corrections, round 1 (2026-09-14)

Four blocking findings, two of them Codex comments on `2962c44e` that the first
round left unanswered. Each is repaired by a mechanism on this branch rather
than by a note, and the reasoning is written here because this worker posts no
pull-request comments.

**The pull request was delivered unstacked, so the raised ceilings could have
merged first.** The card's Constraints say this card lands after
[the fourth freeze](held-out-prefix-freeze-4.md) and merges that branch in, and
Expected scope says it is stacked on `work/held-out-prefix-freeze-4`; the
delivery was based on `main` and mergeable there. `work/held-out-prefix-freeze-4`
is now merged into this branch (merge commit `38bad13e`, the freeze branch's
side taken on both derived lines) and the pull request is retargeted onto it.

**Raising the ceiling opened a green live-run path onto a band already
rendered.** This card is the first to make `assert_limits_are_feasible` accept
`AUTHORIZED_LIMITS`, and that gate runs FIRST in `assert_ready_for_a_live_run`,
so before it the arithmetic alone stopped every live path — including onto
6000-6999, which the stopped third run rendered. The merge closes it by
mechanism, not by ordering: `PREREGISTERED_BAND` and the committed freeze
record are now 7000-7999 while the manifest's Inputs row still binds
6000-6999, and `assert_manifest_binds_the_live_band` refuses that pair inside
`assert_live_run_is_authorized`, before a provider, a credential or a
connection exists. On this tree:

```
.venv/bin/python -c "from experiments import fresh_deduction_instrument as i; i.assert_manifest_binds_the_live_band()"
```

```
experiments.fresh_deduction_instrument.LiveRunNotAuthorized: audits/deduction-candidate/execution-manifest.md binds seed band 6000-6999, but the held-out record at audits/deduction-candidate/held-out/manifest.json holds 7000-7999: the authorization was written for one band and this run would spend another
```

That refusal is not incidental to the tests: at `c97cc075`
`test_the_committed_manifest_binds_the_live_band_or_is_refused` takes its
refusal branch on the committed tree and requires the message to name both
bands, and `_root_binding_the_live_band` plants a rebound COPY for the cases
that are about what happens after this check passes. Item 3 re-binds the row to
7000-7999 in the next round; until it does, the live path stays shut.

**The run-level feasibility check had no reservation term.** Codex's second P1,
and it reproduces: `GameBudget.preflight` recurses into its parent
(`llm/budget.py`), so the RUN budget sees a call's full output cap added to
everything the run has already charged, exactly as the unit budget does. The
gate's own docstring claimed it closed "the same two-units-of-account defect one
level up", but its two run-level comparisons were the only ones with no
reservation term, and the authorization card sizes run output as exactly a
hundred units at the largest measured unit (100 x 4,590 = 459,000) — an
arithmetic that at its own bound, 311,600 against the archived 3,116, could not
have paid for the hundredth unit's last call. `assert_limits_are_feasible` now
adds one turn cap to the run-level OUTPUT comparison: 315,696 needed against
the 459,000 this authorization binds, so the gate still accepts
`AUTHORIZED_LIMITS` and no authorized figure moves. The INPUT comparison keeps
no such term, because an input pre-flight is the prompt's own estimated length
rather than a cap (`llm/budgeted_client.py`'s `estimate`); planted case 4 above
shows the output half going red and the input half staying green under the same
perturbation. `RESERVATION_POLICY` states the term, the manifest quotes it
verbatim, its enforcement paragraph names 315,696 against 459,000, and a
round-1 correction note inside the dated "Fourth authorization (2026-09-14)"
section records the change and that it moves no authorized number.

**The Verification preamble was pinned to a commit where two of its counts did
not reproduce.** It named `b80cb92e` while `390 passed` and `7,702 passed` were
head figures, and its list of what moved after that commit omitted the test
file and `docs/artifacts.md`. The whole section is repinned to `c97cc075` and
every command re-run there — eight commands, all eight in the table above — and
the planted-and-perturbed subsection is repinned with it, because case 3's test
did not exist at `b80cb92e` and the deselect counts moved with the merged
tests. After `c97cc075` only this card's `## Acceptance` and `## Results` move.

Nothing else in this round touches a recording, a report, a DTO, a weight or a
default-path byte; no experiment becomes ON; `experiments/held_out_prefixes.py`
is unedited by this card and arrives only through the merge; no prefix is
printed, opened or committed, and no provider call is made.

### Review corrections, round 2 (2026-09-14)

One blocking finding, and it holds. The round-1 entry above reported Codex's
second P1 closed; it is closed in the gate and not in the numbers, and the
Limitations said the opposite.

**"The re-sized run ceilings clear both figures" was false on the OUTPUT
dimension.** The corrected run-level bound is 315,696 only because
`CALIBRATED_UNIT_OUTPUT_TOKENS` is the three stopped runs' archived 3,116. The
ceiling this authorization binds was sized from the OTHER figure — the
calibration of 2026-09-14's largest measured unit, 4,590 — and 100 x 4,590 is
459,000 to the token, which is exactly the shape
`test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused` declares
infeasible. Forcing the two calibrated constants to the calibration's own
figures at `976f7a6b` refuses `AUTHORIZED_LIMITS`:

```
.venv/bin/python -c "from experiments import fresh_deduction_instrument as i; \
  i.CALIBRATED_UNIT_OUTPUT_TOKENS = 4590; i.CALIBRATED_UNIT_INPUT_TOKENS = 35232; \
  i.assert_limits_are_feasible()"
```

```
experiments.fresh_deduction_instrument.LimitsInfeasible: the run-level output ceiling is 459,000 tokens and 100 units at the largest unit the live archives charged (4,590), plus the 4,096 its last call reserves against the run budget on top of them, need 463,096: a run this long would stop on the run ceiling rather than on its own evidence
```

The INPUT dimension clears either figure (100 x 35,232 = 3,523,200 against
3,710,000), so the residual is one comparison wide. The consequence for this
card's claims is the one the finding names: the gate accepts `AUTHORIZED_LIMITS`
on the archived figure ALONE, so the stale usage profile is load-bearing rather
than neutral, and the Limitations bullet now says that in those words rather
than claiming both figures clear.

**What this round does and does not repair.** It does not move 459,000: that
number is the owner's, copied verbatim from
[the fourth authorization card](fresh-deduction-authorization-4.md)'s
Constraints table, and this card's Constraints bind it. A residual that only a
new authorized ceiling can close is therefore handed back rather than papered
over — to that card and to the owner, alongside the profile refresh
[the calibration card](fresh-deduction-calibration.md)'s Results already left
open. Whichever of the two is done first, the other has to follow, because the
ceiling and the profile are the two sides of one comparison: a refresh without a
raise turns `test_the_gate_accepts_the_fourth_authorizations_limits` red, and a
raise without a refresh leaves the gate checking a figure the calibration has
superseded. Three mechanisms hold it so it cannot be lost:
`test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit`
plants the refresh and requires the refusal (reading both measured figures off
the committed `calibration-2026-09-14/calibration.json` rather than restating
them, and asserting `100 x 4,590 == 459,000` so the case dissolves the day the
ceiling moves); the manifest's dated section gains a "Round-2 review
correction" paragraph a runner reads before the run; and the Limitations bullet
states which half of Codex's second P1 is closed.

Nothing else in this round moves: no authorized figure, no recording, report,
DTO or weight byte, no default-path byte, no experiment to ON,
`experiments/held_out_prefixes.py` unedited, no prefix printed, opened or
committed, and no provider call. `docs/artifacts.md`'s `audits/` row is
recomputed for the manifest's new bytes and the Verification section above is
re-run and repinned to `976f7a6b`.
