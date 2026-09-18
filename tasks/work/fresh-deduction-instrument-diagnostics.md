# Add authored-ballot diagnostics, the how-do guard and per-call finish reasons

**Status:** ready

## Outcome

The instrument reports three readings it can already derive and today throws
away. A labelled per-arm DIAGNOSTICS block counts what the crew AUTHORED before
the guards rewrote it: per-ballot precision against the impostor, its harm
counter on the same denominator, the coalition funnel, gate survival by voter
role, the guard rewrite reasons, and ejection precision against the 1/3 chance
rate. The leak guard gains the interrogative governors `ROLE_LEAK_RULE` already
excludes in words. And `finish_reason`, recorded per call since PR #459 but
reported only in calibration mode, reaches the run's report and its checkpoint.
Instrumentation only: no provider call, no band read, no recorded byte moved, no
rule the run is judged by changed, and every figure below reproduces from the
committed archive, which is how each one is planted.

## Evidence

[The diagnosis of 2026-09-18](../diagnosis-2026-09-18-fifth-run.md) is this
card's source; the owner approved its ten decisions as a set on 2026-09-18 and
the memo's section 11 records the rulings. Three are this card: decision 2 (F1),
decision 9 (F2) and decision 10 (F3). Decision 3 keeps
`supported_correct_ejection` primary and adds no secondary, which is what makes
F1 a labelled diagnostic rather than an outcome.

**The authored layer is recoverable, and only from the guard markers.** A
rewritten ballot records the target AS THE VOTER AUTHORED IT on
`VoteBallot.guard_redirected_from`, beside the typed reason on
`guard_rewrite_reason` (`meetings/schemas.py:795,812-813`), written by
`ballot_target_rewrite_provenance` (`meetings/voting.py:121`) at each rewrite
site: the coercion in `guard_ballot_citation` (`meetings/manager.py:3710,3792`)
and both redirect branches of `guard_ballot_target_graph` (`:3594`,
`:3692-3699`, `:3701-3706`). The pair serializes only when a guard fired
(`meetings/schemas.py:837-855`), so the authored target is
`guard_redirected_from` where one did and `target` otherwise, and all 300
ballots parse as `VoteBallot` from the committed replays with no new parser.

| Recomputed from `run-2026-09-16/` | reference | candidate |
| --- | --- | --- |
| Crew authored EJECTs naming the impostor | 4 of 10 | 51 of 81 |
| Crew-on-crew authored EJECTs (units carrying one) | 6 (6) | 30 (27) |
| Crew authored EJECTs clearing the citation gate | 10 of 10 | 42 of 81 |
| Impostor authored EJECTs clearing it | 4 of 4 | 33 of 38 |
| Correct coalitions authored / cleared / converted | 0 / 0 / 0 | 11 / 2 / 2 |
| Wrongful coalitions authored / cleared / converted | 1 / 1 / 1 | 22 / 10 / 8 |
| Ejections role-correct, of them crew-authored | 0, 0 of 1 | 4, 2 of 12 |

Every figure the wave named reproduces. **One carried two meanings, and this
card separates them: 10 wrongful coalitions cleared the CITATION gate, and 8
CONVERTED.** The two that cleared without converting are seeds 8006 and 8056,
where the swing's ballot passed the gate and was re-aimed onto the impostor by
`under_gate_redirect` (`:3701-3706`), the memo's two "guard-made" role-correct
ejections, and conversion means both authored ballots reached the tally on
their authored target.

**The leak gap is already published in two readings.** The run's own
`RESULTS.md:268-285` prints the frozen implementation's 1 of 50 per arm beside
the rule as written (1 candidate, 0 reference) and names the missing word: seed
8014's counted sentence is interrogative, and `_NOT_AN_ASSERTION`
(`experiments/fresh_deduction_instrument.py:6269`) carries `why would`, `how
would` and `what would` at `:6278` but no `how do`, while `ROLE_LEAK_RULE`
(`:6216`) already excludes a question governing the words.

**Why run mode drops `finish_reason`.** Not the client and not the ledger:
`CapturedCall` carries it (`:1882,1906`) and `_truncation_signals` (`:1916`),
`_cap_signals_disagree` (`:1934`) and `_unusable_response` (`:2735`) read it. It
dies at the fold, `ArmUsage.plus` (`:1974`) reducing it to one boolean count
(`:1972`), and the run report is built from `UnitGrade` and `UnitTelemetry`
(`:5922`, at `:5909-5911`) rather than the in-memory `UnitRecord`s, a resumed
run restoring earlier units from the checkpoint alone (`:5730-5731`); a
calibration, which has no resume, builds off `unit_records` (`_call_rows`,
`:6767`), which is why `CalibrationCall.finish_reason` (`:6581`) exists while
`ArmSummary` (`:4657`) has only `cap_signal_disagreements` (`:4704`). F1 and F3
therefore project at unit close, onto `UnitTelemetry.usage` (`:4999-5011`) and
`CheckpointUnit.telemetry` (`:5087,5103`).

## Acceptance

- [ ] A pure `authored_ballot_diagnostics` over one unit's ballots, roles and
  ejected player, counts only, projected at unit close onto `UnitTelemetry`
  (`:4999`, via `unit_telemetry`, `:5046`) and summed in `_summarize_arm`
  (`:4845`), NOT computed at report time. Planted: a resumed run whose earlier
  units exist only as checkpoint rows reports the same totals as that run
  unresumed, and reading `records` (`:5743`) fails it.
- [ ] The block carries, per arm: crew authored EJECTs naming the impostor over
  crew authored EJECTs, with a one-sided binomial p against the 0.5 null of two
  legal targets; ALWAYS beside crew-on-crew authored EJECTs and the units
  carrying one; the coalition funnel, whose cleared and converted columns are
  different counts; authored / cleared / coerced by voter role; and ejections
  with role-correct and crew-authored role-correct counts against the 1/3
  chance rate. The tail comes from a one-sided binomial helper beside
  `exact_mcnemar_p` (`scripts/paired_stats.py:95`), imported at `:165`. Planted:
  a report with the precision figure and no harm counter is refused, and a unit
  whose two authored ballots clear `guard_ballot_citation`, one carrying
  `under_gate_redirect`, counts 1 cleared and 0 converted.
- [ ] The rewrite-reason tally keys over the members of
  `BallotTargetRewriteReason` (`meetings/schemas.py:727-733`) rather than a
  literal list, so the `off_target_coerced` member
  [the guard card](relevance-aware-citation-guard.md) adds is counted when that
  card lands on top of this one. Planted: a member added to the alias appears in
  the block with a zero count.
- [ ] The report text and the manifest paragraph both state that these are
  AUTHORING-CONDITIONED diagnostics, that they flatter whichever arm authors
  more, that they are never a decision input and were never preregistered, and
  that the arms differ in the ballot register as well as the accounts surface
  until [the v5 prompt set](accounts-prompt-set-v5.md) lands. Planted: no stop
  condition, no `PairedResult` field (`:4558`) and no decision branch reads one.
- [ ] A test walks the 100 committed replays under
  `audits/deduction-candidate/run-2026-09-16/`, parses each ballot as
  `VoteBallot`, feeds the run path's own function and pins the Evidence table
  exactly: candidate 51 of 81 and 30 of 81 in 27 units, reference 4 of 10 and 6
  of 10 in 6 units, coalitions 11 and 22 with 2 and 8 converting (10 wrongful
  cleared), survival 42 of 81 crew and 33 of 38 impostor, ejections 4 and 2 of
  12. It reads that archive and writes nothing to it. Planted: reading the
  authored target off `target` moves the candidate's crew row off 81.
- [ ] `_NOT_AN_ASSERTION` (`:6269`) gains the governors the rule's own text
  excludes: `how do`, and the audited siblings `how does`, `how did`, `why do`,
  `why does`, `why did`, `what do`, `what does`, `what did`. Planted with
  SEED-FREE strings in the style of
  `test_a_supposition_or_a_question_is_not_a_confession`
  (`tests/experiments/test_fresh_deduction_instrument.py:8578`), one per new
  governor, plus the suffix perturbation `:8604` already pins. The widening is
  measured: on the archive it moves one reading, the reference arm's leaking
  turns and units-with-one both 1 to 0, while the candidate's 1 leaking turn,
  both arms' self-telling openings (29 and 3, `opens_with_a_self_tell`, `:6336`)
  and every existing test string hold.
- [ ] `ArmUsage` (`:1959`) and `CarriedUsage` (`:4972`) gain a `finish_reasons`
  distribution folded in `plus` (`:1974`), `merged` (`:1987`) and the
  abandoned-pair projection (`:5256-5263`), keying an absent reading `"null"` as
  `_role_split_rows` already does (`:6510`); `ArmSummary` carries it beside
  `cap_signal_disagreements` (`:4704`, set at `:4892`). It defaults empty, and
  that default must compare equal across instances because `abandoned_spend`
  (`:5225`) tests `spend == ArmUsage()` at `:5251`. Planted: that equality; an
  abandoned pair whose readings survive a resume; and a run reporting `"length"`
  once and `"stop"` otherwise reporting both rather than one aggregate.
- [ ] Records written before this card read empty: a test loads the committed
  `report.json` and `checkpoint-final.json` through the current models and
  asserts every arm and unit reads an empty distribution rather than a
  fabricated `"stop"`, with `CHECKPOINT_SCHEMA` (`:4908`) and the replay row
  (`LLMCallRecord`, `orchestrator/replay.py:174`) unchanged.
- [ ] The execution manifest gains three dated paragraphs and nothing else: one
  under `## Measures and denominators` (`:1633`) defining every diagnostic with
  its denominator and its never-a-gate status, one appended to the leak
  pre-declaration (`:989-1007`) recording the word-list repair and that the
  fifth run's record keeps BOTH readings, and one under `### How each limit is
  enforced` (`:1281`) on the `Per-call cap` bullet (`:1312`). The frozen
  analysis stays byte-identical (the test at `:4406` of the instrument's test
  module) and the authorized limits table is untouched. `docs/artifacts.md`'s
  `audits/` row (`:109`) and `tasks/README.md`'s inventory sentence (`:43`) are
  recomputed with it, and `scripts/verify_ml_evidence.py` passes offline.

## Constraints

No live provider call, on any path, for any reason. No band is drawn, rendered,
printed or tallied. Bands 3000-3999 through 8000-8999 are all development data,
but no prefix and no rendered prompt is printed by this card's tests or its
Results, and `audits/deduction-candidate/held-out/manifest.json` is untouched,
still reading `held_out` for 8000-8999 until
[the sixth freeze](held-out-prefix-freeze-6.md) moves it. Nothing under
`run-2026-09-16/` is rewritten; the test READS that archive.

The primary outcome (`:659`), decision rule (`:677`), minimum actionable effect
(`:672`), `WRONGFUL_EJECTION_TRADEOFF` (`:693`) and `STOP_RULE` (`:722`) do not
change, and decision 7 is that the tradeoff is NOT restated, so no clause is
added to it here either: the diagnostics are reported, never gated, and F1 is
never a decision input. The Evidence table's figures are what the owner's merge
authorizes. F5 and F8 are out of scope of every card of this wave.

No prompt byte and no meeting-layer byte changes here. `meetings/` is not edited
and gains no import of `experiments/`; the diagnostics are computed in the
instrument off the guard markers `meetings/` already records, the direction
`.importlinter` and `pyproject.toml` permit (`experiments/` is deliberately
outside the contract's root packages). The wave's meeting-layer change is
[the guard card](relevance-aware-citation-guard.md)'s and stays DEFAULT-OFF
behind `citation_relevance_version`, declared the way `public_account_version`,
`attributed_testimony_version` and `evidence_reasoning_version` are
(`orchestrator/experiment_config.py:42,44-45`;
`meetings/evidence_profile.py:72-75`); this card declares no lever and is the
instrument's ONE writer in wave A. No recording, no re-record, no adopting
record.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`scripts/paired_stats.py` (one one-sided binomial helper) and
`tests/scripts/test_paired_stats.py`,
`audits/deduction-candidate/execution-manifest.md` (three dated paragraphs),
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived inventory
sentence, this card. Not in scope: `orchestrator/`, `meetings/`, `llm/`, every
prompt template, and every committed recording, report and usage profile.

Delivered on `work/fresh-deduction-instrument-diagnostics` and one pull request
into `main`, a merge commit or fast-forward and never a squash, with the trailer
`Card: tasks/work/fresh-deduction-instrument-diagnostics.md`. Wave A is this
card in parallel with [the v5 accounts prompt set](accounts-prompt-set-v5.md),
both based on `main` and sharing no source file; the execution manifest,
`docs/artifacts.md` and `tasks/README.md` are the three the coordinator
reconciles at merge. Wave B is [the guard](relevance-aware-citation-guard.md),
stacked on this branch because both edit the instrument and its test module,
then [the third calibration](fresh-deduction-calibration-3.md) on all three,
then, once it reports, the sixth authorization with
[its limits card](fresh-deduction-limits-6.md) and
[the sixth freeze](held-out-prefix-freeze-6.md) alongside that card.

## Record impact

Amends one `audits/` document with three dated paragraphs. No recording, report,
DTO, metric or weight byte moves; no committed measurement record is
regenerated; no experiment becomes ON; no adopting record is created; the
held-out record at `MANIFEST_PATH` is untouched.

The arm-surface digest MOVES, this module being in `ARM_SURFACE_SOURCES`
(`:4927-4935`): a fresh stamp before the next calibration, not a re-record, and
`assert_checkpoint_matches` (`:5394`) refuses a resume across it, which costs
nothing with no run in flight. The sibling accounts card moves the same digest
through `agents/strategic/prompts/loader.py`, so whichever lands second
re-stamps. `InstrumentReport` (`:4713`) and `ArmSummary` are `extra="forbid"`,
so the new fields are additive, and the report carries counts only, so
`assert_report_holds_no_prefix_bytes` (`:4808`) passes over the block unchanged.
The leak change edits the regex, never `ROLE_LEAK_RULE`'s own text, which is not
in `_FROZEN_ANALYSIS_CONSTANTS` (the instrument's test module, `:198-211`).

## Validation

`uv run pytest tests/experiments tests/scripts -q` (fake and replay doubles
only, at $0), then `uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh` run whole in a clean worktree. Neither the live
evaluation nor a live calibration is a check here or is run here.
