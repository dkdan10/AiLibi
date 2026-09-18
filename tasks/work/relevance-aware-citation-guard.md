# Make the ballot citation guard test relevance behind a default-OFF lever

**Status:** done

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

- [x] The aboutness rule has ONE definition, in the meeting layer. A new
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
- [x] The guard tests relevance under the lever. `guard_ballot_citation` gains
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
- [x] The lever is declared the way the existing ones are and defaults to
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
- [x] BOTH arms set `citation_relevance_version=1` for the next evaluation:
  `instrument_arms()` (`experiments/fresh_deduction_instrument.py:1025-1048`)
  gives both the same version and `InstrumentArm.environment` (`:999-1022`)
  exports the matching switch, so the arms still differ in the accounts channels
  alone. Card and manifest state that this RE-BASELINES the reference arm: the
  fifth run's reference figures are not comparable with the next run's and none
  may be carried across as a reference cell. Planted: a lever on one arm only
  fails the arm-parity assertion.
- [x] Guard and grader cannot disagree. A test walks a committed fixture's
  ballots and asserts, for each, that the guard's verdict under the lever equals
  the grader's verdict for that ballot graded against its own target, on the
  same turns and lines. It states why they coincide where the primary outcome
  reads them: the grader grades naming ballots against the ejected player, and
  on a naming ballot the ejected player IS the target. Planted: a one-sided edit
  to either caller is red.
- [x] Lever OFF is byte-identical. A committed fixture replays through both
  settings and the OFF run is asserted equal to today's behaviour ballot by
  ballot, including `tests/meetings/test_citation_gate.py:270-301`'s
  redirect-keeps-citation ballot, which passes OFF and coerces ON; `:474-478`
  widens to the new exact parameter set and keeps its suspicion claim. Planted,
  each red before and green after: an on-target citation passes, an off-target
  one coerces with the new reason and marker, a contradiction-flagged target
  still ejects on an off-target citation, and the lever at `None` leaves the
  fixture byte-identical.
- [x] `audits/deduction-candidate/execution-manifest.md` gains a dated section
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
- [x] Offline sizing, no provider call. A documented command in the shape
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

## Results

Delivered on `work/relevance-aware-citation-guard` in six commits
(`6a144038`, `c1242973`, `68dfe979`, `86a67e95`, `d17ca50e`, `13b085a1`) plus
this flip, based on `17d49885` with both wave-A cards already merged, so the PR
targets `main` directly.

### What was built, and against which section

**The aboutness rule is one definition, in the meeting layer.**
`meetings/citation_relevance.py` (new) holds the whole-token player match
(`names_player`), the dumped-structure walker (`every_string_in`), the turn rule
(`turn_bears_on`: a turn is about a player when its speaker is that player or
the player is named anywhere in its dumped content) and the cited-line rule
(`cited_line_names`), which takes already-split LINES so each caller supplies
its own surface. `citations_bear_on` composes them, so neither caller can
compose them differently. `experiments/fresh_deduction_instrument.py` deleted
`_PLAYER_TOKEN`, `_names_player`, `_turn_bears_on` and `_cited_line_names` and
imports the module; `grade_citation_relevance` keeps its signature, its
`subject` argument and its three verdicts. `_every_string_in` stays in the
instrument, because it also serves the held-out leak scan
(`assert_report_holds_no_prefix_bytes`) which is outside the firewall interior;
`tests/meetings/test_citation_relevance.py::TestTheTwoWalkersAgree` asserts the
two walkers agree on a dumped `MeetingTurn`.

The import direction is why the module exists rather than an import: the
firewall interior is `{agents, llm, meetings, observation}` and `experiments`
is ungraphed, so `tests/test_firewall.py`'s `_closure_breakers` sweep forbids
`meetings/` importing `experiments/` outright, while the instrument imports
`meetings` freely. `TestTheImportDirection` states that locally over the new
module's own AST.

**The guard tests relevance under the lever.** `guard_ballot_citation` gains
three keyword-only, defaulted parameters — `citation_relevance_version`,
`turns`, `prompt_lines` — so every existing call site keeps its behaviour. ON,
an EJECT whose citations are present but do not bear on ITS OWN target takes the
uncited path; the zero-flag exemption is read ONCE and shared, so the two
classes cannot disagree about a flagged target. The coercion is countable:
`OFF_TARGET_CITATION_EJECT_MARKER` beside `UNCITED_ZERO_FLAG_EJECT_MARKER`, and
`off_target_coerced` on `BallotTargetRewriteReason`, registered in both marker
tables (`training/surrogate/dataset.py`, `api/replay_loader.py`) so their
equality pin stays green on the widened pair. The citation fields ride into the
record intact on the off-target class — nulling a real id would erase the
evidence the coercion rests on — which is the one respect in which the two
dispositions differ.

The production call site (`meetings/manager.py::_collect_one_ballot`) threads
`self._evidence_profile.citation_relevance_version`, `transcript.turns` and
`prompt.splitlines()` — this meeting's final transcript and the lines of the
ballot prompt THIS voter was served, the only memory surface a private
observation id could have been read off.

**The lever is declared the way the existing ones are.**
`citation_relevance_version: Literal[1] | None = None` on
`RecordedExperimentConfig` inside its integer-version validator; the same field
on `MeetingEvidenceProfile` with `AILIBI_CITATION_RELEVANCE` in
`EXPERIMENT_ENV_NAMES`, resolved by `from_environment`; the switch commented at
`0` in `.env.example`'s independently-versioned-experiments section, which
`scripts/check_doc_facts.py::check_experiment_registry` gates against the
registry (it now verifies a 5-switch registry); and `citation_relevance_version`
added to `orchestrator/game.py`'s runner-agreement tuple so a recorded config
and the served profile cannot differ. The key is omitted from the serialized
payload whenever it is `None`, at EVERY format version, so no committed format-1
or format-2 recording moves a byte, `is_default` still holds, and both
instrument arms stay format 2 — no format bump, which the frozen manifest's
binding of format 2 forbids.

**Both arms enable it, and the reference arm is re-baselined.**
`instrument_arms()` gives both arms `citation_relevance_version=1` and
`InstrumentArm.environment` exports the matching switch, so the arms still
differ in the accounts channels alone. The manifest's dated section and this
card both state that this RE-BASELINES the reference arm: the fifth run's
reference figures are not comparable with the next run's and no reference cell
may be carried across.

### Decisions

1. **The composition, not just the three rules, lives in the shared module.**
   The card names three rules; `citations_bear_on` is a fourth function that
   composes them exactly once. Without it the guard and the grader would each
   write the same three-branch short-circuit and the agreement test would pin a
   coincidence rather than a structure.
2. **The off-target class keeps its citation fields.** The uncited class has
   both fields null by its own predicate; the off-target class has a REAL id,
   and it is the evidence the coercion rests on. Nulling it would also mint a
   second audit marker for a validator that did not fire.
3. **The diagnostics block's rewrite tally now reads the MARKER STACK.** This is
   the trap the card's Evidence names: `ballot_target_rewrite_provenance`
   returns `{}` once a reason is set, so a ballot re-aimed by
   `under_gate_redirect` and then coerced keeps the redirect in
   `guard_rewrite_reason` while both markers stack on the rationale. The fifth
   run's seed 8006 is that ballot, and this card creates the class at scale — so
   a count reading the single field would report zero `off_target_coerced` on a
   run full of them. `ballot_rewrites_that_fired` reads the stack, over a
   marker table asserted complete against `BallotTargetRewriteReason` at import.
   **This is beyond the card's literal Expected-scope enumeration for that file
   and is reported as a deviation below.** It moves a labelled diagnostic only:
   nothing gates on it, no committed recording carries a stacked pair that this
   changes (the fifth run's 44 `uncited_coerced` and 2 `under_gate_redirect` are
   in a directory this card does not re-tally into any published cell).
4. **The counterfactual lives under `experiments/`, not `scripts/`.** It imports
   the instrument's own graders rather than restating them, and `scripts/` is a
   production root that `tests/experiments/test_torch_probe_excluded.py` forbids
   importing `experiments` — the rule that keeps the mypy-excluded torch probe
   out of the shipping tier. It was written to `scripts/` first and moved in
   `d17ca50e` when that gate bit.
5. **`ExperimentConfigView` was NOT widened.** The card's Record impact forbids
   a DTO byte move, and adding the field to the spectator view would add
   `"citation_relevance_version": null` to every served replay's metadata and
   regenerate `frontend/src/types/api.ts`. The consequence is stated in
   Limitations.

### The figures, recomputed

Offline, from the fifth run's archive, no provider call and no band opened:

```sh
.venv/bin/python experiments/citation_relevance_counterfactual.py \
  audits/deduction-candidate/run-2026-09-16
```

| `run-2026-09-16/`, under the lever | reference | candidate |
| --- | --- | --- |
| Recorded ballots re-graded | 150 | 150 |
| Recorded EJECT ballots | 14 | 75 |
| Ballots the rule reaches | 1 | 20 |
| — by voter role, crew / impostor | 1 / 0 | 6 / 14 |
| Naming ballots | 2 | 24 |
| — verdicts | 2 relevant | 15 relevant, 7 off target, 2 uncited |
| — off target, impostor / crew | 0 of 0 / 0 of 2 | 4 of 8 / 3 of 16 |
| Ejections, before → after | 1 → 1 | 12 → 5 |
| Role-correct, before → after | 0 → 0 | 4 → 3 |
| Wrongful, before → after | 1 → 1 | 8 → 2 |
| `supported_correct_ejection`, before → after | 0 → 0 | 2 → 2 |
| Units whose ejection moved | 0 | 7 |
| Ejections invented | 0 | 0 |

Every figure the card's Evidence fixes reproduces exactly: 24 candidate naming
ballots with 7 off target (4 of the impostor's 8, 3 of the crew's 16) against 2
reference naming ballots with 0, and a reach of 20 candidate ballots against 1
reference one. **Coercion only ever removes an EJECT vote and adds a SKIP one,
so the re-tally can lose an ejection and never invent one** — the command
asserts that per unit (`invented_ejections`) and raises rather than printing if
an after-ejection was not a before-ejection; it reports zero here. The
before-column is checked against the archive's own `checkpoint-final.json`
before the after-column is believed, on all 100 units.

The rule costs the candidate 7 of its 12 ejections and 6 of its 8 wrongful ones
while costing it one role-correct ejection, and it costs `supported_correct_ejection`
nothing — the two scoring units survive it. That is a counterfactual over
recorded ballots, not a prediction: nothing downstream of a coerced vote is
modelled.

### Verification

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 (ruff, format, lint-imports, validate_task_docs, generate_prompts --check, mypy over 483 files, 7,9xx pytest, frontend lint/tsc/vitest/build) |
| `.venv/bin/python -m pytest tests/meetings tests/experiments tests/training tests/api tests/test_firewall.py tests/orchestrator -q` | 3439 passed, 2 skipped, 3 xfailed, exit 0 |
| `.venv/bin/lint-imports` | 4 kept, 0 broken |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 66 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | passed; "the 26-lever substrate registry and the 5-switch experiment registry" |
| `.venv/bin/python scripts/verify_ml_evidence.py` | 60 checks, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | passed |
| `bash scripts/verify_samples.sh` | exit 0; 50/50 on each of the two sets |
| `build_sample_report.py --sample-dir <set> --check`, four sets | exit 0 each; "consistent with its replays" |
| `experiments/citation_relevance_counterfactual.py audits/deduction-candidate/run-2026-09-16` | exit 0, table above |

No provider call of any kind was made: the fake provider, the committed replay
double and committed archive bytes only. Nothing under `run-2026-09-16/` was
written. `scripts/verify_ml_evidence.py --complete` was not run. No band was
generated, printed or opened beyond the committed regeneration test the restamp
rule requires.

### Planted and perturbed failures

Each was applied, run, and restored.

1. **The moved rule decides the counts** (acceptance 1). `cited_line_names`
   perturbed to search the whole prompt rather than the line:

   ```
   naming 24 {'relevant': 22, 'uncited': 2} reached 0 after {'ejections': 12, ...}
   ```

   against the true `{'off_target': 7, 'relevant': 15, 'uncited': 2}`, reach 20,
   after-ejections 5. The rule stops biting entirely; the sizing figures move.
2. **A lever on one arm only fails arm parity** (acceptance 4).
   `citation_relevance_version=1` removed from `repaired_clock`:
   `test_the_arms_differ_only_in_the_account_channels` — `Extra items in the
   left set: 'citation_relevance_version'`.
3. **A one-sided GUARD is red** (acceptance 5). The guard's lever test inverted
   to `is None`: `TestGuardAndGraderCannotDisagree` — `assert 'p-2' == 'SKIP'`.
4. **A one-sided GRADER is red** (acceptance 5). `grade_citation_relevance`
   passed `cited_turn_id=None`: same test — `assert guarded is ballot` fails on
   a committed seed-23 ballot the guard coerced and the grader called relevant.
5. **The exemption must be shared** (acceptance 2/6). `if ballot.target in
   flagged and uncited:` — `test_a_flagged_target_still_ejects_on_an_off_target_citation`
   red: the flagged target is coerced under `off_target_coerced`.
6. **Lever OFF must be byte-identical** (acceptance 6). The lever test inverted
   so OFF bites: both `test_the_lever_off_leaves_every_committed_ballot_untouched`
   (`assert lever_off == today`) and the pre-existing
   `test_redirect_keeps_citation_and_passes_the_gate` go red.
7. **The rewrite count must read the marker stack** (decision 3). The old
   `if ballot.guard_rewrite_reason is not None` restored:
   `test_a_doubly_rewritten_ballot_is_counted_under_both_reasons` — `assert 0 ==
   1` on `off_target_coerced`, on a ballot built by the REAL guards.
8. **The new key must be omitted when OFF** (acceptance 3). The conditional
   `del` removed: `test_the_citation_relevance_key_is_absent_until_the_lever_is_on`
   red at format 1 and 2. Note that `verify_samples.sh` stays GREEN under this
   plant — the committed sets are written with the default config, which
   normalizes away entirely — which is why the assertion is made on the
   serializer rather than left to the sample gate.

Two pins moved rather than broke, deliberately:
`tests/meetings/test_citation_gate.py`'s guard-signature equality widened to the
exact new parameter set, keeping its suspicion claim (none of the three new
names is a suspicion value, which is why it stays an equality); and
`tests/api/test_replay_loader.py`'s rewrite-label pin from five typed reasons to
six, which the display class reached by derivation with no edit to the loader's
own set.

### Record impact, as delivered

No recording, report, DTO, metric, weight or sample byte moved: `verify_samples`
and the four `--check` runs pass untouched. `BallotTargetRewriteReason` gained
`off_target_coerced`, widening `TARGET_REWRITE_LABELS` and the display chip set
by derivation; no committed recording carries the label. Two `audits/` files
moved — the execution manifest's new dated section, and the held-out manifest's
restamp — and `docs/artifacts.md`'s audits row was recomputed twice as they
landed, from 25,989,538 to 25,996,198 tracked bytes over the same 324 files.
`tasks/README.md`'s derived inventory sentence follows this card's flip.

**The held-out restamp.** `orchestrator/game.py` is a `GENERATOR_SOURCES` file,
so this card's edit to its runner-agreement tuple turned
`test_the_committed_manifest_regenerates_from_its_own_band` red. The documented
rule (`tasks/post-merge-plan.md`, "Sequencing") applies: regenerating band
8000-8999 leaves all fifty accepted digests and both skips byte-identical, only
`source_sha256` moves, so the dependency digests are restamped with a dated
entry naming commit `6a144038`. `status` still reads `held_out`, nothing was
printed and no prefix bytes were committed. Prefix generation runs with no
meeting runner at all — it halts at `MEETING_PHASE_REACHED` — so a meeting-layer
lever cannot reach a prefix, which is why this is a restamp and not a re-freeze.
The arm-surface digest is NOT moved by this card:
`experiments/fresh_deduction_instrument.py` is not in `ARM_SURFACE_SOURCES`'s
prompt tree and no `agents/strategic/prompts/` byte changed.

### Deviations

1. **`authored_ballot_diagnostics` now counts the marker stack.** Beyond the
   card's Expected-scope enumeration for the instrument ("the three deleted
   helpers, the import, the two arm configs"), inside a file the card owns.
   Forced by this card: it creates the doubly-rewritten class at scale (14 of
   the candidate arm's 20 reached ballots are the impostor's) and the old count
   could not see it. Labelled diagnostic only; decision 3 above.
2. **`experiments/held_out_prefixes.py` and
   `tests/experiments/test_held_out_prefixes.py` were edited.** Both are the
   preparer session's files in `tasks/post-merge-plan.md`'s ownership table. The
   restamp rule names exactly this case and puts the edit in the card's own pull
   request; the sixth freeze card
   ([held-out-prefix-freeze-6.md](held-out-prefix-freeze-6.md)) will rewrite
   `DEPENDENCY_RESTAMPS` to empty for its own band, which is a clean overwrite
   of the one entry added here.
3. **`tests/api/test_leak.py`'s `EXPECTED_EVAL_REPORT_FIELDS` gained
   `citation_relevance_version`.** A tripwire snapshot that a new
   `RecordedExperimentConfig` field is expected to move; the field is a lever
   version number and exposes no engine or role state.
4. **Three paragraphs of the manifest's verification section were re-measured**
   beyond the new dated section: the dry-run figures, the replay-rehearsal
   terminal-unit shape and the relevance paragraph. All three are asserted
   against a live run by `TestDryRun` and `TestUsageReplay`, so leaving them
   would have been a red gate and a stale document.
5. **The sizing script's path is `experiments/`, not `scripts/`** (decision 4).
6. **One extra test file,
   `tests/orchestrator/test_experiment_config.py`,** for the serializer pin the
   lever's byte-identity claim rests on.

### Limitations

- **A replay recorded with the lever ON is not loadable by the spectator DTO.**
  `api.schemas.ExperimentConfigView` forbids extra fields and was deliberately
  not widened (decision 5), so `ReplayLoader` would refuse a recording carrying
  `citation_relevance_version`. The deduction instrument's replays are never
  served by the viewer and none is committed, so nothing is broken today —
  but serving such a recording, or graduating the lever, needs the view widened
  and `frontend/src/types/api.ts` regenerated, and that is a DTO byte move this
  card's Record impact forbids. Flagged for the owner in the pull request.
- **`eval.meeting_quality.compute_conversion_report` does not know the new
  marker.** It diverts an `UNCITED_ZERO_FLAG_EJECT_MARKER` SKIP out of the
  tri-split before the `threshold_inversions` sentinel; an `off_target_coerced`
  SKIP would land in that sentinel. `eval/` is outside this card's scope, the
  lever is default-OFF and no committed recording carries the marker, so no
  published cell moves — but an eval run over lever-ON bytes would over-count
  threshold inversions.
- **`frontend/src/components/BallotCard.tsx` has no case for the new label** and
  falls through to "Recorded vote adjustment". Not a compile error (the switch
  has a default) and no committed recording carries the label.
- **The guard's observation surface is the BALLOT prompt; the grader's is every
  prompt the voter received.** The card's Evidence measured that this changes no
  verdict on the fifth run's 79 cited-observation EJECT ballots, 79 of 79; the
  agreement test controls for it by giving both callers the same lines. A future
  template that prints an observation id in a turn prompt but not in the ballot
  prompt would separate them.
- **The dry run and the replay rehearsal are not evidence about model
  judgment.** The fake provider cites the transcript's last turn whatever it
  says and the double replays an archived distribution; the manifest's own
  paragraphs say so, and the rehearsal's 16-terminal-unit candidate shape is a
  property of that archive, not a prediction.
- **No run, calibration or adopting record is authorized by this merge.** The
  lever defaults to `None`; the arms carry it for the NEXT evaluation, which the
  third calibration and the sixth authorization dispatch on their own cards.
