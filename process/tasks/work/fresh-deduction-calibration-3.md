# Run a third development calibration that measures the revised wave

**Status:** done

## Outcome

A third dated calibration mode, beside the two spent ones and replacing neither,
renders sixty paired seeds of DEVELOPMENT inputs with the whole revised wave
enabled on both arms, at the run's own sampling. The draw is the converted
records' first sixty accepted seeds, which is calibration 2's draw to the seed,
so the token profile compares on identical inputs and the wave's prompt bytes
are the only thing that moved. Per arm it reports the token profile by call type
and hidden role, truncations as measurements carrying their `finish_reason`, the
leak column, and the diagnostics block the diagnostics card builds. It computes
NO paired statistic, evaluates NO decision rule and reports NO primary outcome.
The predictions it is read against are fixed here before the sitting, and the
owner's merge authorizes its limits.

## Evidence

[The diagnosis of 2026-09-18](../diagnosis-2026-09-18-fifth-run.md), whose ten
decisions the owner approved as a set that day with the rulings in its section
11, is decision 1: revise and evaluate a new version. Its section 7 pairs F6
with F7 and refuses F4 alone, and section 10.8 makes both stages load-bearing.
This is the first spend after that wave, and a development measurement rather
than the evaluation: it asks whether the three cards did what section 7 predicts
before a held-out band is touched.

**The draw is the shipped one, named in the clause.**
`_draw_in_converted_order` (`experiments/fresh_deduction_instrument.py:3448`,
refusal at `:3499-3508`) holds a draw to a PREFIX of `CONVERTED_BANDS` from the
first record with none skipped, and `verify_calibration_set` (`:3270`) rebuilds
`accepted[:drawn]` with no offset (`:3378-3381`), holding every prefix to the
digest that record froze (`:3381-3390`). Sixty seeds is therefore all fifty
accepted seeds of `held-out/manifest-band-3000-3999.json` (3000 to 3057) then
the first ten of `held-out/manifest-band-5000-5999.json` (5000 to 5009), which
is calibration 2's draw to the seed.

**Band 8000-8999 is not drawable here, and this card does not wait for it.** The
fifth run rendered every accepted seed of it, so those prefixes are development
data by the preregistration, but the record is still the live held-out one at
`MANIFEST_PATH` (`experiments/held_out_prefixes.py:146`): `_converted_band_for`
(`:3241`) refuses that path BY NAME first (`:3252-3258`) and
`verify_calibration_set` refuses a record not marked `development`
(`:3316-3322`). Only a freeze card moves and flips it, and
[the sixth freeze](held-out-prefix-freeze-6.md) is dispatched after this
calibration reports. So this sitting never names that record, and the
predictions below are read against the fifth run's figures on DIFFERENT
prefixes, which makes them directional readings and none of them a gate.

**The sizing profile has to become the mode's.**
`assert_ready_for_a_calibration` passes `CALIBRATION_SIZING_UNIT_INPUT_TOKENS`
and its output twin (`:3613-3614`), 24,282 / 3,116, to the feasibility gate for
BOTH modes, and `:561-579` says why: each spent mode's ceilings record a spend
already made. This mode is sized on the profile that exists today, 38,440 /
4,176 (`:558-559`), which calibration 2 measured on these same sixty seeds at
accounts revision v4. Against 24,282 the gate passes anything, 120 units of it
being 2,913,840; against 38,440 it bites at 4,612,800. It must be a frozen
literal on the mode, or the refresh
[the limits card](fresh-deduction-limits-6.md) makes from THIS sitting would
re-point this mode's gate at its own measurement.

The report shape is calibration 2's; new is only the diagnostics block, which
[the diagnostics card](fresh-deduction-instrument-diagnostics.md) builds.

**The predictions, fixed before the sitting**, read from memo section 7 against
the fifth run's own figures. None is a gate.

| # | Mechanism | Fifth run | Prediction |
| --- | --- | --- | --- |
| P1 | F6 costs the impostor its free pass (§3) | impostor EJECTs survive 86.8%, crew 51.9% | the gap narrows |
| P2 | F6 attacks stage 2 (§2) | wrongful coalitions convert 36.4%, correct 18.2% | wrongful falls to or below correct |
| P3 | F7 equalises the register (§4) | candidate authors 119 EJECT / 31 SKIP of 150 | authored EJECTs fall toward 14 |
| P4 | F4 revives the turn channel (§3) | 0 of 150 keep a `primary_reason_id`; 27 nulled; 44 coerced | surviving ids rise, coercions fall |
| P5 | The deduction signal is real (§5) | crew authored EJECTs name the impostor 51 of 81 | holds near 63% once volume falls |
| P6 | The vocabulary un-collapses (§4) | 1 contradiction flag against 14 | flags rise above 1 |

## Acceptance

- [x] Review correction: P2 is re-labelled **did not hold**. The manifest's
  prediction is that the wrongful coalition conversion rate FALLS to or below the
  correct one; it rose, 36.4% (8 of 22) to 100.0% (8 of 8), and its order against
  the correct rate is a tie at the ceiling on a correct denominator of one. The
  first publication called that "held by the letter, on n = 1", which reads the
  relative-order clause as the whole prediction and drops the fall the F6
  mechanism claim rests on. The verdict cell, the tally, the Limitations bullet
  and the three documents the "four held" headline reached —
  `audits/deduction-candidate/calibration-3-2026-09-18/CALIBRATION.md`,
  `audits/deduction-candidate/README.md` and
  `audits/deduction-candidate/checkpoint.md` — now read three held (P1, P3, P4)
  and three did not (P2, P5, P6). The prediction's own text does NOT move: it is
  frozen before the sitting in the manifest and in this card's Evidence table,
  and `TestTheSixPredictionsAreFixedBeforeTheSitting`
  (`test_the_module_carries_the_cards_six_rows`,
  `test_the_manifest_copies_them_verbatim`) holds those two copies and the
  module's `CALIBRATION_3_PREDICTIONS` to the same six rows.
- [x] Review correction: the four replay-derived figures are marked as NOT
  reproducible from committed bytes, with the clause that authorizes it named.
  AGENTS.md craft rule 5 (`AGENTS.md:68-69`) requires numbers reproducible from
  committed evidence; the recorded EJECT/SKIP column, the surviving and nulled
  `primary_reason_id` counts, the contradiction flags and the claim vocabulary
  are read off replays the manifest's "Development calibration 3 (2026-09-18)"
  section puts outside version control by name, and this card's aggregates item
  restates. The record now separates what DOES recompute from `calibration.json`
  (P4's coercion half via `guard_rewrites_by_reason.uncited_coerced`, P3's
  numerator via `by_voter_role[].authored` = 23 and 39) from what does not (P4's
  surviving-id half, all of P6), marks the verdict cells and the section header,
  and routes the closing repair — those four counters in `authored_diagnostics` —
  to the sixth authorization's instrument work, an instrument byte this run pull
  request may not move.
- [x] Review correction: the archived `role_leak_rule` is dispositioned. It is
  the live evaluation's `ROLE_LEAK_RULE`, which calls the leak count a column
  "beside the primary outcome" in a payload that reports none — the defect this
  card already repaired for `AUTHORED_DIAGNOSTICS_NOTE` and not for this string.
  `ROLE_LEAK_RULE` is an instrument constant, so the calibration-specific or
  outcome-neutral description is routed to the sixth authorization's instrument
  work beside the item above, and the live text stays byte-identical because it
  is what the live run publishes under. The record states that both clauses argue
  the column is not a gate, which is also this mode's position, and that the
  count is 0 on both arms with no outcome beside it to read.
- [x] Review correction: the 11.2% ballot-input rise is re-stated as an OBSERVED
  cross-sitting difference rather than as the wave's template bytes. A seed holds
  the scripted prefix constant and not the meeting the sitting generates, and a
  ballot prompt renders that generated transcript: this sitting's candidate turn
  output mean is 476.2 against the 2026-09-15 sitting's 443.0 on the same sixty
  seeds. The record now says the figure mixes static template bytes with the
  growth of the transcript they produce, that separating them needs a
  controlled-transcript measurement no sitting has made, and that the sizing
  conclusion is unaffected — the largest charged unit is 34,412 input however the
  rise is apportioned.
- [x] Review correction: `## Results` counts its own boxes. Its opening
  paragraph numbered the outstanding items one low — it called the committed
  aggregates item 8 and the live sitting item 9, against a list whose item 8 is
  `CEILING_PROPOSAL_RULE` and is checked — so a reader reconciling the prose
  against the boxes met a contradiction about what is outstanding. Renumbered
  against the list as it now stands, review corrections included, and re-derived
  by `uv run python scripts/validate_task_docs.py`, which holds a `done` card to
  no unchecked box and this `active` one to the inventory sentence.
- [x] Review correction: the 2026-09-18 artifact no longer publishes the live
  evaluation's `AUTHORED_DIAGNOSTICS_NOTE`, which says the counts are "reported
  beside the primary outcome" and that a cross-arm reading is confounded "until
  the v5 prompt set equalises the register" — both false of a payload that
  reports no primary outcome and renders v5 on both arms. The block's note is a
  parameter, `CALIBRATION_DIAGNOSTICS_NOTES` names one per reporting mode, and
  `assert_every_reporting_mode_has_its_note` refuses a table that does not match
  the modes or that points a calibration at the live note. Proved by
  `test_the_published_block_is_not_the_live_runs_note`,
  `test_the_third_modes_block_publishes_its_own_note`,
  `test_a_note_table_that_does_not_match_the_modes_is_refused` (planted three
  ways) and `test_a_calibration_may_not_publish_the_live_runs_note`.
- [x] A THIRD dated clause and constant set beside the 2026-09-14 and
  2026-09-15 sets, neither edited: `CALIBRATION_3_PAIRED_SEEDS = 60`,
  `CALIBRATION_3_LIMITS`, `CALIBRATION_3_SAMPLING` equal to
  `AUTHORIZED_SAMPLING` (`:438`), a `CALIBRATION_3_CLAUSE` the manifest quotes
  verbatim, and a third `CalibrationMode` (`:1519`) in `CALIBRATION_MODES`
  (`:1551`) carrying `truncation_is_a_measurement=True`. `calibration_mode_for`
  (`:1580`) accepts exactly one mode whole. Planted: sixty seeds under the
  2026-09-15 mode's limits, and this mode's limits at the 2026-09-14 sampling.
- [x] The clause NAMES the draw and the shipped rule verifies it: all fifty
  accepted seeds of `held-out/manifest-band-3000-3999.json` then the first ten
  of `held-out/manifest-band-5000-5999.json` (5000 to 5009). A test asserts
  `verify_calibration_draw` at `CALIBRATION_3_PAIRED_SEEDS` yields exactly those
  sixty seeds, with `_draw_in_converted_order` (`:3448`) and
  `verify_calibration_set` (`:3270`) untouched, the held-out record at
  `MANIFEST_PATH` still refused by name inside them, and every prefix rebuilt to
  the digest its record froze (`:3381-3390`). A second test asserts the draw is
  the same sixty seeds after a sixth band is APPENDED to `CONVERTED_BANDS`,
  since a prefix draw cannot reach it. Planted: a list naming the held-out
  record, a `status` that is not `development`, a moved prefix digest, a record
  named twice, and a draw of fifty-nine.
- [x] The feasibility gate bites on this mode's own sizing profile. The profile
  a mode's ceilings were sized against becomes a frozen field of
  `CalibrationMode`, 24,282 / 3,116 on the two spent modes and 38,440 / 4,176 on
  this one, and `assert_ready_for_a_calibration` (`:3613-3614`) passes the
  matched mode's pair. `assert_limits_are_feasible` (`:1306`) then accepts the
  Constraints table for 120 units: per-unit output 16,000 over the 15,360
  schedule (`unit_output_reservation`, `:603`), per-unit input 116,000 over
  38,440, run input 4,700,000 over 4,612,800, run output 520,000 over 120 x
  4,176 + 4,096 = 505,216. Planted: a run-level input ceiling of 4,600,000,
  refused here and passing against 24,282.
- [x] Both arms run with the wave enabled: the v5 accounts prompts on the
  candidate ([their card](accounts-prompt-set-v5.md)) and
  `citation_relevance_version=1` on BOTH arms
  ([the guard card](relevance-aware-citation-guard.md)). That lever's declared
  default stays `None`, on the pattern of `EXPERIMENT_ENV_NAMES`
  (`meetings/evidence_profile.py:25`) and `MeetingEvidenceProfile` (`:67`),
  mirrored at `orchestrator/experiment_config.py:42-45`, where `None` preserves
  recorded behaviour; this sitting passes it explicitly and the report records
  the resolved profile per arm. Planted: mode 3 with the guard resolved OFF on
  either arm is refused before a client exists.
- [x] In THIS mode a per-call truncation is a measurement, as in the 2026-09-15
  mode: the cap branch that builds `PerCallCapExceeded` (`:2815`) does not raise
  here, the call takes the meeting layer's shipped fail-soft, and it is counted
  per arm, per call type and per role with its `finish_reason`. `STOP_RULE`
  (`:722`) is not edited and the live path still stops. Planted: a live
  evaluation invocation still raises on that response.
- [x] The report carries, per arm and as aggregates: calibration 2's
  `by_call_type` and `by_role` profile, the truncation rows, the leak column
  under `ROLE_LEAK_RULE` (`:6216`), and the diagnostics block, which is authored
  precision with its harm counter on the same denominator, the coalition funnel,
  gate survival by role, guard rewrite reasons over `BallotTargetRewriteReason`
  (`meetings/schemas.py:727-733`) including the guard card's
  `off_target_coerced`, and ejections by role-correctness. Counts only: no
  prose, prompt, prefix or per-seed outcome, with
  `assert_report_holds_no_prefix_bytes` (`:4808`) over the payload.
- [x] This mode carries its OWN caveat beside `CALIBRATION_CAVEAT` (`:6093`),
  which stays byte-identical, being what the two spent sittings were published
  under. The new string says what is and is not reported: aggregate ballot and
  ejection diagnostics off development units, no primary outcome, no paired
  statistic, no decision rule. Planted: a mode-3 report carrying a `paired`
  block or a `supported_correct_ejection` field is refused.
- [x] `CEILING_PROPOSAL_RULE` (`:6061`) and `ceiling_proposal` (`:6934`) are
  unchanged and the proposal is published for the hundred-unit run as
  calibration 2's was, while the refresh it feeds stays out of scope.
- [x] Aggregates committed under
  `audits/deduction-candidate/calibration-3-<date>/` in the shape calibration 2
  committed, with per-unit usage rows; replays go to the runner's
  `--output-dir`, outside version control, which is where a per-seed reading of
  the predictions is available. The manifest gains a dated "Development
  calibration 3" section: the clause verbatim, the named draw with each record's
  sha256 and seeds, the limits and sampling table, the lever settings, and the
  six predictions copied verbatim as predictions rather than gates, with the
  sentence that a miss is neither a stop nor a verdict. A test holds the card's
  table and the manifest's copy to the same six rows; the frozen analysis
  strings stay byte-identical and no earlier dated section is edited. The
  manifest half was committed by the implementer; the aggregates are now at
  [`calibration-3-2026-09-18/`](../../audits/deduction-candidate/calibration-3-2026-09-18/CALIBRATION.md)
  — `calibration.json` (206,332 bytes), `unit-usage.jsonl` (120 rows),
  `calibration-run.log` and `CALIBRATION.md` — with the replays in the runner's
  `--output-dir` outside version control and nothing committed from them but
  counts.
- [x] The live sitting runs once, by a separate runner session on
  `work/fresh-deduction-calibration-3-run` under the manifest's calibration-3
  clause. Its Results subsection records the profile, the truncation rows, the
  leak counts, the diagnostics block, each prediction as met or missed, the
  proposal, usage at $0.00 and the archive path. Ran `2026-09-18T17:17:08Z` to
  `2026-09-18T20:16:13Z`, exit 0, all 120 units and all 721 attempts, once and
  not resumed: `### The live sitting (2026-09-18)` below.

## Constraints

Stacked on all three wave cards, [v5 accounts](accounts-prompt-set-v5.md),
[the diagnostics](fresh-deduction-instrument-diagnostics.md) and
[the guard](relevance-aware-citation-guard.md). The values below are the ones
the owner's merge authorizes:

| Field | Value |
| --- | --- |
| Paired seeds | 60: all fifty of `manifest-band-3000-3999.json`, then 5000-5009 of `manifest-band-5000-5999.json` |
| Units and calls | 120 units (60 paired seeds x 2 arms), about 720 model calls |
| Provider and model | `featherless`, `Qwen/Qwen3.6-27B`, non-thinking, `json_object`, prompt set `qwen3_6_27b`, carried from the model lock |
| Per-call token cap | turn 4,096 output / vote 1,024, `AUTHORIZED_SAMPLING`, so the draw is the one a run makes |
| Per-unit token ceiling | 116,000 input / 16,000 output |
| Run-level token ceiling | 4,700,000 input / 520,000 output |
| Wall-clock deadline | 5 h of model work within a 6 h elapsed deadline, one sitting |
| Transport bound | 4 attempts per call at a 180 s per-attempt wall, unchanged |
| Dollar limit | $0.00 marginal, the flat-rate subscription and the run's cost statement |

The run-level pair carries margin over the floors the gate enforces, 1.9% on
input and 2.9% on output, because the wave adds prompt bytes to the candidate
ballot that no calibration has measured: a ceiling pinned at the floor is a stop
rule on the first unit larger than any of calibration 2's. The wall is the
binding limit. 720 calls in 5 h allows 25.0 s per call, against about 12.9 s on
the fifth run's candidate arm (3,897.6 s over 301 calls) and 11.65 s per attempt
on calibration 2's candidate arm, a margin of 1.9x at the slowest pace measured
on these inputs. A calibration has no checkpoint and no resume: a stop is
reported with its partial accounting, and a second sitting needs the owner.

The usage-profile refresh this sitting feeds, the two calibrated constants at
`:558-559` and their dependent test
`test_the_calibration_is_the_largest_unit_the_archives_charged`
(`tests/experiments/test_fresh_deduction_instrument.py:5123`) belong to
[the limits card](fresh-deduction-limits-6.md), not to this card and not to the
runner: that is calibration 2's hand-back, settled in advance this time.

This is the only live spend the card authorizes. No held-out band is read,
rendered or converted; the record at `MANIFEST_PATH` is refused by name and
untouched, and this draw never names it, before or after
[the sixth freeze](held-out-prefix-freeze-6.md). No grader runs, no paired
statistic is computed and no primary outcome is reported, so no unit reaches the
frozen analysis. The live run's primary outcome (`:659`), decision rule
(`:677`), minimum actionable effect (`:672`), `WRONGFUL_EJECTION_TRADEOFF`
(`:693`) and `STOP_RULE` (`:722`) do not change, and per decision 7 the tradeoff
is not restated; the truncation relaxation is scoped to this mode. F5 and F8 are
out of scope of every card of this wave. Prompt-byte and meeting-layer changes
belong to the wave cards and stay behind their default-OFF levers; this card
changes no prompt byte and makes no recording, re-record or re-scored report.
`agents/` does not import `engine/`; the four contracts at `.importlinter:20-52`
are untouched, and `experiments/` is deliberately outside the root packages
(`.importlinter:5-7`), so "meetings/ must not import experiments/" is a design
rule this card restates rather than a linter gate. Stacked after all three wave
cards, this is the only writer on the instrument, and the runner is not this
card's implementer.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`audits/deduction-candidate/execution-manifest.md`,
`audits/deduction-candidate/calibration-3-<date>/` (the sitting's outputs),
`docs/artifacts.md` (the `audits/` row, today 25,974,591 tracked bytes / 324
files at `:109`), `tasks/README.md`'s derived inventory sentence, this card. The
committed usage profile and the calibrated constants are NOT in scope.

Delivered on `work/fresh-deduction-calibration-3`, based on the last of the
three wave branches to merge and retargeted onto `main` once all three have
landed, as one pull request into `main`; merge commit or fast-forward, never
squash; trailer `Card: tasks/work/fresh-deduction-calibration-3.md`. Every gate
an acceptance item adds carries a planted failure, and any `audits/` byte change
recomputes the audits row. The live sitting lands on a second pull request from
`work/fresh-deduction-calibration-3-run`. Once this calibration reports, the
sixth authorization opens with [its limits card](fresh-deduction-limits-6.md)
and [the sixth freeze](held-out-prefix-freeze-6.md) dispatched alongside it.

## Record impact

Adds a third calibration mode and one dated manifest section; adds a measurement
record under `audits/` when the sitting runs. The arm-surface digest moves
because the instrument is in `ARM_SURFACE_SOURCES` (`:4927`): a fresh stamp
before the sixth run, not a re-record. No recording, report, DTO, metric or
weight byte moves; no experiment becomes ON by default; no adopting record; the
committed usage profile and the two calibrated constants do not move here; the
held-out record at `MANIFEST_PATH` is untouched.

## Validation

`uv run pytest tests/experiments -q` (fake and replay doubles only, at $0), then
`uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh` run whole, in a clean worktree, so no gate after the
first failure is masked. Neither the live calibration nor the live evaluation is
a check here.

## Results

**Status `done`, and why.** `## Acceptance` carries SIXTEEN items: this round's
FOUR review corrections, prepended and checked; the two review corrections of
round 1 after them; and the card's original ten. All sixteen are now met and
checked.

Items 5-14 were met by the implementer, on `work/fresh-deduction-calibration-3`,
merged as PR #469 (`ef8081c3`); everything below `### The design this follows`
and above `### The live sitting (2026-09-18)` is that session's record and is
unedited apart from the two cells `### Review corrections (2026-09-19)` names.
Item 15 was split there: its manifest half — the dated "Development calibration 3
(2026-09-18)" section, the clause verbatim, the named draw with each record's
sha256 and seeds, the limits/sampling/lever table and the six predictions — was
committed then, because the live gate reads that document and the sitting could
not be authorized without it, while its
`audits/deduction-candidate/calibration-3-<date>/` aggregates were a product of
a sitting that had not happened. Item 16 was the sitting itself.

Both were closed by the RUNNER session on
`work/fresh-deduction-calibration-3-run`, which is this card's second pull
request: the sitting ran once on 2026-09-18 and its aggregates are committed at
`audits/deduction-candidate/calibration-3-2026-09-18/`. `tasks/README.md`'s
derived inventory sentence is updated for the status flip.

### The design this follows

`docs/architecture.md` **Layering** and **Enforced boundaries**: nothing here
moves the firewall, `agents/` still does not import `engine/`, and
`experiments/` stays outside the root packages (`.importlinter:5-7`), so
"`meetings/` must not import `experiments/`" remains a design rule this card
restates rather than a linter gate. The four contracts at `.importlinter:20-52`
are untouched. **Determinism and the substrate ladder**: the relevance lever
keeps its declared default of `None`, which preserves recorded behaviour, and
this card turns nothing on by default — the 2026-09-18 mode passes it
explicitly and is refused if either arm resolves it off. AGENTS.md load-bearing
rule 5 (no module-level mutable state; invalid input raises) is why
`CALIBRATION_CAVEATS` is a `MappingProxyType` checked at import against
`CALIBRATION_MODES`, and why `assert_calibration_reports_no_outcome` raises
rather than dropping a field.

### Decisions

1. **The sizing profile is a FIELD of `CalibrationMode`, not a module constant.**
   `assert_ready_for_a_calibration` and `assert_calibration_is_authorized`
   passed one pair — `CALIBRATION_SIZING_UNIT_*` — for both modes. The
   2026-09-18 mode is sized on 38,440 / 4,176 instead, so the pair moved onto
   the mode and each gate now hands the gate the matched mode's own. Consequence
   stated rather than absorbed: `assert_ready_for_a_calibration` now resolves
   the mode BEFORE the feasibility arithmetic. `calibration_mode_for` reads no
   file and needs no credential, so the ordering rule the module documents —
   arithmetic and authorization before the inputs, the inputs before a client —
   is unchanged.
2. **38,440 / 4,176 are FROZEN LITERALS.** They equal `CALIBRATED_UNIT_*` today.
   `tasks/work/fresh-deduction-limits-6.md` refreshes those two constants FROM
   this sitting, and a mode reading them would then be checked against the
   measurement it produced. The test anchors them to
   `calibration-2-2026-09-15/calibration.json`'s own
   `proposal.measured_max_unit_*_tokens` — a committed record that does not move
   — rather than to a live constant or a typed number.
3. **Three new mode fields instead of reusing `truncation_is_a_measurement` as a
   proxy.** That flag decided the report SHAPE (`by_role`, the leak rule) as
   well as the stop discipline. `reports_the_role_split`,
   `reports_authored_diagnostics` and `requires_the_revised_wave` state each
   decision, and the three spent/unspent modes now differ explicitly rather than
   by coincidence.
4. **`authored_diagnostics` is `None`, not an empty block, on the two spent
   modes.** An empty `AuthoredBallotDiagnostics` is not empty in the payload: it
   carries `AUTHORED_DIAGNOSTICS_NOTE`, a paragraph about authored ejections and
   the primary outcome. Publishing it beside the 2026-09-14 output's zeros would
   have the first calibration explaining a block it never measured — and it
   turned `TestCalibrationRun::test_the_report_grades_nothing` red, which is how
   this was found. Absent means absent.
5. **A third caveat beside the first, which stays byte-identical.** This mode
   reports more than a spend measurement, so the string that says "no meeting
   outcome is reported" would contradict its own payload. `CALIBRATION_CAVEAT`
   is unchanged and is checked against what the 2026-09-15 sitting actually
   published.
6. **`assert_calibration_reports_no_outcome` scans KEYS, not values.** Both
   caveats and the diagnostics note SAY "no primary outcome" in those words; a
   value scan would refuse the sentence that makes the promise. It runs on every
   mode, not on the third alone, because a guard applied on one path only has
   already started to drift.
7. **The wave gate checks what it can and states what it cannot.** It refuses a
   mode-3 sitting whose arms do not resolve `AILIBI_CITATION_RELEVANCE=1` and
   `AILIBI_PROMPT_SET=qwen3_6_27b`. It cannot say which accounts REVISION those
   templates are at; that half is pinned by the accounts card's own version test
   and by the prompt-version markers a run records, and the manifest says so.

### Verification

Run in this worktree at the head of this branch, each with its real exit code.

| Command | Result |
| --- | --- |
| `uv run pytest tests/experiments -q` | 603 passed |
| `uv run python scripts/validate_task_docs.py` | passed: 390 historical phase tasks and 390 prompts; 66 work cards |
| `uv run python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `uv run python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7 (the class-(c) evidence branch, expected on a fresh checkout), INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/verify_samples.sh` | 50 + 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/samples/4p1i` | consistent with its replays |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/samples/9p2i` | consistent with its replays |
| `bash scripts/check.sh` | exit 0, run whole and captured directly: ruff, ruff format, lint-imports, `validate_task_docs.py`, `generate_prompts.py --check`, strict mypy over 484 sources, 7,980 passed / 20 skipped / 3 xfailed, and the four frontend legs at 515 tests |

Neither the live calibration nor the live evaluation was run: no provider call
was made by this card, and every case above uses the fake provider, the replay
double or a synthetic input.

### Planted and perturbed failures

Each was demonstrated by editing the shipped code, running the case, and
restoring it.

| Guard | Plant | Observed |
| --- | --- | --- |
| `ballot_rewrites_that_fired` anchored to the marker stack | the pre-repair substring search restored | `test_a_model_echoing_a_marker_phrase_is_not_a_guard_that_fired` → `AssertionError: assert ('off_target_coerced',) == ()` |
| the counterfactual's before-column cross-check | `if archived is not None and (...)`, the pre-repair silent skip | `test_a_replay_with_no_checkpoint_row_is_a_stop` → DID NOT RAISE; the command printed its aggregates from an unchecked before-column |
| the relevance lever's export in `run_case` | the key removed from the env dict | `test_the_scenario_harness_exports_the_relevance_lever` and `test_a_config_without_the_lever_still_resolves_it_off` → `KeyError: 'AILIBI_CITATION_RELEVANCE'` |
| `assert_the_revised_wave_is_enabled` | the gate's body short-circuited to `return` | 4 failures in `TestTheRevisedWaveIsRequiredByTheThirdMode`, including the run path |
| the mode's own sizing pair | mode 3 pointed at `CALIBRATION_SIZING_UNIT_*` | `test_a_run_input_ceiling_below_the_floor_is_refused_here` → DID NOT RAISE (4,600,000 clears 120 x 24,282) |
| `assert_calibration_reports_no_outcome` | `present` forced empty | all three `test_a_payload_carrying_an_outcome_is_refused` cases → DID NOT RAISE |
| `reports_authored_diagnostics` | set `False` on mode 3 | `test_the_diagnostics_block_is_reported_per_arm` and `test_each_arms_resolved_levers_are_published` → `KeyError` / `assert block is not None` |

Plants that live in the suite rather than in an edit: every crossing of the
three modes (`test_every_crossing_of_the_three_modes_is_refused` enumerates all
27 orderings and accepts exactly the three authorized ones), the held-out record
named in the draw, a record named twice, a `status` that is not `development`, a
moved prefix digest, a draw of fifty-nine, a manifest without the third clause,
and a live evaluation invocation that still raises `PerCallCapExceeded` on a
capped completion.

### What the mode does and does not do

`--calibrate --calibration-mode 2026-09-18` renders the sixty seeds of the
shipped prefix draw on both arms at `AUTHORIZED_SAMPLING`, counts a per-call
truncation as a measurement, and reports per arm: the `by_call_type` and
`by_role` token profile, truncations with their `finish_reason`, the leak column
under `ROLE_LEAK_RULE`, the resolved lever profile, and the authored-ballot
diagnostics block — precision beside its harm counter, the illegal-target
column, the coalition funnel with `cleared` and `converted` apart, gate survival
by voter role, guard rewrites by reason including `off_target_coerced`, and
ejections by role-correctness. It computes no paired statistic, evaluates no
decision rule and reports no primary outcome; `PRIMARY_OUTCOME`, `DECISION_RULE`,
`MINIMUM_ACTIONABLE_EFFECT_UNITS`, `WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE`
are byte-identical and the frozen-analysis test passes.

### Record impact, as made

The instrument is in `ARM_SURFACE_SOURCES`, so the arm-surface digest MOVES: a
fresh stamp before the sixth run, not a re-record, and no committed constant
pins it. `experiments/fresh_deduction_instrument.py` is NOT in
`GENERATOR_SOURCES` (`experiments/held_out_prefixes.py:155-178`), so no freeze
restamp is owed by this card. The held-out record at `MANIFEST_PATH` is
untouched and is refused by name inside the draw, before and after the sixth
freeze — which a test proves by appending a sixth band to `CONVERTED_BANDS` and
showing the draw does not move. No recording, report, DTO, metric or weight byte
moves; no experiment becomes ON by default; the committed usage profile and the
two calibrated constants do not move here.

`audits/` bytes moved (the manifest's new section), so the `docs/artifacts.md`
inventory row was recomputed with the change staged: **25,997,781 → 26,011,418
tracked bytes, 324 files unchanged**.

### Deviations

Three files outside the card's Expected scope were touched, all of them the
carry-over repairs the dispatch names, each small and each with a planted case:

* `experiments/citation_relevance_counterfactual.py` — the before-column
  cross-check now fails loudly on a replay the checkpoint has no row for;
* `experiments/deduction_scenarios.py` and
  `experiments/investigation_evaluation.py` — both export
  `AILIBI_CITATION_RELEVANCE` from the config, so every field of
  `meetings.evidence_profile.EXPERIMENT_ENV_NAMES` reaches the renderer. It
  resolves to `0` for every arm either harness builds today, which is what an
  absent key already resolved to, so no capture's behaviour moves;
* `tests/experiments/test_citation_relevance_consumers.py` — a new file for
  those two repairs, rather than mixing an unrelated module's cases into the
  instrument's 11k-line test file. The marker-anchor repair's cases live with
  the function they test, in `TestTheAuthoredLayerIsRecoverable`.

One rename inside the Expected scope: `TestTheTwoAuthorizedCalibrationModes` is
now `TestTheTwoSpentCalibrationModes`, because its docstring said "two sets" and
there are three.

### Limitations

* **The predictions are directions, not thresholds.** They are read against the
  fifth run's figures, which were measured on the 8000-8999 prefixes and not on
  this draw's. A miss is neither a stop nor a verdict, and no decision rule
  reads any of them. The manifest says so beside the table.
* **Cross-sitting comparison is on inputs, not on arms.** The draw is
  calibration 2's to the seed, so the token profile compares; the reference arm
  was RE-BASELINED by the citation guard, so no cell of the fifth run may be
  carried across.
* **The wave gate cannot read the accounts revision.** It checks the lever and
  the prompt set; v5 itself is pinned elsewhere.
* **`ballot_rewrites_that_fired` is anchored, not proof against every echo.** It
  reads the contiguous marker block at position zero and stops at the first
  chunk that is not a marker this codebase writes. A model echo INSIDE that
  block is impossible because the block is built by prepending; a marker head
  with no `"] "` terminator is treated as a truncated record and ends the walk
  rather than being guessed at.
* **The sizing pair is frozen and will look stale.** After
  `fresh-deduction-limits-6.md` refreshes the committed profile, 38,440 / 4,176
  will no longer equal `CALIBRATED_UNIT_*`. That is the intent, and the
  perturbed case
  (`test_a_refreshed_committed_profile_does_not_move_this_modes_gate`) is what
  keeps it from being read as drift.
* **No live measurement exists yet.** Every figure in this section is arithmetic
  over constants or a $0 rehearsal. The sitting's own numbers, the six
  predictions read as met or missed, the proposal and the archive path are the
  runner's Results subsection on the second pull request.

### Review corrections, round 1 (2026-09-18)

Two findings from the independent verifiers, both valid, both repaired here on
`work/fresh-deduction-calibration-3` before merge. Neither moves the draw, the
limits, the sampling, the clause, a prompt byte or a frozen analysis string, and
no provider call was made for either. Every command below was run at this
subsection's commit.

**Finding 1 — `## Results` miscounted its own boxes.** The opening paragraph read
"Acceptance items 1-7 are met and checked. Item 8 is split … Item 9 is the live
sitting", against a list of ten items of which EIGHT were checked: it called the
committed aggregates item 8 and the live sitting item 9, while the card's own
item 8 is the `CEILING_PROPOSAL_RULE` one and is `[x]`. A reader reconciling the
prose against the boxes was told the outstanding work began one item earlier than
it does. Card text only; no code, no gate and no number moves. The paragraph is
now renumbered against the list AS IT NOW STANDS — twelve items, the two review
corrections prepended and checked, the original ten after them, items 1-10
checked, item 11 the split one and item 12 the live sitting — rather than against
the pre-correction list, so it stays true after the reopen rather than becoming
wrong by two. (That was the list at round 1, and this sentence is left as it was
written. Round 2 prepends four more corrections, so the opening paragraph is
renumbered again — sixteen items, 5-14 the implementer's, 15 the split one and 16
the live sitting.)

**Finding 2 — the mode-3 artifact published the live evaluation's note.**
`authored_ballot_block` hard-coded `AUTHORED_DIAGNOSTICS_NOTE`, so
`--calibrate --calibration-mode 2026-09-18` wrote, into every arm of
`calibration.json`, a paragraph saying the counts "are reported beside the
primary outcome" and that "a cross-arm reading of these counts is confounded
until the v5 prompt set equalises the register". Both are false of this payload:
`CALIBRATION_3_CAVEAT`, three lines away in the same file, says no primary
outcome is reported, and `resolved_levers` on the candidate arm shows
`AILIBI_PUBLIC_ACCOUNTS=1` — the v5 set, rendering. This is decision 4's own
reasoning (an empty block "is not empty in the payload: it carries
`AUTHORED_DIAGNOSTICS_NOTE`, a paragraph about … the primary outcome") applied to
the two spent modes and not to the third.

The repair, on the shape the caveats already use rather than an `if`:

* `CALIBRATION_3_AUTHORED_DIAGNOSTICS_NOTE` is a second string beside the live
  one, which stays byte-identical because it is what the live run's block is
  published under. It drops the two false clauses, keeps the half that makes the
  block safe to read — authoring-conditioned, flatters whichever arm authors
  more, the precision ONLY beside its harm counter, the illegal-target column,
  never preregistered, NEVER a decision input — and states what this payload is:
  no primary outcome reported, no paired statistic computed, no decision rule
  evaluated, predictions rather than gates. Where the live note asserts the
  register confound, this one says the register is one of the things the counts
  are read FOR (prediction P3), because whether v5 equalised it is this
  sitting's question and not its premise.
* `note` is a keyword parameter of `authored_ballot_block`, defaulting to the
  live evaluation's, so `_summarize_arm` (the run path) is byte-unchanged in
  behaviour.
* `CALIBRATION_DIAGNOSTICS_NOTES` is a closed `MappingProxyType` naming one note
  per mode that REPORTS the block, and `_summarize_calibration_arm` now takes
  `diagnostics_note: str | None` in place of `with_diagnostics: bool`: the block
  is requested BY its note, so "report the block" and "supply its note" cannot
  disagree.
* `assert_every_reporting_mode_has_its_note` runs at import and refuses a table
  that does not name exactly the modes with `reports_authored_diagnostics`, or
  that points a calibration at `AUTHORED_DIAGNOSTICS_NOTE`. A function rather
  than a bare `if`, so the invariant can be planted from the suite.

| Guard | Plant | Observed |
| --- | --- | --- |
| the mode's own note reaches the artifact | the pre-repair `authored_ballot_block(_authored_counts_over(own))` restored | `test_the_published_block_is_not_the_live_runs_note` and `test_the_diagnostics_block_is_reported_per_arm` → `AssertionError`, the left set carrying "confounded until the v5 prompt set equalises the register" |
| `assert_every_reporting_mode_has_its_note` | in-suite, three ways: an empty table, a note for a mode that reports no block, an extra mode | `test_a_note_table_that_does_not_match_the_modes_is_refused` → `InstrumentError: … needs its OWN note here` |
| the same guard, on the note itself | in-suite: the table pointed at `AUTHORED_DIAGNOSTICS_NOTE` | `test_a_calibration_may_not_publish_the_live_runs_note` → `InstrumentError: a calibration may not publish the live evaluation's note` |

`test_the_published_block_is_not_the_live_runs_note` reads the PAYLOAD rather
than the constructed model — the bytes a reader of the artifact holds — and
asserts the live note appears nowhere in the file.
`test_the_prose_that_promises_no_outcome_is_not_itself_refused` now scans the new
note too, so decision 6's key-only guard keeps being proved against every string
that promises no outcome. The live evaluation's own path is unmoved:
`test_the_block_reaches_the_report_beside_the_outcome` still asserts a dry run's
arms carry `AUTHORED_DIAGNOSTICS_NOTE`.

**Record impact of this round.** The manifest's calibration-3 section gains the
paragraph that states the note split beside the caveat split, so `audits/` bytes
moved again and the `docs/artifacts.md` row was recomputed with the change
staged: **26,011,418 → 26,012,257 tracked bytes, 324 files unchanged**. The
arm-surface digest moves again for the same reason the first commit moved it: the
instrument is in `ARM_SURFACE_SOURCES`, and this is a fresh stamp rather than a
re-record. `experiments/fresh_deduction_instrument.py` is still not in
`GENERATOR_SOURCES`, so no freeze restamp is owed. No recording, report, DTO,
metric or weight byte moves; no lever changes default; the held-out record at
`MANIFEST_PATH` is untouched; `CALIBRATION_CAVEAT`, `AUTHORED_DIAGNOSTICS_NOTE`,
`PRIMARY_OUTCOME`, `DECISION_RULE`, `MINIMUM_ACTIONABLE_EFFECT_UNITS`,
`WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` are byte-identical. No file outside
the Expected scope was touched in this round.

| Command | Result |
| --- | --- |
| `uv run pytest tests/experiments -q` | 610 passed (603 before, plus this round's seven cases) |
| `uv run python scripts/validate_task_docs.py` | passed: 390 historical phase tasks and 390 prompts; 66 work cards |
| `uv run python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `uv run python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7 (the class-(c) branch, expected on a fresh checkout), INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/verify_samples.sh` | 50 + 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/samples/4p1i` and `…/9p2i` | both consistent with their replays |
| `bash scripts/check.sh` | exit 0, run whole and captured directly: 7,987 passed / 20 skipped / 3 xfailed, strict mypy over 484 sources, four frontend legs at 515 tests |
| `uv run python -m experiments.fresh_deduction_instrument --calibrate --calibration-mode 2026-09-18 --json <tmp>/calibration.json` | exit 0, 120 units, 720 calls, `$0.00`, `dry_run: true`; the artifact's own bytes carry neither "reported beside the primary outcome" nor "until the v5 prompt set", and both arms' blocks carry this mode's note (the uncommitted rehearsal the finding was raised on, re-run after the repair) |

### The live sitting (2026-09-18)

The runner session's record, on `work/fresh-deduction-calibration-3-run` at
`ef8081c3`. It ran the sitting ONCE — `2026-09-18T17:17:08Z` to
`2026-09-18T20:16:13Z`, exit 0, 120 units, 721 attempts, not resumed and not
restarted — and wrote no instrument, prompt, manifest or constant byte. The whole
record is
[`audits/deduction-candidate/calibration-3-2026-09-18/CALIBRATION.md`](../../audits/deduction-candidate/calibration-3-2026-09-18/CALIBRATION.md);
every figure below is read from `calibration.json` beside it, EXCEPT the four
replay-derived rows — the recorded EJECT/SKIP column, the surviving and nulled
`primary_reason_id` counts, the contradiction flags and the claim vocabulary —
which were computed by the derivation that file quotes off replays the manifest
keeps outside version control and which therefore do NOT recompute on a clean
checkout. `### Review corrections (2026-09-19)` is that disposition.

**Pre-flight, before any spend.** `.venv/bin/pytest tests/experiments -q` 610
passed; both input records bound by `shasum -a 256` to the digests the manifest
names and by `git diff --exit-code origin/main` to `origin/main`'s bytes (both
exit 0); one fake-provider calibration-3 at $0 which wrote 120 units, 720 calls,
the role split, the leak column, the per-record inputs block and both arms'
diagnostics blocks carrying this mode's own note; and an offline confirmation
that `assert_calibration_is_authorized` accepts the committed manifest for the
2026-09-18 mode and that `assert_limits_are_feasible` accepts
`CALIBRATION_3_LIMITS` for 120 units — per unit 116,000 / 16,000, run 4,700,000 /
520,000, 18,000 s of model work inside 21,600 s elapsed, `AUTHORIZED_SAMPLING`
(turn 4,096 / vote 1,024), 4 transport attempts at 180 s, `featherless` /
`Qwen/Qwen3.6-27B` / `qwen3_6_27b` at `ACCOUNT_PROMPT_SET_REVISION` v5, and
`AILIBI_CITATION_RELEVANCE=1` resolved on BOTH arms.

**The token profile.**

| Arm | Call | n | in mean | in p95 | in max | out mean | out p95 | out max | cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | turn | 181 | 3,278.1 | 4,091 | 4,344 | 286.4 | 426 | 540 | 4,096 |
| `repaired_clock` | ballot | 180 | 3,668.7 | 4,337 | 4,721 | 100.8 | 123 | 143 | 1,024 |
| `combined_accounts` | turn | 180 | 3,397.5 | 4,736 | 5,477 | 476.2 | 835 | 1,187 | 4,096 |
| `combined_accounts` | ballot | 180 | 4,753.1 | 6,227 | 7,354 | 99.8 | 123 | 130 | 1,024 |

Per unit: reference 20,895.1 in / 1,166.3 out mean, largest 25,247 / 1,602;
candidate 24,451.9 / 1,728.3 mean, largest **34,412 / 2,764**. The candidate's
ballot INPUT is where the cross-sitting difference sits — 4,753.1 against the
2026-09-15 sitting's 4,272.6 on the same seeds, +11.2%, with that call's output
unmoved. That is an OBSERVED difference between two sittings and not an estimate
of the wave's template bytes: a seed holds the scripted prefix constant and not
the meeting the sitting generates, the ballot prompt renders that generated
transcript, and this sitting's candidate turns are longer (turn output mean 476.2
against 443.0), so the figure mixes static template bytes with transcript growth
in a proportion no sitting has separated. The sizing conclusion does not rest on
the split. The role split and its prose lengths are in the archive.

**Truncations: zero**, on both arms, both call types and both roles, by both
signals. `finish_reason` is `{"stop": 361}` on the reference and `{"stop": 360}`
on the candidate, and the cap-signal disagreement count is **0 per arm**.

**Leak and self-tell.** Leaking turns 0 on each arm and 0 units carrying one, on
the repaired `_NOT_AN_ASSERTION` guard; the count is an estimate carrying error
in BOTH directions and is not a floor. Self-telling impostor ballots 28 of 60
candidate (46.7%) and 3 of 60 reference (5.0%).

**Refusals, defaults and transport.** Reference: 0 charged failed attempts, 0
defaults, 0 retries, 0 unaccounted. Candidate: **1** billed-and-refused attempt
(2,885 in / 459 out) and **1** defaulted turn by schema validation — the same
call, in 1 unit of 60 — with 0 defaulted votes, 0 retried calls, 0 unaccounted
and 0 aborted attempts. The reference arm made one extra call (361 for 360 slots)
on the meeting layer's shipped single re-ask, which is neither a retry nor a
default.

**The DIAGNOSTICS block**, per arm, precision never without its harm counter:

| Figure | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| authored EJECT / SKIP of 180 ballots | 23 / 157 | **39 / 141** |
| crew authored EJECTs naming the impostor | 6 of 15 (40.0%, p 0.849) | 13 of 27 (48.1%, p 0.649) |
| HARM: crew-on-crew authored EJECTs / units carrying one | 9 / 9 of 60 | 14 / 14 of 60 |
| gate survival, CREWMATE (authored / cleared / coerced / illegal) | 15 / 15 / 0 / 0 = 100.0% | 27 / 26 / 1 / 0 = 96.3% |
| gate survival, IMPOSTOR | 8 / 7 / 1 / 0 = 87.5% | 12 / 10 / 2 / 0 = 83.3% |
| correct coalitions authored / cleared / converted | 0 / 0 / 0 | 1 / 1 / 1 |
| wrongful coalitions authored / cleared / converted | 3 / 3 / 3 | 8 / 8 / 8 |
| ejections / role-correct / crew-authored role-correct | 3 / 0 / 0 (p 1.0) | 9 / 1 / 1 (p 0.974) |
| guard rewrites `off_target_coerced` / `uncited_coerced` / `under_gate_redirect` | 1 / 0 / 0 | 3 / 0 / 1 |
| surviving `primary_reason_id` / nulled | 19 of 180 / **0** | **32 of 180** / **0** |
| contradiction flags / units carrying one | 7 / 6 of 60 | **0** / 0 of 60 |
| claims accusation / alibi / corroboration | 174 / 42 / 12 | 175 / 0 / 0 |

**The six predictions, read as directions and not as gates.** The baseline is the
fifth run, measured on the 8000-8999 prefixes at 50 paired seeds rather than on
this draw's 60; no paired statistic was computed and no primary outcome or
decision rule was evaluated.

| # | Fifth run | This sitting (candidate) | Verdict |
| --- | --- | --- | --- |
| P1 the gap narrows | impostor 86.8%, crew 51.9% | impostor 83.3%, crew 96.3% | **held** — inverted rather than narrowed |
| P2 wrongful falls to or below correct | 36.4% vs 18.2% | 100.0% (8 of 8) vs 100.0% (1 of 1) | **did not hold** — wrongful ROSE rather than falling; the order is a tie at the ceiling on n = 1 (re-labelled in round 2) |
| P3 authored EJECTs fall toward 14 | 119 / 31 of 150 (79.3%) | 39 / 141 of 180 (21.7%), reference 12.8% | **held** |
| P4 surviving ids rise, coercions fall | 0 of 150 keep one; 27 nulled; 44 coerced | 32 of 180 keep one; 0 nulled; 0 `uncited_coerced` | **held on both halves** — the coercion half recomputes from the payload, the surviving-id half is replay-derived and does not |
| P5 holds near 63% | 51 of 81 (63.0%, p 0.013) | 13 of 27 (48.1%, p 0.649) | **did not hold** |
| P6 flags rise above 1 | 1 against 14 | 0 against 7 | **did not hold** — every figure in the row is replay-derived and does not recompute from the payload |

**Pace and usage.** 14.89 s per attempt pooled (13.49 s reference, 16.30 s
candidate), 10,737.2 s of model work inside 10,744.1 s elapsed. Against the
calibration-3 limits: run input 2,720,819 / 4,700,000 (57.9%), run output 173,677
/ 520,000 (33.4%), largest unit input 34,412 / 116,000 (29.7%), largest unit
output 2,764 / 16,000 (17.3%), model work 59.7%, elapsed 49.7%. No ceiling fired.
**$0.00 marginal.**

**The ceiling proposal**, by the unchanged `CEILING_PROPOSAL_RULE`, for 100
units: per unit **104,000 / 16,000**, run **3,442,000 / 281,000** — the max floor
binding on both dimensions, the output floor carrying the in-flight headroom term
(100 x 2,764 + 4,096 = 280,496 -> 281,000). `clears_the_feasibility_gate: true`,
which is true BY CONSTRUCTION because the rule computes those figures from the
maxima the check reads; `clears_the_committed_profiles_gate: false`, because this
sitting's units are SMALLER on output than the committed profile's 4,176 and a
proposal sized on the smaller does not clear the larger. The proposal authorizes
nothing.

**The committed usage profile was NOT refreshed and neither calibrated constant
moved**, by this card's own Constraints: that work is
[the limits card](fresh-deduction-limits-6.md)'s. Run into a path outside version
control so the numbers exist for it: 721 call rows, 120 unit rows,
`largest_charged_unit_input_tokens` **34,412**,
`largest_charged_unit_output_tokens` **2,764**. One consequence, stated and not
acted on: a hundred units of that largest unit need 3,441,200 input and 280,496
output, and the standing `AUTHORIZED_LIMITS` run ceilings (3,844,000 / 422,000)
clear both.

**Guards re-run over the archived payload.**
`assert_report_holds_no_prefix_bytes` passed against all sixty rebuilt prefixes,
and `assert_calibration_reports_no_outcome` passed over the same bytes. The
credential scan over all four files of the archive directory, comparing counts
only against the whole key and its first six characters, returns 0 and 0. The
log's stdout body is byte-identical to `calibration.json` (both sha256
`ce5e95610ba390a9bd0c871252baf42188316c036620c76164dc4a8570556984`).

**Record impact of the sitting.** `audits/` bytes moved, so the
`docs/artifacts.md` inventory row was recomputed with the change staged. No
instrument, prompt, recording, report, DTO, metric or weight byte moves; no lever
changes default; no experiment becomes ON; the held-out record at `MANIFEST_PATH`
is untouched and was refused by name inside the draw; `CALIBRATION_CAVEAT`,
`CALIBRATION_3_CAVEAT`, `AUTHORED_DIAGNOSTICS_NOTE`, `PRIMARY_OUTCOME`,
`DECISION_RULE`, `MINIMUM_ACTIONABLE_EFFECT_UNITS`, `WRONGFUL_EJECTION_TRADEOFF`
and `STOP_RULE` are byte-identical. `experiments/fresh_deduction_instrument.py`
did not move, so the arm-surface digest does not move on this pull request.

**Limitations of the sitting**, in full in the archive's own section: it measured
cost, shape and the authored layer and not merit; the six predictions are
directions and not thresholds, read against a different band at a different
sample size; cross-sitting comparison holds on INPUTS, the reference arm having
been re-baselined by the citation guard both arms enable; the diagnostics are
authoring-conditioned and neither arm's crew precision separates from its 0.5
null; the coalition funnel rests on one correct coalition; nine ejections and
three cannot separate from the 1/3 chance rate; zero truncations bounds the rate
rather than proving it; and the leak rule carries two-sided error.

**Deviations.** Three, each recorded in the archive: the credential reached the
process through `uv run --env-file` from a 0600 file outside the repository
(deleted afterwards) rather than through the manifest's bare `.venv/bin/python`
form, with every other argument identical; the committed usage profile was not
refreshed, which is this card's own instruction; and
`audits/deduction-candidate/checkpoint.md` and `README.md` gained a dated line
and an index paragraph, which the dispatch asked for.

| Command | Result |
| --- | --- |
| `.venv/bin/pytest tests/experiments -q` (pre-flight, and again at the head of this branch) | 610 passed |
| `.venv/bin/python -m experiments.fresh_deduction_instrument --calibrate --calibration-mode 2026-09-18 --output-dir <tmp> --json <tmp>/calibration.json` | exit 0, $0, 120 units / 720 calls, `dry_run: true` |
| the live sitting, once | exit 0, 120 units, 721 attempts, `$0.00`, `dry_run: false` |

The gates, run in this worktree at the head of this branch, each with its real
exit code captured directly rather than through a pipe:

| Command | Result |
| --- | --- |
| `.venv/bin/python scripts/validate_task_docs.py` | passed: 390 historical phase tasks and 390 prompts; 66 work cards (the inventory sentence now reads 2 ready, 64 done) |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `.venv/bin/pytest tests/experiments -q` | 610 passed |
| `.venv/bin/python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7 (the class-(c) evidence branch, expected on a fresh checkout), INFO 5 |
| `.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | **exit 0**, run whole: ruff, ruff format, lint-imports, `validate_task_docs.py`, `generate_prompts.py --check`, strict mypy over 484 sources, 7,987 passed / 20 skipped / 3 xfailed, and the four frontend legs at 515 tests |

`docs/artifacts.md`'s `audits/` inventory row was recomputed from
`git ls-files audits/` with this change staged: **26,012,257 → 26,509,796 tracked
bytes, 324 → 328 files**. The credential scan is count-only and returned 0 and 0
on three denominators: the 4 files of the archive directory, the 9 files this
pull request changes, and all 22,280 files of the worktree.

### Review corrections (2026-09-19)

Four findings were raised against the sitting's record on PR #470, all four by
the repository's automated reviewer and all four valid as observations. They are
the four `Review correction:` acceptance items at the top of `## Acceptance`, and
each is dispositioned IN THE RECORD, under
[`CALIBRATION.md`'s own "Review corrections (2026-09-19)"](../../audits/deduction-candidate/calibration-3-2026-09-18/CALIBRATION.md)
section as well as in place where each number sits. The card stays `done`.

**Nothing measured moved.** The sitting was not re-run and **no provider call was
made in this round**: this card authorizes exactly one live spend and that spend
is spent, so every repair is a reading of bytes already committed. No instrument,
prompt, manifest, profile, constant, recording, report, DTO, metric or weight
byte moves; no lever changes default; no experiment becomes ON; the held-out
record at `MANIFEST_PATH` is untouched; `calibration.json`, `unit-usage.jsonl` and
`calibration-run.log` are byte-identical, so the log's stdout body still matches
the payload at sha256 `ce5e9561…6984`; `CALIBRATION_CAVEAT`, `CALIBRATION_3_CAVEAT`,
`AUTHORED_DIAGNOSTICS_NOTE`, `ROLE_LEAK_RULE`, `PRIMARY_OUTCOME`, `DECISION_RULE`,
`MINIMUM_ACTIONABLE_EFFECT_UNITS`, `WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE`
are byte-identical; and the six predictions themselves are untouched in both the
manifest and this card's Evidence table, which
`TestTheSixPredictionsAreFixedBeforeTheSitting` holds to the same six rows. The
arm-surface digest does not move, because the instrument did not.

**Finding 1 — P2 was recorded as held although wrongful conversion ROSE.** Valid,
and repaired by re-labelling rather than by argument. The prediction is that the
wrongful coalition conversion rate FALLS to or below the correct one; it rose
from 36.4% (8 of 22) to 100.0% (8 of 8), and its order against the correct rate
is a tie at the ceiling on a correct denominator of one. "Held by the letter, on
n = 1" reads the relative-order clause as the whole prediction and drops the fall
that the F6 mechanism claim — F6 ATTACKS stage 2 — rests on. P2 now reads **did
not hold** in the archive's prediction table, in the live-sitting table above, in
the archive's Limitations bullet on the funnel, and the "four held, two did not"
headline reads **three held (P1, P3, P4), three did not (P2, P5, P6)** in
`audits/deduction-candidate/README.md` and `audits/deduction-candidate/checkpoint.md`
as well. The owner's reading of the sixth band is made from the six verdicts as
they now stand.

**Finding 2 — P4 and P6 are not reproducible from any committed byte.** Valid,
and dispositioned rather than closed, because closing it here is not available.
AGENTS.md craft rule 5 (`AGENTS.md:68-69`) requires numbers reproducible from
committed evidence. Four figures are not: the recorded EJECT/SKIP column, the
surviving and nulled `primary_reason_id` counts, the contradiction flags and the
claim vocabulary. They are read off the sitting's replays, which
`audits/deduction-candidate/execution-manifest.md`'s "Development calibration 3
(2026-09-18)" section puts outside version control BY NAME — *"its replays go to
the `--output-dir` the runner names, which is not under version control, and a
per-seed reading of the six predictions is available there and nowhere else"* —
and which this card's own aggregates item restates. That is the clause, and it is
a held-out-discipline trade rather than an oversight: a replay row carries
rendered prompts and model-output prose, which this directory's aggregates-only
rule forbids. The record now separates the sub-claims exactly: P4's coercion half
recomputes (`authored_diagnostics.guard_rewrites_by_reason.uncited_coerced` = 0
on both arms) and P3's numerator recomputes
(`authored_diagnostics.by_voter_role[].authored` sums to 23 and 39 over 180
ballots per arm), while P4's "32 of 180 keep one, 0 nulled" and every figure of
P6 do not, the payload carrying no citation, contradiction or claim field. The
closing repair is those four counters in `authored_diagnostics` — an INSTRUMENT
byte, which a run pull request may not move — and it is routed to the sixth
authorization's instrument work. It cannot be closed retroactively: the sitting's
`--output-dir` no longer exists, re-deriving the counts needs a second live spend
this card does not authorize, and committing the replays is refused by the
aggregates-only rule.

**Finding 3 — the archived `role_leak_rule` tells the reader to read the leak
count beside a primary outcome this payload does not report.** Valid. It is
`ROLE_LEAK_RULE`, the live evaluation's string, carrying the same defect this
card already repaired for `AUTHORED_DIAGNOSTICS_NOTE` by giving mode 3 its own
note. The fix is a calibration-specific or outcome-neutral description, which is
an instrument constant and therefore out of this run pull request's scope; it is
routed to the sixth authorization's instrument work beside finding 2, and the
live text stays byte-identical because it is what the live run publishes under.
The archive's leak section now records that the archived text is the live-run
string, that both of the disputed clauses argue the column is NOT a gate — which
is also this mode's position — and that the count is **0 on both arms** with no
outcome in the payload for a reader to read it beside.

**Finding 4 — the 11.2% ballot-input rise was attributed to v5 template bytes.**
Valid. A seed holds the scripted prefix constant and not the meeting the sitting
generates, and a ballot prompt renders that generated transcript, so two sittings
at nonzero temperature do not hold the ballot's input text fixed. The confound is
measurable in the committed payloads: this sitting's candidate turn output mean
is 476.2 against `calibration-2-2026-09-15/calibration.json`'s 443.0 on the same
sixty seeds. Both the archive's measured-profile section and the token-profile
paragraph above now state the figure as an OBSERVED cross-sitting difference that
mixes static template bytes with transcript growth, say that separating them
needs a controlled-transcript measurement no sitting has made, and say that the
sizing conclusion does not rest on the split — the largest charged unit is 34,412
input however the rise is apportioned.

**Record impact of this round.** `audits/` bytes moved (three files: the
archive's `CALIBRATION.md`, `README.md` and `checkpoint.md`), so
`docs/artifacts.md`'s inventory row was recomputed from `git ls-files audits/`
with the change staged: **26,509,796 → 26,522,872 tracked bytes, 328 files
unchanged**. Five files move in this round and no sixth: the archive's
`CALIBRATION.md`, `docs/artifacts.md`'s `audits/` row and this card are Expected
scope; `audits/deduction-candidate/README.md` and
`audits/deduction-candidate/checkpoint.md` are the sitting's already-recorded
deviation 3, corrected here rather than newly touched, because the headline this
round re-labels is the one they carry. This round
adds no committed byte that a credential could reach — every change is prose this
session wrote, plus one number in `docs/artifacts.md` — and a count-only scan of
its whole diff for key-shaped strings (`FEATHERLESS`, `API_KEY`, `sk-…`, `secret`
and any run of 32 or more identifier characters) returns matches that are **all
symbol names** — `assert_calibration_reports_no_outcome`,
`assert_report_holds_no_prefix_bytes`,
`TestTheSixPredictionsAreFixedBeforeTheSitting` and its two case names — and zero
credentials. The sitting's own three-denominator scan stands from the subsection
above: none of the archive's four files moved in this round except
`CALIBRATION.md`, whose added bytes are this section's prose.

| Command | Result |
| --- | --- |
| `uv run python scripts/validate_task_docs.py` | passed: 390 historical phase tasks and 390 prompts; 66 work cards |
| `uv run python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `uv run pytest tests/experiments -q` | 610 passed |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7 (the class-(c) evidence branch, expected on a fresh checkout), INFO 5 — and FAIL 1 on the in-tree family inventory until the `audits/` row above was recomputed, which is the gate that catches an un-recomputed row |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | see below, run whole with its real exit code |
