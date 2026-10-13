# Add authored-ballot diagnostics, the how-do guard and per-call finish reasons

**Status:** done

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

- [x] A pure `authored_ballot_diagnostics` over one unit's ballots, roles and
  ejected player, counts only, projected at unit close onto `UnitTelemetry`
  (`:4999`, via `unit_telemetry`, `:5046`) and summed in `_summarize_arm`
  (`:4845`), NOT computed at report time. Planted: a resumed run whose earlier
  units exist only as checkpoint rows reports the same totals as that run
  unresumed, and reading `records` (`:5743`) fails it.
- [x] The block carries, per arm: crew authored EJECTs naming the impostor over
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
- [x] The rewrite-reason tally keys over the members of
  `BallotTargetRewriteReason` (`meetings/schemas.py:727-733`) rather than a
  literal list, so the `off_target_coerced` member
  [the guard card](relevance-aware-citation-guard.md) adds is counted when that
  card lands on top of this one. Planted: a member added to the alias appears in
  the block with a zero count.
- [x] The report text and the manifest paragraph both state that these are
  AUTHORING-CONDITIONED diagnostics, that they flatter whichever arm authors
  more, that they are never a decision input and were never preregistered, and
  that the arms differ in the ballot register as well as the accounts surface
  until [the v5 prompt set](accounts-prompt-set-v5.md) lands. Planted: no stop
  condition, no `PairedResult` field (`:4558`) and no decision branch reads one.
- [x] A test walks the 100 committed replays under
  `audits/deduction-candidate/run-2026-09-16/`, parses each ballot as
  `VoteBallot`, feeds the run path's own function and pins the Evidence table
  exactly: candidate 51 of 81 and 30 of 81 in 27 units, reference 4 of 10 and 6
  of 10 in 6 units, coalitions 11 and 22 with 2 and 8 converting (10 wrongful
  cleared), survival 42 of 81 crew and 33 of 38 impostor, ejections 4 and 2 of
  12. It reads that archive and writes nothing to it. Planted: reading the
  authored target off `target` moves the candidate's crew row off 81.
- [x] `_NOT_AN_ASSERTION` (`:6269`) gains the governors the rule's own text
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
- [x] `ArmUsage` (`:1959`) and `CarriedUsage` (`:4972`) gain a `finish_reasons`
  distribution folded in `plus` (`:1974`), `merged` (`:1987`) and the
  abandoned-pair projection (`:5256-5263`), keying an absent reading `"null"` as
  `_role_split_rows` already does (`:6510`); `ArmSummary` carries it beside
  `cap_signal_disagreements` (`:4704`, set at `:4892`). It defaults empty, and
  that default must compare equal across instances because `abandoned_spend`
  (`:5225`) tests `spend == ArmUsage()` at `:5251`. Planted: that equality; an
  abandoned pair whose readings survive a resume; and a run reporting `"length"`
  once and `"stop"` otherwise reporting both rather than one aggregate.
- [x] Records written before this card read empty: a test loads the committed
  `report.json` and `checkpoint-final.json` through the current models and
  asserts every arm and unit reads an empty distribution rather than a
  fabricated `"stop"`, with `CHECKPOINT_SCHEMA` (`:4908`) and the replay row
  (`LLMCallRecord`, `orchestrator/replay.py:174`) unchanged.
- [x] The execution manifest gains three dated paragraphs and nothing else: one
  under `## Measures and denominators` (`:1633`) defining every diagnostic with
  its denominator and its never-a-gate status, one appended to the leak
  pre-declaration (`:989-1007`) recording the word-list repair and that the
  fifth run's record keeps BOTH readings, and one under `### How each limit is
  enforced` (`:1281`) on the `Per-call cap` bullet (`:1312`). The frozen
  analysis stays byte-identical (the test at `:4406` of the instrument's test
  module) and the authorized limits table is untouched. `docs/artifacts.md`'s
  `audits/` row (`:109`) and `tasks/README.md`'s inventory sentence (`:43`) are
  recomputed with it, and `scripts/verify_ml_evidence.py` passes offline.
- [x] Review correction: an authored target the meeting layer refused as an
  `invalid_target` — a hallucinated id, a player already dead, or the voter
  itself — is counted in an `illegal_targets` column of its own and in no
  other, so it raises no crew-on-crew harm counter, flags no unit as carrying
  one, forms no coalition and enters neither precision denominator, the 0.5
  null being the null of two LEGAL targets. Planted: one such crew ballot
  leaves every harm counter and the denominator at zero; two at one refused id
  are no coalition; a self-vote and a dead target are settled the same way; an
  off-roster id is illegal even unrewritten. Stated in the manifest's Measures
  paragraph and in the block's own note. The archive carries none, so no pinned
  figure moves.
- [x] Review correction: the Codex review on `bba09ec2` is dispositioned in
  full — the P2 by the fix above, two P1s by a fix (the detector comment
  condensed to current intent with one trailing provenance line; a populated
  carried `finish_reasons` distribution refused unless it is one non-negative
  row per call, the empty legacy mapping staying legal) and two by a reasoned
  refutation recorded in Results.
- [x] Review correction: the recordings row says what its command verifies.
  `scripts/verify_samples.sh` walks `AILIBI_SAMPLES_ROOT` only, so a bare run
  is 100 (50 + 50) and the other 200 are a second run against
  `replays/ml_corpus`; both runs are recorded.

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

## Results

Delivered on `work/fresh-deduction-instrument-diagnostics`, based on
`66d5c480`. Instrumentation only: no provider call was made on any path, no
band was drawn or rendered, no byte of any committed recording, report or usage
profile moved, and `audits/deduction-candidate/held-out/manifest.json` is
untouched. Architecture: `docs/architecture.md` "experiments/" — offline
measurement harnesses write separate artifacts, so the diagnostics are computed
in `experiments/` off the guard markers `meetings/` already records, and
`meetings/` is neither edited nor given an import of `experiments/`. The
contract this implements is the diagnosis of 2026-09-18, decisions 2, 9 and 10
as ruled in its section 11.

### Decisions

1. **The authored target is read from the guard's own testimony, never from
   `target`.** `authored_ballot_target` returns `guard_redirected_from` where a
   guard fired, `target` where none did, and `None` under `parse_default`, which
   authored nothing. Reading `target` instead collapses the candidate's crew row
   from 81 to 42 — the perturbation is pinned as a test rather than described.
2. **Cleared and converted are separate counts.** A ballot CLEARED when its
   recorded target is still a player (read off the recorded target, not off the
   rewrite reason, because more than one guard can coerce to SKIP and the
   question is what the tally saw) and CONVERTED when its recorded target is the
   one its voter authored. A coalition clears when all of its ballots did and
   converts when all of them did, which is what separates the archive's 10
   wrongful cleared from its 8 converted.
3. **A coalition is defined generally, not as "one crewmate plus the impostor".**
   Two or more ballots authored at one target in one unit, CORRECT when that
   target is the impostor and WRONGFUL otherwise. On this four-player prefix the
   two definitions coincide (the memo's §1 identities), and the general one does
   not silently stop counting on a different roster.
4. **The precision figure cannot be published without its harm counter.** A
   `model_validator(mode="before")` on `AuthoredBallotDiagnostics` refuses a
   payload carrying any of the three precision keys while either harm key is
   missing, and names the missing key. Checked on the payload so it catches a
   hand-assembled block and a report re-read from a file alike; an empty block
   carries neither half and is not a half-told claim, which is what lets the
   fifth run's committed `report.json` still parse.
5. **The block is projected at unit close, not built at report time.**
   `unit_telemetry` computes it, so the checkpoint carries it and a resumed run
   sums rows for units it never ran. The p values are computed in
   `authored_ballot_block` over the arm's summed counts, because a tail is not
   additive.
6. **The rewrite tally is derived from the schema alias.**
   `BALLOT_REWRITE_REASONS = tuple(sorted(get_args(BallotTargetRewriteReason)))`,
   so the `off_target_coerced` member the guard card adds is counted with no
   second edit here.
7. **The leak governors are crossed, not listed.** `(?:why|how|what)\s+(?:would|do|does|did)`
   replaces the three modal entries, so the family is complete by construction.
   `ROLE_LEAK_RULE`'s own text is unchanged — the repair makes the code do what
   the rule already said — and it is not a frozen-analysis constant.
8. **`finish_reasons` sums to `calls`, keying an absent reading `"null"`.** The
   empty distribution must compare equal across instances, because
   `abandoned_spend` decides whether an arm spent anything by testing
   `spend == ArmUsage()`; `ArmUsage.plus` over no calls therefore seeds no key.
9. **The fifth run's record is not restated.** Both leak readings stay published
   in `run-2026-09-16/RESULTS.md`; the manifest's dated paragraph records the
   repair and says the record keeps both.

### The figures, recomputed

Every figure of the Evidence table above reproduces from the committed archive
through the run path's own `authored_ballot_diagnostics`, over ballots parsed
back into `VoteBallot` with no new parser; the hidden roles are recovered from
each archived prefix's single scripted kill, which only an impostor can take.
The pins live in `TestTheFifthRunsArchiveReproducesTheEvidenceTable`
(`tests/experiments/test_fresh_deduction_instrument.py`) and nothing else
supplies them:

```
.venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
  -q --no-header -k "FifthRunsArchive"
9 passed, 437 deselected
```

Candidate: crew authored 81, 51 naming the impostor (one-sided exact binomial
p = 0.013 against the 0.5 null, the memo's figure), 30 crew-on-crew in 27 units,
42 of 81 crew and 33 of 38 impostor clearing the gate, coalitions 11 correct
(2 cleared, 2 converted) and 22 wrongful (10 cleared, 8 converted), 12 ejections
with 4 role-correct and 2 crew-authored. Reference: 10 / 4 / 6 in 6 units,
10 of 10 and 4 of 4 clearing, 0 correct and 1 wrongful coalition (1 cleared,
1 converted), 1 ejection with 0 role-correct. **No figure failed to reproduce.**

The leak repair's effect on the archive was measured offline before it was
written, and moves one reading: `repaired_clock`'s leaking turns and
units-carrying-one both fall from 1 to 0; `combined_accounts` keeps its 1
leaking turn in 1 unit; both arms' `opens_with_a_self_tell` counts hold at 29
and 3. That measurement is recorded in the manifest's dated leak paragraph.

### Planted and perturbed failures

Each was demonstrated by editing the module, running the named test and
restoring the edit; the edits are not in the delivered tree.

1. **The block is projected at unit close.** Perturbation: the report's
   `_summarize_arm` calls given `telemetry=[unit_telemetry(record) for record in
   records]` — the in-memory records of this sitting, which a resumed run does
   not have for its carried units.
   `-k test_the_block_is_projected_at_unit_close_not_at_report_time` →
   `1 failed`, the resumed run's `authored_diagnostics` differing from the
   uninterrupted run's on both arms. Restored → passes.
2. **The precision is refused without its harm counter.** Perturbation: the
   validator's `missing` list emptied.
   `-k test_the_precision_is_refused_without_its_harm_counter` → `1 failed`
   (`DID NOT RAISE ValidationError`). Restored → passes.
3. **A coalition can clear without converting.** Not a source perturbation but
   the synthetic unit the card names: two authored ballots on one crewmate, one
   carrying `under_gate_redirect`, counts 1 cleared and 0 converted
   (`test_a_coalition_can_clear_the_gate_without_converting`), beside its
   control where neither was rewritten and the coalition converts.
4. **The rewrite tally follows the alias.** Perturbation: `BALLOT_REWRITE_REASONS`
   written as a literal five-member tuple AND `off_target_coerced` added to
   `BallotTargetRewriteReason` in `meetings/schemas.py` — the guard card's future
   state. `-k test_the_rewrite_tally_keys_over_the_schemas_own_alias` →
   `1 failed` on the stale list. Restoring only the derived form, with the alias
   still grown → `1 passed`, the new member appearing with a zero count. Both
   edits restored.
5. **The authored layer is not the recorded one.** Perturbation:
   `authored_ballot_target` returning `ballot.target` unconditionally.
   `-k FifthRunsArchive` → `5 failed` (the candidate's crew row moving 81 → 42
   and the precision tail 0.013 → 0.044). Restored → passes. The same
   perturbation is also pinned inside the suite, without a source edit, by
   `test_reading_the_authored_target_off_the_recorded_one_moves_the_row`.
6. **The leak governors.** Perturbation: `_NOT_AN_ASSERTION` reverted to
   `why\s+would|how\s+would|what\s+would`. `-k RoleLeak` → `10 failed, 13 passed`,
   every new governor and the crossed-family test red. Restored → `23 passed`.
   The suffix perturbation the module already pinned is re-run against the
   widening by `test_the_widened_family_still_reaches_only_what_governs_the_words`:
   a confession with one of the new words TRAILING it is still a confession.
7. **The empty `finish_reasons` compares equal.** Perturbation: `ArmUsage.plus`
   seeding `{"null": 0}` before folding.
   `-k test_the_empty_distribution_compares_equal_across_instances` → `1 failed`
   (`ArmUsage().plus([]) != ArmUsage()`, which is what would make
   `abandoned_spend` write a row for a pair nobody ran). Restored → passes.
8. **Both readings rather than one aggregate.** A dry run whose provider reports
   `"length"` on its third call stops — a truncation is still a stop — and its
   partial accounting reads `{"length": 1, "stop": 2}` rather than one integer
   (`test_a_run_reports_both_readings_rather_than_one_aggregate`).
9. **Records written before this card read empty.** The committed `report.json`
   and `checkpoint-final.json` parse through the current models with every arm's
   `finish_reasons` `{}` and every unit's diagnostics zeroed, with
   `CHECKPOINT_SCHEMA` and `LLMCallRecord` unchanged
   (`test_records_written_before_this_card_read_empty`).
10. **Nothing reads the block.** Its fields are disjoint from `PairedResult`'s,
    none of them appears in `STOP_RULE`, `DECISION_RULE`,
    `WRONGFUL_EJECTION_TRADEOFF` or `PRIMARY_OUTCOME_RUBRIC`, and none of its
    symbols appears in `paired_result`'s source
    (`test_no_decision_reads_the_block`).
11. **The archive is read-only.** The walk hashes every file of
    `run-2026-09-16/` before and after and requires the fingerprints equal
    (`test_the_walk_writes_nothing_to_the_archive`), and the denominator is
    checked at 50 replays per arm so a silent zero cannot pass the pins.

### Verification

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments tests/scripts -q` | 1907 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed |
| `.venv/bin/python scripts/check_doc_facts.py` | passed |
| `.venv/bin/python scripts/verify_ml_evidence.py` | 60 checks, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — 7,876 Python passed, 20 skipped, 3 xfailed; 515 frontend tests in 19 files; strict mypy on 480 sources; 4 import contracts kept, 0 broken; 390 prompts in sync; lint, format and the production build |
| `bash scripts/verify_samples.sh` | exit 0 — 100 canonical recordings verified clean (`replays/samples/{4p1i,9p2i}`, 50 + 50; the row said 300 and is corrected in round 1 below) |
| `scripts/build_sample_report.py --check` x 4 (`replays/samples/{4p1i,9p2i}`, `replays/ml_corpus/{4p1i,9p2i}`) | all exit 0, "consistent with its replays." each |

The frozen analysis is byte-identical: `-k "frozen_analysis or amendment"` →
`10 passed` (not skipped — the worktree has full history), so
`_FROZEN_ANALYSIS_CONSTANTS` is unmoved and the authorized-limits table is
untouched.

`docs/artifacts.md`'s `audits/` row is recomputed with the manifest's new bytes:
25,974,591 → 25,981,220 tracked bytes over the same 324 files
(`git ls-files audits` with the change staged), and
`scripts/verify_ml_evidence.py` compares that row against disk offline.
`tasks/README.md`'s derived inventory sentence is updated for this card's flip
(6 ready / 60 done → 5 ready / 61 done, 66 cards).

### Review corrections, round 1 (2026-09-18)

Four blocking findings from independent review, read against `bba09ec2`. Two of
them are one defect seen from two lenses — the Codex P2 on the authored layer —
a third asks that the whole Codex review on that head be dispositioned, and the
fourth is a claim about what one verification command verifies. All four are
valid and none is refuted; two of the Codex P1s carried in the third are.
Nothing the run is judged by moves in this round: the primary outcome, the
decision rule, the minimum actionable effect, the tradeoff bound and the stop
rule are byte-identical, no band was read, no provider was called, and no byte
under `run-2026-09-16/` was rewritten.

**The defect: an id the meeting REFUSED was scored as harm.** Under
`guard_rewrite_reason="invalid_target"` the id preserved on
`guard_redirected_from` is the one the meeting layer normalized away
(`meetings/voting.py` `normalize_ballot_target`, the manager's own
`_normalize_ballot_target`), and `meetings/schemas.py` says in as many words
that it "need not name a live player" — it is a hallucinated id, a player
already dead, or the voter itself, the manager's candidate set being
living-minus-voter. The block's `else` branch scored such a ballot as
crew-on-crew and put it in the denominator read against `CREW_PRECISION_NULL`,
whose own justification is the crew pair's "two legal targets". A trial that had
no legal target is in neither half of that null. `_authored_a_legal_target` now
settles it off the layer's own typed verdict, with the unit's roster as the belt
to that brace, and the ballot is counted in an `illegal_targets` column beside
its voter role and in no other — not in `crew_authored_ejects`, not in the harm
counter, not in `units_with_crew_on_crew`, and in no coalition, two voters
naming one refused id having agreed about nobody. The perturbation is the old
branch:

```
$ PYTHONPATH=. .venv/bin/python -c "
import experiments.fresh_deduction_instrument as I
from meetings.schemas import VoteBallot
b = VoteBallot(voter='p-1', target='SKIP', confidence=0.7, primary_reason_id=None,
               rationale_text='because.', guard_redirected_from='p-99-ghost',
               guard_rewrite_reason='invalid_target')
roles = {'p-1': 'CREWMATE', 'p-2': 'CREWMATE', 'p-4': 'IMPOSTOR'}
row = lambda c: (c.crew_authored_ejects, c.crew_on_crew_authored_ejects,
                 c.units_with_crew_on_crew, c.crew_authored_illegal_targets)
print('now      ', row(I.authored_ballot_diagnostics(ballots=(b,), roles=roles, ejected_player_id=None)))
I._authored_a_legal_target = lambda ballot, roles: True
print('perturbed', row(I.authored_ballot_diagnostics(ballots=(b,), roles=roles, ejected_player_id=None)))
"
now       (0, 0, 0, 1)
perturbed (1, 1, 1, 0)
```

Six cases pin it inside the suite — the reason is a member of the schema's own
alias, so a rename cannot turn the exclusion into a no-op; the single refused
ballot; two at one refused id forming no coalition; the self-vote and the dead
target; an off-roster id that is illegal even unrewritten; and the arm block
whose crew row reads 1 of 1 with the refused ballot in its own column rather
than 1 of 2. The manifest's Measures addition gains a paragraph stating the rule
and its denominator consequence — in place, under the same dated 2026-09-18
heading, so the three places this card amends stay three — and the block's own
serialized note states it too, so a report reader meets the column explained.
**No pinned figure moves**: the fifth run's archive carries no `invalid_target`
ballot at all (44 `uncited_coerced`, 3 `under_gate_redirect`, counted over the
100 committed replays), which both reviewers established independently and the
archive walk re-confirms:

```
.venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
  -q --no-header -k "FifthRunsArchive"
9 passed, 445 deselected
```

— the same nine pins, the deselected count moving only because this round adds
cases to the module.

**The Codex review on `bba09ec2`, dispositioned in full.** Its P2 is the defect
above. Of its four P1s, two are valid and fixed here:

1. *Condense the detector comment to current intent* — valid. The craft rule
   allows one trailing provenance line and the comment above `_NOT_AN_ASSERTION`
   had grown a dated account of the fifth run and the ruling that followed it.
   The comment now explains the crossing (a question in the present or the past
   asserts as little as a modal one, and a fifth auxiliary is one word rather
   than three entries) and carries one trailing line: crossed on 2026-09-18,
   `ROLE_LEAK_RULE` unchanged. The history stays in the manifest's dated leak
   paragraph, which is the record for it.
2. *Reject inconsistent finish-reason totals in checkpoints* — valid. A
   checkpoint is a file and a resumed run merges it whole, so `CarriedUsage` now
   refuses a POPULATED distribution that is not what it claims to be: no
   negative reading, and one row per call of that same row's `calls`. The empty
   mapping stays legal at any call count, because that is exactly what a record
   written before the field reads — the committed fifth run is that record, and
   `test_records_written_before_this_card_read_empty` still passes on it.
   Planted both ways.

The other two are refuted:

3. *Gate the widened regex default-OFF behind an experimental lever* —
   refuted. The craft rule it cites governs prompt bytes and substrate
   detectors: things that change what a run RECORDS and therefore need an
   adopting record and a replay stamp, declared the way `public_account_version`
   and `attributed_testimony_version` are in
   `orchestrator/experiment_config.py`.
   `_NOT_AN_ASSERTION` is none of those. It lives in `experiments/`, is read
   only by `count_leaking_turns` over a transcript that has ALREADY been
   recorded, changes no recorded byte, no agent behaviour and no replay, and
   gates nothing — the leak column is a reported diagnostic. There is no lever
   surface to declare it on, and the repository's own precedent is this guard's:
   the whole third family was added ungated as a round-1 review fix on
   2026-09-15 (`0eb5eeb8`). Gating a measurement repair default-OFF would leave
   the default path counting a question as a confession, which contradicts
   `ROLE_LEAK_RULE`'s published text; the "preserve earlier experiment verdicts"
   half of the same rule is honoured instead, the fifth run keeping BOTH
   readings in its own `RESULTS.md` and the manifest saying so.
4. *Remove the audit reference from the serialized note* — refuted. The rule it
   cites is about user-facing copy and model speech: what a player, a spectator
   or a model is shown. This string is emitted into `report.json` under
   `audits/deduction-candidate/`, an audit artifact read beside the execution
   manifest, and a dated reference to the ruling that approved a diagnostic is
   what that record is FOR — the same document's measures are cited the same way
   throughout. Nothing renders it to a player and no model is handed it. The
   note is self-contained on its own terms even so: it says what the block is,
   what it flatters, that it is never a decision input and was never
   preregistered, and it now also explains the illegal-target column, all
   without requiring the reader to open the memo.

**The recordings row said 300 where the command verifies 100.**
`scripts/verify_samples.sh` walks `AILIBI_SAMPLES_ROOT` (default
`replays/samples`) and nothing else, so a bare run covers `4p1i` and `9p2i`
there — 50 + 50 — and never touches the 200 under `replays/ml_corpus/`
(50 + 150). The row above is corrected to what the bare run verifies, and the
second root is run rather than the claim shrunk; the four
`build_sample_report.py --check` runs beside it already named all four sets and
are unchanged by this round, which touches no replay and no report byte.

**Verification, round 1.** Re-run whole on the corrected tree:

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments tests/scripts -q` | 1915 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed — 66 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | passed |
| `.venv/bin/python scripts/verify_ml_evidence.py` | 60 checks, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — 7,884 Python passed, 20 skipped, 3 xfailed; 515 frontend tests in 19 files; strict mypy on 480 sources; 4 import contracts kept, 0 broken; 390 prompts in sync; lint, format and the production build |
| `bash scripts/verify_samples.sh` | exit 0 — 50 + 50 clean |
| `AILIBI_SAMPLES_ROOT=replays/ml_corpus bash scripts/verify_samples.sh` | exit 0 — 50 + 150 clean |

`docs/artifacts.md`'s `audits/` row is recomputed again for the manifest's
round-1 bytes: 25,981,220 → 25,982,290 over the same 324 files, which
`scripts/verify_ml_evidence.py` compares against disk offline.

### Limitations

- **These are diagnostics and only diagnostics.** They are authoring-conditioned,
  so they flatter whichever arm authors more ejections; the block says so in the
  report and the manifest says so in the record. They were not preregistered,
  nothing gates on them, and a cross-arm reading of them stays confounded until
  the v5 prompt set equalises the ballot register.
- **An illegal authored target is excluded, not interpreted.** The block says
  the ballot happened and that the meeting could not act on it; it does not say
  whether the voter MEANT a crewmate and mistyped, because nothing recorded can
  answer that. The count is reported per voter role so a run in which the
  column stops being zero is visible rather than absorbed, and the fifth run's
  archive has none, so this rule is the instrument for the next run only.
- **The archive test recovers roles from each prefix's scripted kill.** The
  archive records no role. The recovery is sound for this design — only an
  impostor kills — but it is a derivation rather than a recorded fact, and a
  future prefix shape with more than one kill action would need a different one
  (the test asserts exactly one kill per prefix rather than assuming it).
- **A completed run can never carry a `"length"` reading**, because a truncation
  is a stop. The distribution's value on a clean run is that it distinguishes
  "the provider said `stop`" from "the provider said nothing", and on a stopped
  run it names what the stop saw.
- **The arm-surface digest MOVES**, this module being in `ARM_SURFACE_SOURCES`:
  a fresh stamp is needed before the next calibration, and
  `assert_checkpoint_matches` refuses a resume across it. No run is in flight,
  so this costs nothing. The sibling v5 accounts card moves the same digest, so
  whichever lands second re-stamps.
- **Three files are shared with the wave.** The execution manifest,
  `docs/artifacts.md` and `tasks/README.md` are also touched by the v5 accounts
  card; the coordinator reconciles them at merge.
- **No record, re-record or adopting record.** No experiment becomes ON, no
  lever is declared here, and adoption is "not applicable".
