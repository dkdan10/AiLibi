# Run a third development calibration that measures the revised wave

**Status:** ready

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

- [ ] A THIRD dated clause and constant set beside the 2026-09-14 and
  2026-09-15 sets, neither edited: `CALIBRATION_3_PAIRED_SEEDS = 60`,
  `CALIBRATION_3_LIMITS`, `CALIBRATION_3_SAMPLING` equal to
  `AUTHORIZED_SAMPLING` (`:438`), a `CALIBRATION_3_CLAUSE` the manifest quotes
  verbatim, and a third `CalibrationMode` (`:1519`) in `CALIBRATION_MODES`
  (`:1551`) carrying `truncation_is_a_measurement=True`. `calibration_mode_for`
  (`:1580`) accepts exactly one mode whole. Planted: sixty seeds under the
  2026-09-15 mode's limits, and this mode's limits at the 2026-09-14 sampling.
- [ ] The clause NAMES the draw and the shipped rule verifies it: all fifty
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
- [ ] The feasibility gate bites on this mode's own sizing profile. The profile
  a mode's ceilings were sized against becomes a frozen field of
  `CalibrationMode`, 24,282 / 3,116 on the two spent modes and 38,440 / 4,176 on
  this one, and `assert_ready_for_a_calibration` (`:3613-3614`) passes the
  matched mode's pair. `assert_limits_are_feasible` (`:1306`) then accepts the
  Constraints table for 120 units: per-unit output 16,000 over the 15,360
  schedule (`unit_output_reservation`, `:603`), per-unit input 116,000 over
  38,440, run input 4,700,000 over 4,612,800, run output 520,000 over 120 x
  4,176 + 4,096 = 505,216. Planted: a run-level input ceiling of 4,600,000,
  refused here and passing against 24,282.
- [ ] Both arms run with the wave enabled: the v5 accounts prompts on the
  candidate ([their card](accounts-prompt-set-v5.md)) and
  `citation_relevance_version=1` on BOTH arms
  ([the guard card](relevance-aware-citation-guard.md)). That lever's declared
  default stays `None`, on the pattern of `EXPERIMENT_ENV_NAMES`
  (`meetings/evidence_profile.py:25`) and `MeetingEvidenceProfile` (`:67`),
  mirrored at `orchestrator/experiment_config.py:42-45`, where `None` preserves
  recorded behaviour; this sitting passes it explicitly and the report records
  the resolved profile per arm. Planted: mode 3 with the guard resolved OFF on
  either arm is refused before a client exists.
- [ ] In THIS mode a per-call truncation is a measurement, as in the 2026-09-15
  mode: the cap branch that builds `PerCallCapExceeded` (`:2815`) does not raise
  here, the call takes the meeting layer's shipped fail-soft, and it is counted
  per arm, per call type and per role with its `finish_reason`. `STOP_RULE`
  (`:722`) is not edited and the live path still stops. Planted: a live
  evaluation invocation still raises on that response.
- [ ] The report carries, per arm and as aggregates: calibration 2's
  `by_call_type` and `by_role` profile, the truncation rows, the leak column
  under `ROLE_LEAK_RULE` (`:6216`), and the diagnostics block, which is authored
  precision with its harm counter on the same denominator, the coalition funnel,
  gate survival by role, guard rewrite reasons over `BallotTargetRewriteReason`
  (`meetings/schemas.py:727-733`) including the guard card's
  `off_target_coerced`, and ejections by role-correctness. Counts only: no
  prose, prompt, prefix or per-seed outcome, with
  `assert_report_holds_no_prefix_bytes` (`:4808`) over the payload.
- [ ] This mode carries its OWN caveat beside `CALIBRATION_CAVEAT` (`:6093`),
  which stays byte-identical, being what the two spent sittings were published
  under. The new string says what is and is not reported: aggregate ballot and
  ejection diagnostics off development units, no primary outcome, no paired
  statistic, no decision rule. Planted: a mode-3 report carrying a `paired`
  block or a `supported_correct_ejection` field is refused.
- [ ] `CEILING_PROPOSAL_RULE` (`:6061`) and `ceiling_proposal` (`:6934`) are
  unchanged and the proposal is published for the hundred-unit run as
  calibration 2's was, while the refresh it feeds stays out of scope.
- [ ] Aggregates committed under
  `audits/deduction-candidate/calibration-3-<date>/` in the shape calibration 2
  committed, with per-unit usage rows; replays go to the runner's
  `--output-dir`, outside version control, which is where a per-seed reading of
  the predictions is available. The manifest gains a dated "Development
  calibration 3" section: the clause verbatim, the named draw with each record's
  sha256 and seeds, the limits and sampling table, the lever settings, and the
  six predictions copied verbatim as predictions rather than gates, with the
  sentence that a miss is neither a stop nor a verdict. A test holds the card's
  table and the manifest's copy to the same six rows; the frozen analysis
  strings stay byte-identical and no earlier dated section is edited.
- [ ] The live sitting runs once, by a separate runner session on
  `work/fresh-deduction-calibration-3-run` under the manifest's calibration-3
  clause. Its Results subsection records the profile, the truncation rows, the
  leak counts, the diagnostics block, each prediction as met or missed, the
  proposal, usage at $0.00 and the archive path.

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
