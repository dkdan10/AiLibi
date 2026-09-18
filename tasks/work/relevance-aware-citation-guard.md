# Make the ballot citation guard test relevance behind a default-OFF lever

**Status:** ready

## Outcome

The ballot citation gate stops accepting a citation that is merely real and
starts asking whether it is about the player the ballot names. The aboutness
rule becomes one definition in the meeting layer, the instrument's grader
imports it instead of keeping its own copy, and a test makes it impossible for
guard and grader to disagree about a ballot. It sits behind a new versioned
experiment lever, `citation_relevance_version`, defaulting to `None`, so every
default-path game, recording, sample and report is byte-identical, and BOTH arms
of the deduction instrument turn it on for the next evaluation. An off-target
EJECT takes the disposition an uncited EJECT takes today, coerced to SKIP unless
its target is contradiction-flagged, under its own rewrite reason
`off_target_coerced`. Nothing is recorded and nothing the run is judged by
moves.

## Evidence

[The diagnosis of 2026-09-18](../diagnosis-2026-09-18-fifth-run.md) is the
basis; the owner approved its ten decisions as a set on 2026-09-18 and the
memo's section 11 records the rulings. Decision 5 is this card. Its section 7 F6
row adds that this is the only change costing the impostor its free pass, that
it edits shared substrate and that it re-baselines both arms.

`guard_ballot_citation` (`meetings/manager.py:3710`) coerces an EJECT to SKIP
only when BOTH citation fields are null and the target carries no contradiction
flag (`:3778-3799`). Its docstring states the gap as a scope choice: the gate
enforces citation "VALIDITY, never relevance" (`:3764`), because no upstream
validator links a citation to the ballot's target. The rule that does ask is
`grade_citation_relevance` (`experiments/fresh_deduction_instrument.py:4387`),
the primary outcome's third conjunct (`:4485-4500`), built from `_names_player`
(`:4342`, whole-token via `_PLAYER_TOKEN` at `:4339`), `_turn_bears_on`
(`:4348`) and `_cited_line_names` (`:4366`).

The gap is one-sided by role. Re-tallied from
`audits/deduction-candidate/run-2026-09-16/` with the committed grader, over
every recorded EJECT ballot graded against its OWN target:

| Candidate arm, recorded EJECTs | Crew | Impostor |
| --- | --- | --- |
| Survived today's gate | 42 | 33 |
| Citation on target | 34 | 19 |
| Citation off target | 6 (14.3%) | 14 (42.4%) |
| Uncited, flag-exempt | 2 | 0 |

Those denominators are memo section 3's 51.9% and 86.8% survival rates exactly;
the reference arm records 10 crew and 4 impostor EJECTs, 1 off target.
Restricted to the 24 ballots naming an ejected player the memo's figure
reproduces: 7 off target, 4 of the impostor's 8 and 3 of the crew's 16, against
0 of 2.

Disposition matters because the guard runs post-redirect (`:3756-3767`) and the
redirect keeps the citation. Seed 8006 is that case live: `p-3`'s ballot was
redirected from `p-1` onto `p-4` (`under_gate_redirect`, `:3697-3706`) and kept
an observation citation naming `p-1`. It is 1 of the 20 candidate ballots the
new rule reaches, and it is why `ballot_target_rewrite_provenance` matters: it
returns `{}` when a reason is already set (`meetings/voting.py:139-140`), so a
twice-rewritten ballot keeps `under_gate_redirect` in the typed field while both
markers stack on the rationale, and a count of this class reads the marker
stack.

Architecture. `meetings/` may not import `experiments/`: the firewall interior
is `{agents, llm, meetings, observation}` (`tests/test_firewall.py:389`),
`experiments` is ungraphed (`:381`), and `_closure_breakers` sweeps every
interior package for an exterior import (`:522-532`, asserted at `:569-575`).
The legal direction is the other one, the instrument already importing
`meetings.manager` and `meetings.schemas` (`:117-131`). At the guard's call site
the manager holds `transcript.turns` (used at `meetings/manager.py:2317`) and
the rendered ballot prompt, bound at `:2163`; grading both arms' 79
cited-observation EJECT ballots against that prompt alone changes no verdict, 79
of 79. Two pins move rather than break:
`tests/meetings/test_citation_gate.py:474-478` pins the guard's parameter set as
exactly `{"ballot", "contradictions"}`, and `:270-301` pins the
redirect-keeps-citation ballot passing, the fixture the lever flips.

## Acceptance

- [ ] The aboutness rule has ONE definition, in the meeting layer. A new
  `meetings/citation_relevance.py` holds the whole-token player match, the turn
  rule (a turn is about a player when its speaker is that player or the player
  is named in its dumped content) and the cited-line rule, taking already-split
  LINES so each caller supplies its own surface.
  `experiments/fresh_deduction_instrument.py` deletes `_names_player`,
  `_turn_bears_on` and `_cited_line_names` and imports the meeting-layer rule;
  `grade_citation_relevance` keeps its signature, `subject` argument and
  verdicts. `_every_string_in` (`:4785`) stays put: it also serves the held-out
  leak scan (`:4823`, `:5357`), and a test asserts the two walkers agree on a
  dumped `MeetingTurn`. The move changes no grade: the sizing command re-grades
  all 300 archived ballots and reports 24 candidate naming ballots with 7 off
  target and 2 reference naming ballots with 0. Planted: an edit to the moved
  rule changes those counts.
- [ ] The guard tests relevance under the lever. `guard_ballot_citation` gains
  keyword-only `citation_relevance_version`, the meeting's turns and the voter's
  prompt lines, all defaulted so every existing call site stays valid. ON, an
  EJECT whose citations are present but do not bear on ITS OWN target takes the
  uncited path: exempt when the target is contradiction-flagged, otherwise
  coerced to SKIP, the exemption evaluated once and shared so the two classes
  cannot disagree about a flagged target. The coercion is countable: a new
  marker beside `UNCITED_ZERO_FLAG_EJECT_MARKER` (`meetings/manager.py:400-402`)
  and a new `BallotTargetRewriteReason` member `off_target_coerced`
  (`meetings/schemas.py:727-733`), registered in both marker tables
  (`training/surrogate/dataset.py:189-196`, `api/replay_loader.py:3562-3569`) so
  their equality pin (`tests/training/test_surrogate_dataset.py:1074-1078`)
  stays green on the widened pair rather than a stale six.
- [ ] The lever is declared the way the existing ones are and defaults to
  `None`: a `Literal[1] | None` field named `citation_relevance_version` on
  `RecordedExperimentConfig` (`orchestrator/experiment_config.py:42-46`) inside
  its integer-version validator (`:48-56`), the same field on
  `MeetingEvidenceProfile` (`meetings/evidence_profile.py:72-88`) with its
  switch `AILIBI_CITATION_RELEVANCE` in `EXPERIMENT_ENV_NAMES` (`:25-32`)
  resolved by `from_environment` (`:91-104`), that switch commented at `0` in
  `.env.example:235-250`, and the field added to
  `orchestrator/game.py:2213-2218`'s runner-agreement tuple so a recorded config
  and the served profile cannot differ. The key is omitted from the serialized
  payload whenever it is `None` (`experiment_config.py:95-107`), so every
  committed recording keeps its bytes and `is_default` (`:117-123`) still holds;
  a format bump is refused because the frozen manifest binds format 2 and both
  arms are format-2 configs. `scripts/check_doc_facts.py:1899-1969` gates
  template against registry.
- [ ] BOTH arms set `citation_relevance_version=1` for the next evaluation:
  `instrument_arms()` (`experiments/fresh_deduction_instrument.py:1025-1048`)
  gives both the same version and `InstrumentArm.environment` (`:999-1022`)
  exports the matching switch, so the arms still differ in the accounts channels
  alone. Card and manifest state that this RE-BASELINES the reference arm: the
  fifth run's reference figures are not comparable with the next run's and none
  may be carried across as a reference cell. Planted: a lever on one arm only
  fails the arm-parity assertion.
- [ ] Guard and grader cannot disagree. A test walks a committed fixture's
  ballots and asserts, for each, that the guard's verdict under the lever equals
  the grader's verdict for that ballot graded against its own target, on the
  same turns and lines. It states why they coincide where the primary outcome
  reads them: the grader grades naming ballots against the ejected player, and
  on a naming ballot the ejected player IS the target. Planted: a one-sided edit
  to either caller is red.
- [ ] Lever OFF is byte-identical. A committed fixture replays through both
  settings and the OFF run is asserted equal to today's behaviour ballot by
  ballot, including `tests/meetings/test_citation_gate.py:270-301`'s
  redirect-keeps-citation ballot, which passes OFF and coerces ON; `:474-478`
  widens to the new exact parameter set and keeps its suspicion claim. Planted,
  each red before and green after: an on-target citation passes, an off-target
  one coerces with the new reason and marker, a contradiction-flagged target
  still ejects on an off-target citation, and the lever at `None` leaves the
  fixture byte-identical.
- [ ] `audits/deduction-candidate/execution-manifest.md` gains a dated section
  "Relevance-aware citation guard (2026-09-18)" declaring the change, its basis
  (the diagnosis, linked), that it applies to BOTH arms and so re-baselines the
  reference, that it is CANDIDATE-WEIGHTED in practice (on the fifth run's
  archive it reaches 20 candidate ballots against 1 reference ballot, and costs
  the impostor 4 of its 8 naming ballots against the crew's 3 of 16), and that
  the primary outcome, decision rule, minimum actionable effect,
  `WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` are unchanged
  (`fresh_deduction_instrument.py:659`, `:672`, `:677`, `:693`, `:722`). That
  `audits/` byte change recomputes `docs/artifacts.md`'s audits row (today
  `25,974,591 tracked bytes / 324 files`, `:109`), `tasks/README.md`'s inventory
  sentence (`:43`) is updated, and `scripts/verify_ml_evidence.py` passes.
- [ ] Offline sizing, no provider call. A documented command in the shape
  `audits/deduction-candidate/run-2026-09-16/reconcile.py` established (counts
  only; no prompt, prefix, transcript or ballot text in its output) re-tallies
  that archive under the lever and prints the counterfactual ejection table per
  arm: ballots reached, ejections, role-correct, wrongful and the paired
  `supported_correct_ejection` cells, before and after. Results reports that
  table and states that coercion only removes an EJECT vote, so the re-tally can
  lose an ejection and never invent one.

## Constraints

No live provider call of any kind: fake and replay providers only, no
calibration, no recording, no re-record, no re-scored report. Nothing under
`audits/deduction-candidate/run-2026-09-16/` is edited; it is read, for counts
only. The primary outcome, decision rule, minimum actionable effect,
`WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` do not change on this card or any
card of this wave, and per decision 7 the tradeoff is not restated; this card
changes what a ballot must cite, never what the run is judged by, and moves none
of the owner's authorized limits. F5 and F8 are out of scope of every card of
this wave, so no second citation slot is added and the shared reason-id
normalizer keeps its bytes. The figures the specification fixes are the owner's,
fixed by this card's merge: 4 of the impostor's 8 naming ballots and 3 of the
crew's 16.

`meetings/` must not import `experiments/` and no card of this wave relaxes
that. No held-out band prefix is generated, printed or opened: bands 3000-3999
through 8000-8999 are development data, and
`audits/deduction-candidate/held-out/manifest.json` keeps reading `held_out` for
8000-8999 until [the sixth freeze](held-out-prefix-freeze-6.md) moves it. One
writer per file within the wave: this card owns `meetings/` and its tests, and
shares the instrument and its test module with
[the diagnostics card](fresh-deduction-instrument-diagnostics.md) only by
stacking behind it.

## Expected scope

`meetings/citation_relevance.py` (new), `meetings/manager.py` (the marker, the
guard and its call site at `:2388`), `meetings/schemas.py`,
`meetings/evidence_profile.py`, `orchestrator/experiment_config.py`,
`orchestrator/game.py`, `.env.example`,
`experiments/fresh_deduction_instrument.py` (the three deleted helpers, the
import, the two arm configs), `training/surrogate/dataset.py` and
`api/replay_loader.py` (the marker tables), the tests for each of those, a new
`tests/meetings/test_citation_relevance.py`, the sizing script,
`audits/deduction-candidate/execution-manifest.md`, `docs/artifacts.md`,
`tasks/README.md`'s inventory sentence, this card. No prompt family is in scope.

Delivered on `work/relevance-aware-citation-guard` and one pull request into
`main`, a merge commit or fast-forward and never a squash, with the trailer
`Card: tasks/work/relevance-aware-citation-guard.md`. Wave A is
[the v5 accounts prompt set](accounts-prompt-set-v5.md) in parallel with
[the instrument diagnostics](fresh-deduction-instrument-diagnostics.md); this
card is wave B and bases on the diagnostics branch, because both edit the
instrument and its test module, retargeting `main` once that card merges. Then
[the third calibration](fresh-deduction-calibration-3.md) stacks on all three,
and then, once it reports, the sixth authorization with
[its limits card](fresh-deduction-limits-6.md) and
[the sixth freeze](held-out-prefix-freeze-6.md) dispatched alongside that card.

## Record impact

Moves substrate behaviour behind a lever defaulting to `None`, so no recording,
report, DTO, metric, weight or sample byte moves and no experiment becomes ON;
no adopting record is created. The one `audits/` change is the manifest's new
dated section. `BallotTargetRewriteReason` gains `off_target_coerced`, widening
`TARGET_REWRITE_LABELS` (`training/surrogate/dataset.py:206-208`) and the
display chip set (`api/replay_loader.py:302-304`) by derivation, and no
committed recording carries the new label. The measured consequence is for the
NEXT run only and is stated
rather than discovered: both arms enable the lever, so the reference arm is
re-baselined and the fifth run's reference figures are not comparable with the
sixth's. On that archive the rule reaches 20 candidate ballots and 1 reference
one, which is why the manifest calls it candidate-weighted while the code is
symmetric.

## Validation

`uv run pytest tests/meetings tests/experiments tests/training tests/api
tests/test_firewall.py -q` (fake and replay providers only), `uv run
lint-imports`, `uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`) with
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`,
`bash scripts/verify_samples.sh`, the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check` runs
over the two `replays/samples/` and two `replays/ml_corpus/` sets, the offline
sizing command, and `bash scripts/check.sh` to the end rather than to the first
gate. Do not run the
live evaluation, a calibration or any provider call as a check.
