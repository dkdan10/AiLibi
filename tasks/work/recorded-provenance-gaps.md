# Close the recorded-provenance gaps the follow-up review found

**Status:** done

## Outcome

A recording states which observation clock produced it, a committed evaluation
artifact hashes only reproducible bytes, the live-versus-reconstructed memory
guard is bound to the meeting it checks, and the v3 policy re-decision is a
profile option rather than an unconditional core check. A candidate measurement
can then be labelled and reproduced instead of pooling two clocks into one arm.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each claim
from the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md), findings
NC4-3, NC6-1, NC6-2, NC3-1 and FU-ORA-2) on this checkout before implementing.

- **NC4-3.** `eval/report_schema.py:224-236` — `GameProvenance` carries the
  factory kind, experiment config, substrate flags and both tactical policy
  stamps, but no observation-clock version, so v1 and v2 recordings fold into
  one arm. The replay rows already carry it: `experiments/deduction_evaluation.py`
  reads `row.temporal_observation_version` when it checks an arm's clock.
- **NC6-1.** `experiments/investigation_evaluation.py:509` writes `view.json`
  including an mtime-derived `metadata.created_at`, and `:771` then hashes every
  file in the output directory into `artifact_hashes`, so committed hashes are
  timestamps and cannot reproduce. The reader projection already excludes
  `created_at`; the writer does not.
- **NC6-2.** The live-versus-reconstructed memory guards at
  `experiments/investigation_evaluation.py:465-472` and
  `experiments/deduction_evaluation.py:233-248` are existential substring
  matches over every prompt the agent ever received, so serving meeting 0's
  memory for meeting 1 passes silently. A mutation survived both harnesses'
  adverse tests.
- **NC3-1.** `eval/replay_walk.py:577` invokes the v3 policy re-decision for
  every `supports_experiments` profile on a format-3 recording (constructed at
  `:545-561`), and `orchestrator/policy_reconstruction.py` raises a bare
  `ValueError` that bypasses the profile's `on_violation` hook, contradicting the
  walker's documented "no check is core-mandatory" contract.
- **FU-ORA-2.** The committed investigation captures record and reconstruct in
  one process at one commit, so `outcome_verified=True` attests self-consistency.
  A refuter showed the oracle does catch an injected policy defect when the
  recording and the tree differ — that cross-tree walk is simply never run.

## Acceptance

- [x] Review correction: Decision 1 claimed the new clock field answered the
  earlier review's C4-5 complaint, and the field exhibited exactly C4-5's
  defect — `Literal[1, 2]` accepts a JSON `true` (`bool` subclasses `int`) and
  a report whose clock could not be read loaded as clock v1. The recorded row's
  integer check is now one shared function run at every mirror of the stamp;
  proved by `tests/eval/test_report_schema.py::test_a_committed_report_whose_clock_is_a_json_boolean_is_refused`
  (and the four parametrized site tests it sits beside), which load as `1`
  before the fix and raise after it.
- [x] Review correction: pull request #441 was `CONFLICTING` against its base,
  and round 1 declared the shared `tests/fixtures/` inventory row a value
  someone else would merge. It is merged here instead: `work/evidence-renderer-salience`
  at `bd6f05dc` is merged in (never rebased), the row recomputed from
  `git ls-files` with the merge staged, and the result proved by
  `.venv/bin/python scripts/verify_ml_evidence.py` (exit 0, "every check
  passed") and `tests/scripts/test_verify_ml_evidence.py` (80 passed).
- [x] Review correction: three non-blocking defects were code, not prose, and
  are fixed with their own perturbations — the served provenance cards now name
  the observation clock (`frontend/src/components/PublicResults.test.tsx`), the
  historical-projection guard and its exclusion set read one shared key tuple
  (`tests/scripts/test_build_sample_report.py::test_the_committed_shape_guard_names_every_projected_identity_key`),
  and the v3 mismatch's "no half-stepped walk" claim is pinned rather than
  argued (`tests/eval/test_v3_cross_tree_reconstruction.py::test_a_mismatch_cannot_be_swallowed_onto_a_half_stepped_reconstruction`).
- [x] Review correction: the merge-tree conflict count in "Review corrections,
  round 1" (`grep -c '<<<<<<<'` → 1) reproduced on no committed tree — the
  sentence stating it puts the literal marker into the card, and the merge-tree
  output diffs the card too, so the unanchored pattern matches twice at
  `17e929f4`. The count is now anchored to the diff's added lines and paired with
  the structural count it summarises: on the committed tree
  `git merge-tree 201849fc origin/work/evidence-renderer-salience HEAD` piped
  through `grep -c '^+<<<<<<<'` → 1 and `grep -c '^changed in both'` → 1, both
  recorded in "Review corrections, round 2".
- [x] Review correction: the Verification table's standalone `tests/api` +
  `tests/scripts` figure (`1721 passed, 2 skipped`) reproduces on no tree. The
  row now states the trio run this round made on the committed tree —
  `uv run pytest tests/eval tests/api tests/scripts -q` → `2825 passed, 3
  skipped`, exit 0 — and the collection count that contradicts the old figure
  (`.venv/bin/python -m pytest tests/api tests/scripts --collect-only -q` →
  `1738 tests collected`) is recorded in "Review corrections, round 1".
- [x] Review correction: a second lens reported the same figure independently and
  named the base-tree comparison it also made. The "before this card's fixes and
  green after" clause and the per-file counts are dropped rather than restated,
  because no command run in this round produced them; `git diff 201849fc HEAD
  --stat -- tests/api tests/scripts` (58 insertions, no deletions) is what now
  carries "no existing test was removed or weakened".
- [x] Review correction: `docs/artifacts.md`'s `tests/fixtures/` inventory row is
  a cell two concurrent cards write, so pull request #441 is `CONFLICTING`
  against its declared base. The merged value is stated (29 files / 2,098,510
  bytes) with the command that computes it, the pull request body's "shares no
  file with the renderer card" claim is corrected, and a one-sided resolution is
  shown failing `.venv/bin/python scripts/verify_ml_evidence.py` (exit 1,
  "promises 27 files, the index tracks 25"), which
  `tests/scripts/test_verify_ml_evidence.py::test_every_counted_registry_row_matches_the_index`
  carries into `bash scripts/check.sh`.
- [x] `GameProvenance` gains `temporal_observation_version: int | None`, carried
  through `ReplayMetadataView` and `ReportProvenanceGroupView` in
  `api/schemas.py`. Absent stays unknown — a historical recording is not
  relabelled — and mixed v1/v2 inputs no longer group into one arm.
- [x] All four committed `--check` runs stay green through
  `scripts/build_sample_report.py`'s historical projection
  (`_historical_report_exclusions` at `:203`, `_can_project_historical` at
  `:230`); no committed report is regenerated to accommodate the new field.
- [x] `view.json` is written without the mtime-derived `created_at` before it is
  hashed, matching what the reader projection already excludes. A rebuild on a
  different machine reproduces the artifact hashes; the current bytes do not.
- [x] Both memory guards are keyed by meeting (and voter), with a planted
  cross-meeting case: serving meeting 0's memory for meeting 1 fails where it
  passes today.
- [x] `ReplayWalkConfig` gains `reconstruct_v3_policies: bool = False` and
  `WalkViolationKind` (`eval/replay_walk.py:237-251`) gains a
  `v3_policy_mismatch` member; a disagreement routes through `on_violation`
  instead of raising. Both are public-type changes — enumerate the consumers of
  each and name which profiles enable the option.
- [x] A cross-tree reproduction check exists: walk a committed format-3
  recording under a later tree so a policy change is detected, and a planted
  policy defect makes it fail. A same-process, same-commit capture is not
  accepted as evidence for that check.
- [x] Every new gate has a planted or perturbed failure proving it detects the
  claimed defect, not merely that the implementation exists.

## Constraints

No committed report or recording is rewritten, re-recorded or regenerated; all
four `--check` runs must be green on the existing bytes. No provider calls, new
dependencies or new levers. Candidates stay default-OFF; nothing here adopts an
experiment. Follow `docs/architecture.md` Layering, Enforced boundaries and
Determinism, and keep the privileged reader boundary intact. Prerequisite: none,
but the schema field is a semantic prerequisite for the fresh-model instrument
card, so land it before that card's arms are labelled.

## Expected scope

`eval/report_schema.py`, `eval/replay_walk.py`, `eval/balance_eval.py`,
`api/schemas.py`, `api/replay_loader.py`, `api/public_results.py`,
`scripts/build_sample_report.py`, `experiments/investigation_evaluation.py`,
`experiments/deduction_evaluation.py`, and their tests under `tests/eval`,
`tests/api` and `tests/scripts`. Generated frontend types and the type-fidelity
fixture may follow through when a served DTO gains the field.

## Record impact

Added provenance fields only; absent means unknown and no historical stamp
changes meaning. Future recordings carry the observation-clock version, so
reports produced after this card group differently from reports produced before
it — that is the point of NC4-3 and must be stated wherever the two are
compared. A new `v3_policy_mismatch` violation kind can newly fail a profile
that previously passed: name in Results which profiles enable
`reconstruct_v3_policies` and which keep the default `False`. Committed
`artifact_hashes` in the investigation evaluation become reproducible only for
artifacts regenerated after the writer change; the existing committed values
stay historical and are not retro-certified.

## Validation

`uv run pytest tests/eval tests/api tests/scripts -q` for the planted
cross-meeting, cross-tree and violation-routing cases, then
`bash scripts/check.sh`, then `bash scripts/verify_samples.sh`, then the four
derived report checks:

```sh
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
```

Then the browser journeys with `cd frontend && npm run e2e`, because the served
provenance views change shape.

## Results

Implemented on `work/recorded-provenance-gaps` in five implementation commits
off `201849fc`: a frozen format-3 fixture, the observation-clock provenance
field, the `view.json` timestamp exclusion, the meeting-keyed memory guard, and
the v3 policy re-decision as a profile option. Those five are what the sections
below describe. The branch itself carries more than five — the review rounds
below added documentation commits, one closeout round added source, and one
merge commit brought in the base branch — so a reader counting commits should
count `git log --oneline --first-parent 201849fc..HEAD`, not this list.

Architecture references. `docs/architecture.md` **Layering** — the provenance
field is added at the `eval`/`api` reader layer over recordings; nothing in
`agents/` sees it. **Enforced boundaries** — no import-linter contract moves,
and the privileged reader boundary is untouched: the clock version is recorded
metadata about a recording, never agent-visible evidence, which is why
`tests/api/test_leak.py`'s recursive served-field snapshot admits it explicitly
rather than by silent growth. **Determinism and the substrate ladder** and its
**Observation timing and public identities** subsection are the governing
contract for the new field: "Tick-row versions identify partial runs; missing
means legacy" is exactly the rule the field follows — absent is unknown, not v1.

### The review's claims, reproduced on this checkout first

Run at `201849fc` before any edit.

* **NC4-3.** `grep -n "temporal_observation_version" eval/report_schema.py
  eval/balance_eval.py api/schemas.py` → exit 1, no matches. The clock was not
  part of the recorded identity anywhere.
* **NC6-1.** Two runs of `.venv/bin/python -m experiments.investigation_evaluation
  --output-dir <fresh directory>` (the flag is `required=True`; the earlier
  spelling of this line omitted it and was not runnable — see "Review
  corrections, closeout round 1"): `artifact hash keys: 245 differing: 35 / by
  basename: {'view.json': 35} / everything else identical: True`, with `created_at`
  `2026-09-08T04:11:36.838241+00:00` vs `...T04:11:50.234935+00:00` and `view
  identical modulo created_at: True`.
* **NC6-2.** Replacing `meeting.meeting_id` with `report.meetings[0].meeting_id`
  in each harness's memory comprehension left both adverse suites green:
  `tests/eval/test_investigation_evaluation.py` 3 passed,
  `tests/eval/test_deduction_evaluation.py` 9 passed.
* **NC3-1.** A `ReplayWalkConfig` byte-equal to `eval/leak_scan.py`'s declared
  no-check profile, walking a format-3 recording with one action retyped:
  `RAISED ValueError recorded tactical actions disagree with the version-3
  policy at tick 0 | on_violation calls: []`. The clean recording walked
  completed, with the reconstruction running unasked.
* **FU-ORA-2.** `git grep -l temporal_observation_version -- '*.jsonl'` → exit 1
  across the 376 tracked recordings (`git ls-files '*.jsonl' | wc -l` → 376), so
  the v3 oracle had never run against any committed bytes.

### Decisions

1. **The field is typed `TemporalObservationVersion` (`Literal[1, 2] | None`)
   behind an integer check, not the card's literal `int | None`.** The alias is
   a narrowing to the two versions `observation/version.py` can resolve: a
   report claiming a clock this build cannot reconstruct under is a corrupt
   claim. The alias alone is not enough, and saying so is the correction this
   card was reopened for — `Literal[1, 2]` rejects `0`, `3`, `2.0` and `"2"`
   but accepts a JSON `true`, because Python's `bool` subclasses `int` and
   `True == 1`. What is enforced now is the alias plus
   `orchestrator.replay.require_integer_temporal_version`, a `mode="before"`
   field validator that refuses any value whose `type` is not exactly `int`.
   The recorded field it mirrors (`ReplayEntry.temporal_observation_version`)
   runs the same function object rather than a copy of it, and the served views
   run a deliberately shadowed copy pinned against it by test. That is the
   whole of the claim: it is not an appeal to a house style, and no claim is
   made here about `ExperimentConfigView.format_version`, which carries a bare
   alias and is not an example of the rule.
2. **`current-report` enables `reconstruct_v3_policies`; every other shipping
   profile keeps the default `False`.** Enabling it preserves exactly what that
   profile already did, now routed through its own hook. Leaving
   `leak-scan-factory` off is the point of NC3-1: its declared policy is no
   checks and `KeyError(tick)`, and the unconditional re-decision replaced both.
3. **`PolicyReconstructionMismatch` is a `ValueError` subclass.** The walker has
   to recognise this one disagreement without catching every `ValueError` the
   decision path can raise, and a subclass leaves `api/replay_loader`'s own
   reconstruction — which catches nothing — byte-identical in behaviour.
4. **The `view.json` exclusion is a function returning a fresh mapping, not a
   module constant.** A `MappingProxyType` constant was tried first and silently
   dropped the whole `metadata` block rather than one field (Pydantic's
   `exclude` needs a plain nested mapping); a shared mutable dict would be
   module-level mutable state. The regression test asserts the block survives.
5. **The memory guard's meeting partition is read from the recorded per-meeting
   calls, with a live-subset assertion.** The provider protocol carries no
   meeting id, so the partition has to come from somewhere; requiring every
   recorded `(agent, prompt)` pair to be one the live provider was handed keeps
   the live prompts the thing compared rather than letting the reader's bytes
   stand in for them.
6. **The cross-tree fixture is committed under `tests/fixtures/`**, following the
   `tests/fixtures/prompt_regression/` precedent for committed `.jsonl`. It is
   outside `replays/`, so `verify_samples.sh`, the four `--check` sets and
   `check_doc_facts.py`'s replay counter (scoped to `replays/samples/`) do not
   see it.

### Consumers of the two changed public types

`ReplayWalkConfig` has ten shipping construction sites. Only two set
`supports_experiments=True` and could therefore ever have reached the v3
re-decision:

| Profile | Module | `reconstruct_v3_policies` |
| --- | --- | --- |
| `current-report` | `eval/balance_eval.py:933` | **`True`** — preserves today's behaviour, now coded |
| `leak-scan-factory` | `eval/leak_scan.py:950` | `False` (default) — restores its declared no-check policy |
| `validity-gate` | `eval/validity.py:499` | `False` (never reached it) |
| `win-condition-selfcheck` | `eval/win_condition_selfcheck.py:205` | `False` |
| `kill-gift` | `eval/balance_eval.py:914` | `False` |
| `watchability-referee` | `eval/watchability.py:1465` | `False` |
| `kill-craft` | `eval/kill_craft.py:527` | `False` |
| `solvability` | `eval/solvability.py:698` | `False` |
| `evidence-honesty` | `eval/evidence_honesty.py:2551` | `False` |
| `funnel-instrument` | `eval/funnel.py:254` | `False` |

Test profiles: `v3-policy-test` (`tests/eval/test_investigation_replay_walk.py`)
and `v3-cross-tree` (`tests/eval/test_v3_cross_tree_reconstruction.py`) set it
`True`; the profiles in `tests/eval/test_replay_walk.py`,
`tests/orchestrator/test_experimental_evaluation_integrity.py` and
`tests/orchestrator/test_temporal_delivery.py` keep the default.
`api/replay_loader.py:1534` constructs `PolicyReconstruction` on its own walk,
not through this walker, and is deliberately unchanged: there the reconstruction
builds the memories the reader serves, so it is load-bearing rather than a check.

`WalkViolationKind` gains `v3_policy_mismatch`. Its consumers are the ten
`on_violation` hooks above. Every one either forwards the kind verbatim
(`eval/balance_eval.py:927` into `ReplayIntegrityError(code=...)`), looks it up
with a default (`eval/evidence_honesty.py:2547`, `eval/solvability.py:694`), or
falls through to an explicit "unexpected walk violation" branch
(`eval/kill_craft.py:522`, `eval/funnel.py:244`), so the new member breaks no
hook — and only the one profile that opts in can produce it.

### Verification

Every exit code below was captured directly from the command, never from a
pipeline.

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — ruff check + format, lint-imports, `validate_task_docs` (390 historical phase tasks and 390 prompts; 43 work cards), `generate_prompts --check`, mypy "no issues found in 471 source files", `7216 passed, 20 skipped, 3 xfailed`, then frontend lint + `tsc:check` + `19 files / 514 tests` + build |
| `uv run pytest tests/eval tests/api tests/scripts -q` (the card's named trio) | exit 0 — `2825 passed, 3 skipped in 2450.75s`, run standalone on the committed tree in review round 1. The same suites run again inside the gate's pytest leg, which collects all of `tests/` — a strict superset — and that leg is the run of record. The per-suite figures this row carried before round 1 were not reproducible and are superseded; see "Review corrections, round 1". |
| `bash scripts/verify_samples.sh` | exit 0, "All 50 samples verified clean." twice — 100 canonical reconstructions |
| `build_sample_report.py --check` × 4 (`replays/samples/{4p1i,9p2i}`, `replays/ml_corpus/{4p1i,9p2i}`) | all exit 0, "consistent with its replays." each |
| `cd frontend && npm run e2e` | exit 0 — 16 Playwright tests, `13 passed (3.9m)`, 3 skipped |

The first `check.sh` run on this branch exited **2**: the two
`ReportProvenanceGroupView` literals in
`frontend/src/components/PublicResults.test.tsx` were incomplete once the DTO
gained a required additive field (`TS2741`). That is real follow-through, not a
flake, so it was folded into the commit that caused it rather than appended,
which keeps every commit on the branch green under `npm run tsc:check`. The
recorded run above is the gate on the final tree.

No committed report or recording changed: `git diff --name-only 201849fc HEAD --
replays audits` names no file under `replays/` at all, and exactly one under
`audits/` — `audits/deduction-candidate/held-out/manifest.json`, which arrives
whole from the merged base branch and not from this card (see "Review
corrections, closeout round 1"). This card's own commits move nothing under
either: `git diff --name-only 201849fc db6ffb9e -- replays audits` is empty.
`docs/artifacts.md` carries two inventory rows this branch is responsible for
reporting — `tests/fixtures/`, which this card's fixture moves and the merge
then merges (23 files / 2,054,135 bytes at the base → 25 / 2,067,334 on this
card alone → **29 / 2,098,510** merged), and `audits/`, which the base branch's
restamp moves (14,852,039 bytes / 202 files) and which this card does not
touch. Both are recomputed from `git ls-files` with the change staged rather
than copied. The frozen held-out manifest needs no restamp from this card:
intersecting `git diff --name-only 201849fc db6ffb9e` and this round's
uncommitted set with `experiments.held_out_prefixes.GENERATOR_SOURCES` gives
`[]` both times, the two sources the manifest does record
(`agents/memory/store.py`, `experiments/held_out_prefixes.py`) are the base
branch's, and `tests/experiments/test_held_out_prefixes.py` is green
(28 passed).

### Planted and perturbed failures

Each was demonstrated by editing the tree, running the check, and restoring.

1. **Historical projection (NC4-3).** Deleting `"temporal_observation_version":
   True` from `_historical_report_exclusions` →
   `build_sample_report.py --sample-dir replays/samples/4p1i --check` exits 1
   with "is STALE — it does not match a rebuild from its own replays". Restored,
   exit 0.
2. **Provenance grouping (NC4-3).**
   `tests/eval/test_balance_eval.py::test_mixed_observation_clocks_do_not_fold_into_one_provenance_group`
   carries its own perturbation inline: clearing the new field on both reports
   restores the pre-change identity and collapses two groups into one
   (`game_ids == ("clock-v1", "clock-v2")`).
3. **`view.json` reproducibility (NC6-1).**
   `test_written_view_is_hashed_without_the_filesystem_timestamp` moves the
   replay file's mtime — the only machine-varying input — and asserts the
   un-excluded dump (what the writer used to emit) changes while the bytes now
   written do not. Two full harness runs after the fix: `245 differing: 0`,
   against `245 differing: 35` before.
4. **Cross-meeting memory (NC6-2).** `tests/eval/test_meeting_memory_guard.py`
   plants a mis-indexed reconstruction at `ReplayLoader.get_meeting_memory` for
   both harnesses. Restoring the pre-fix existential guard in the source makes
   all three planted tests fail and leaves the two controls passing; the fixed
   guard passes all five. Re-applying the review's own `meetings[0]` source
   mutation now fails 4 of the 12 harness tests it previously left green.
5. **Profile routing (NC3-1).**
   `test_the_v3_reconstruction_is_a_profile_option_not_a_core_check` walks a
   tampered format-3 recording under a config byte-equal to
   `leak-scan-factory`'s: with the option off the walk completes and no hook
   fires; with it on the profile's own `KeyError` is raised and the hook records
   `["v3_policy_mismatch"]`.
6. **Cross-tree reconstruction (FU-ORA-2).**
   `tests/eval/test_v3_cross_tree_reconstruction.py` walks
   `tests/fixtures/v3_policy_reconstruction/replay-seed-1.jsonl`, recorded by the
   tree at `201849fc` before this card edited any source. A planted crewmate
   policy that stops submitting task attempts fails it at tick 2 with
   `v3_policy_mismatch`, and the same defective tree walks the same bytes clean
   with the option off. The same defect applied as a source edit to
   `agents/tactical/crewmate_policy.py` rather than a monkeypatch reproduces it
   identically, then was restored.

### Limitations

* **The clock field changes how future reports group, on purpose.** A report
  produced after this card separates v1 from v2 where a report produced before
  it pooled them. Any comparison spanning the two must say so; that is NC4-3's
  whole point and it is stated in Record impact.
* **Committed `artifact_hashes` are not retro-certified.**
  `audits/investigation-candidate/2026-09-06-normal-policies.json` keeps its 35
  timestamp-derived `view.json` hashes as a historical record. Only artifacts
  regenerated after this change reproduce.
* **The "different machine" claim is argued, not measured.** Both harness runs
  were on one machine. What the test establishes is stronger than a rerun and
  weaker than a second host: `created_at` was the only field in the projection
  derived from anything outside the recording, and moving its source now leaves
  the written bytes unchanged.
* **`leak-scan-factory` loses a check it never declared.** Restoring its no-check
  contract means a format-3 recording walked by the leak scan is no longer
  policy-re-decided. Nothing regresses today — no committed recording is
  format 3 — but a future consumer that wanted the re-decision there must ask
  for it.
* **The frozen fixture is a tripwire by design.** A tactical-policy or
  observation change that makes
  `tests/eval/test_v3_cross_tree_reconstruction.py` fail means the current tree
  decides differently from the recorded bytes. That is the finding, not a stale
  fixture; the fixture README says so, and re-recording it is a decision rather
  than maintenance.
* **The cross-tree walk is procedurally cross-tree; today it is not yet
  decision-diverse.** The fixture was recorded at `201849fc` and is walked here,
  which is what makes it a cross-tree check by construction. But this branch
  changes no file on the reproduce path — `git diff --name-only 201849fc HEAD`
  filtered to `agents/`, `engine/`, `observation/` and `meetings/` names only
  the base branch's two `agents/memory/` files, neither of which the tactical
  decision path reads — so the tree that re-decides is, for those decisions,
  the tree that recorded. The check therefore cannot detect drift *today*; its
  value is prospective, and the planted-defect half is what shows it would.
  Stated because "cross-tree" otherwise sounds like a measurement rather than a
  standing tripwire.
* **The cross-tree oracle covers 9 ticks and 59 recorded actions** of one seed —
  moves, task attempts, a kill, two vents and a body report. It is a real
  cross-tree check, not a broad one, and a 9-tick prefix does not exercise every
  decision branch: while choosing the planted defect I tried two others
  (returning `None` from `CrewmatePolicy._first_visible_body`, and from
  `agents.tactical.investigation._visible_body_intent`) and neither changed a
  reproduced action on these bytes. I did not chase why, so treat that as "this
  prefix does not cover those branches", not as a claim about them. A wider or
  longer fixture is a separate decision.
* **The memory guard now depends on the recording mirroring the live prompts.**
  That dependency is asserted rather than assumed, and a recording that does not
  mirror them is refused — but a harness whose recorder and provider both
  drifted the same way would still agree with itself. This is the same shared
  oracle limitation FU-ORA-1 names for the renderer, and this card does not
  close it.

### Review corrections, round 1 (2026-09-08)

Three findings from the independent verifiers, two distinct defects, both in
this card's evidence prose rather than in its code. This round changed no
source file, no test and no committed artifact: `git diff e26045bd HEAD --stat`
touches `tasks/work/recorded-provenance-gaps.md` alone.

**1 — the standalone trio figure reproduced on no tree.** The Verification row
used to read: "Each suite was also run on its own during development:
`tests/eval` `1089 passed, 1 skipped`; `tests/api` + `tests/scripts` `1721
passed, 2 skipped` before this card's fixes and green after". That sentence is
superseded. `1721 + 2 = 1723` is not the size of those two directories at any
commit on this branch:

* `.venv/bin/python -m pytest tests/api tests/scripts --collect-only -q` at
  `e26045bd` → `1738 tests collected`.
* `git diff 201849fc HEAD --stat -- tests/api tests/scripts` → `4 files changed,
  58 insertions(+)`, no deletions. The branch only adds to those directories, so
  no test was removed and no `xfail` marker dropped, and the base collects fewer
  than 1738 rather than more. A tree of 1,723 exists nowhere between the two.

The row now carries the run this round actually made on the committed tree —
`uv run pytest tests/eval tests/api tests/scripts -q` → `2825 passed, 3 skipped
in 2450.75s`, exit code read from the command and not from a pipeline. The
"before this card's fixes" half and the per-file breakdown are dropped rather
than re-derived: this round did not re-run them, and a number nobody in the
round ran does not belong in Results. The gate's own pytest leg, which collects
all of `tests/`, remains the run of record — that part of the row was never in
dispute.

**2 — the `tests/fixtures/` inventory row is a cell two concurrent cards
write.** Pull request #441 is opened against `work/evidence-renderer-salience`
because the queue serialises the renderer card ahead of this one. Both branches
are cut from `201849fc` and both add files under `tests/fixtures/`, so both
rewrite that row's file count and byte total, and GitHub reports the pull
request `CONFLICTING` / `DIRTY` (`gh pr view 441 --json
mergeable,mergeStateStatus`). Reproduced locally: `git merge-tree 201849fc
origin/work/evidence-renderer-salience HEAD` reports exactly one "changed in
both" path — `docs/artifacts.md` — with one conflict hunk (`grep -c '<<<<<<<'` →
1); every other file merges. The pull request body's claim that this branch
"shares no file with the renderer card" was false about that one line and has
been corrected there.

*(Superseded in "Review corrections, round 2" below, in that one parenthetical
only: the unanchored `grep` count was measurable only before this sentence was
committed, because the sentence itself carries the literal marker. The claim it
summarises — one `changed in both` path, one conflict hunk — is unchanged, and
is re-measured there with anchored patterns.)*

| Tree | `tests/fixtures/` |
| --- | --- |
| `201849fc`, the shared base | 23 files / 2,054,135 bytes |
| this branch (adds the frozen format-3 recording and its README) | 25 / 2,067,334 |
| `work/evidence-renderer-salience` (adds four memory-rendering goldens) | 27 / 2,085,311 |
| the two merged | **29 / 2,098,510** |

The merged value is computed, not inferred. Neither branch modifies a file the
other adds and neither touches an existing fixture — `git diff --name-status`
against the shared base shows only `A` lines on both sides — so the union of the
two listings is the merged inventory:

```sh
git ls-tree -r -l HEAD tests/fixtures > ours.txt
git ls-tree -r -l origin/work/evidence-renderer-salience tests/fixtures > theirs.txt
cat ours.txt theirs.txt \
  | awk '{size[$5]=$4} END {n=0; s=0; for (p in size) {n++; s+=size[p]}
          printf "%d files / %d bytes\n", n, s}'
# 29 files / 2098510 bytes
```

Resolving the conflict by keeping either side's number lands a tree whose own
gate is red, by the mechanism this card already leans on:
`scripts/verify_ml_evidence.py` compares each in-tree registry row's promised
file count and byte total against `git ls-files` of the pathspec
`_IN_TREE_INVENTORY` declares for it, and
`tests/scripts/test_verify_ml_evidence.py::test_every_counted_registry_row_matches_the_index`
asserts that row is `OK` at `_REPO_ROOT`, inside the `check.sh` pytest leg.
Demonstrated by perturbation on this tree: setting the row to the renderer
branch's `2,085,311 tracked bytes / 27 files` makes
`.venv/bin/python scripts/verify_ml_evidence.py` exit 1 with `note :
tests/fixtures/: docs/artifacts.md promises 27 files, the index tracks 25` and
the matching byte note under `[ FAIL ] in-tree family inventory`. Restoring the
row returns exit 0 and `every check passed`, with `docs/artifacts.md` back at
its committed bytes.

*(Superseded in "Review corrections, closeout round 1" below: the collision IS
resolved on this branch now, by merging the base branch's tip rather than
rebasing onto it. The reasoning below is kept as the state of the argument when
it was written, and the second bullet's objection — that a merge goes stale the
moment the base pushes again — is answered there rather than denied.)*

This branch does not resolve the collision, and that is a decision rather than
an omission:

* Rebasing onto `work/evidence-renderer-salience` would rewrite this branch's
  already-pushed commits, which the branch policy forbids.
* Merging that branch's tip in would carry another card's in-review code inside
  this pull request, and would go stale the moment its own fix round pushes —
  the same conflict, one tip later.

So the row is declared here as a shared, coordinator-recomputed cell. *(Also
superseded: this branch now sets it itself, to the same measured value.)*
Whoever retargets this pull request to `main` after the renderer card merges
sets it to **29 files / 2,098,510 bytes**, keeping both descriptive clauses —
this branch's
"one frozen format-3 recording and its README for the cross-tree policy check"
and the renderer's own — then re-runs
`.venv/bin/python scripts/verify_ml_evidence.py` and
`.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py` on the
merged tree. If either branch adds or drops a fixture before then, the number is
recomputed with the command above rather than copied from the table.

Coordination note, not a claim about either card: `tasks/post-merge-plan.md`
assigns the `audits/` row of `docs/artifacts.md` to the coordinator and names no
owner for the `tests/fixtures/` row, which two concurrent cards have now both
rewritten. The one-writer-per-file rule has a gap exactly the width of that row.

**Gates re-run on the corrected tree.** The card text is the only thing this
round moved, so these are the same suites on the same code as the original run.
None of the counts depends on that text, and it was checked rather than assumed:
`check.sh` ran twice, once before and once after these numbers were written into
the table, identical both times (`324.51s`, then `288.10s`), and
`uv run python scripts/validate_task_docs.py` plus
`tests/scripts/test_work_cards.py` and `tests/scripts/test_check_doc_facts.py`
ran once more on the exact bytes committed.

| Command | Result |
| --- | --- |
| `uv run pytest tests/eval tests/api tests/scripts -q` | exit 0 — `2825 passed, 3 skipped in 2450.75s` |
| `bash scripts/check.sh` | exit 0 — `7216 passed, 20 skipped, 3 xfailed`, mypy "no issues found in 471 source files", `390 historical phase tasks and 390 prompts; 43 work cards`, `All 390 prompts are in sync.`, frontend `19 files / 514 tests` and build |
| `bash scripts/verify_samples.sh` | exit 0 — "All 50 samples verified clean." twice |
| `build_sample_report.py --check` × 4 | all four exit 0, "consistent with its replays." each |
| `cd frontend && npm run e2e` | exit 0 — `13 passed (1.3m)`, 3 skipped |

### Review corrections, round 2 (2026-09-08)

One finding, from the documentation and evidence-claims lens, and it is the same
defect class round 1 reopened this card for: a number in Results that reproduces
on no committed tree. It is confined to one parenthetical, and this round moved
nothing else — the diff against `17e929f4` touches
`tasks/work/recorded-provenance-gaps.md` alone, no source file, no test, no
committed artifact.

**The conflict count counted the sentence that stated it.** Item 2 of "Review
corrections, round 1" reads, verbatim:

> Reproduced locally: `git merge-tree 201849fc
> origin/work/evidence-renderer-salience HEAD` reports exactly one "changed in
> both" path — `docs/artifacts.md` — with one conflict hunk (`grep -c '<<<<<<<'` →
> 1); every other file merges.

That parenthetical is superseded. `git merge-tree` emits a unified diff for every
path that differs between the two tips; this card is one of those paths; and the
sentence above spells the conflict marker out. So on the tree that ships the
sentence, the unanchored pattern matches twice — the real marker inside the
`docs/artifacts.md` hunk, and the card's own prose being added by this branch. At
`17e929f4`, the commit the finding was raised against, those are output lines 89
and 917; the second number moves with every edit to this card, which is the
point. The figure `1` was measurable only before the sentence was committed —
the same defect class round 1 reopened this card for. At `17e929f4`:

```sh
git merge-tree 201849fc origin/work/evidence-renderer-salience HEAD > mt.txt
grep -c '<<<<<<<' mt.txt            # 2 — the marker, and this card quoting it
grep -c '^+<<<<<<<' mt.txt          # 1 — added lines only: the marker
grep -c '^changed in both' mt.txt   # 1 — docs/artifacts.md, and nothing else
```

Both replacements are anchored, and they have to be. `^changed in both` can only
match `git merge-tree`'s own path headers, which sit at column 0, while every
line of file content it prints is a diff line carrying a `+`, `-` or space
prefix. `^+<<<<<<<` can only match an added line whose content *begins* with the
marker. Prose quoting either pattern cannot satisfy them: it appears in the
output as an added line, and the quoted token sits mid-line behind a backtick.
That is not an argument taken on trust — both anchored counts were re-measured
after this subsection was written, on the exact bytes this round commits, and
both are still `1` on a card that now spells the marker out seven times rather
than the one time that broke the count.

The claim the parenthetical summarised is unchanged, and was re-measured rather
than restated. The single `changed in both` entry is `docs/artifacts.md` — base
`33a39860`, `.our` `7c19f025` (`work/evidence-renderer-salience`, the first tip
argument), `.their` `a615e3fe` (this branch) — and its one hunk is the
`tests/fixtures/` inventory row, `2,085,311 tracked bytes / 27 files` on their
side against `2,067,334 / 25` on ours. *(The last clause is superseded in
"Review corrections, closeout round 1": read against the `.our` / `.their`
labels this sentence has just defined, it hands each side the other's figure.
`git merge-tree` prints `2,085,311 / 27` under `<<<<<<< .our` — the renderer
branch, the first tip argument — and `2,067,334 / 25` above `>>>>>>> .their`,
this branch. The blob mapping earlier in the sentence, the round-1 table and
the pull request body all assign them correctly.)* The round-1 sentence keeps its words and
now carries an explicit supersession marker naming this subsection. The
inventory table above it was re-run this round as well and is unchanged:
`git ls-tree -r -l <tree> tests/fixtures` summed with `awk` gives 23 files /
2,054,135 bytes at `201849fc`, 25 / 2,067,334 at this head, 27 / 2,085,311 on
the renderer branch, and the union `awk` prints `29 files / 2098510 bytes`.

Nothing else in Results needed changing: the lens reported that every other
number and command in it reproduced. The pull request body does not repeat the
conflict count, so it carries no copy of the defect; it is refreshed only to
match this head.

**Gates re-run on the corrected tree.** As in round 1, the card text is the only
thing that moved, so these run the same suites on the same code. That the counts
do not depend on the text was checked rather than assumed: `check.sh` ran once
before these numbers were written into the table and once after, on the bytes
this round commits, with identical counts both times — the duration is the only
figure that moved, and it is not recorded here for that reason. The three gates
that read the card — `validate_task_docs.py`,
`tests/scripts/test_work_cards.py` and `tests/scripts/test_check_doc_facts.py` —
ran last of all, inside that second `check.sh`.

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — `7216 passed, 20 skipped, 3 xfailed`, mypy "no issues found in 471 source files", `390 historical phase tasks and 390 prompts; 43 work cards`, `All 390 prompts are in sync.`, frontend `19 files / 514 tests` and build; identical on both runs |
| `uv run pytest tests/eval tests/api tests/scripts -q` | exit 0 — `2825 passed, 3 skipped, 1 warning in 1003.39s` |
| `bash scripts/verify_samples.sh` | exit 0 — "All 50 samples verified clean." twice |
| `build_sample_report.py --check` × 4 | all four exit 0, "consistent with its replays." each |
| `cd frontend && npm run e2e` | exit 0 — `13 passed (1.1m)`, 3 skipped |


### Review corrections, closeout round 1 (2026-09-08)

One blocking finding, fourteen non-blocking ones across three lenses, and the
pull request's `CONFLICTING` state against its base. Unlike rounds 1 and 2 this
round moved source: four findings — the blocking one and three of the
non-blocking ones — were defects in the code, not in the prose describing it,
and one more was a claim about the code that turned out to be false.

**1 — the blocking finding: Decision 1 claimed a complaint closed that the
field still exhibited.** The Decision said the new clock field "answers the
earlier review's C4-5 complaint that version fields should reject non-version
input". C4-5 reads: "`temporal_observation_version` accepts a JSON boolean and
coerces it to 1". Measured at `db6ffb9e`,
`GameProvenance.model_validate({'temporal_observation_version': True})` returned
`1`, and the committed `replays/samples/4p1i` report read through
`TournamentEvalReport` with its first game's stamp set to `true` loaded as clock
v1 — the exact relabelling the field's own docstring forbids ("a recording made
before the stamp existed is legacy, not v1, and reading one does not relabel
it"). The recorded row it says it mirrors did reject it, through a validator
this card had not mirrored.

Resolved by option (a) of the finding: mirror the enforcement rather than
weaken the claim. `orchestrator/replay.py`'s three-line rule is lifted out of
`ReplayEntry` into `require_integer_temporal_version`, so the recording and
everything that reads it back run one function object instead of copies that
can drift. Its five boundaries:

| Site | Module | Why it is a boundary and not a repeat |
| --- | --- | --- |
| `ReplayEntry` | `orchestrator/replay.py` | The recorded row; the rule's original home, now delegating |
| `GameProvenance` | `eval/report_schema.py` | The recorded identity, and the type `ReportProvenanceGroup` inherits |
| `GameReport` | `eval/report_schema.py` | The model a committed report's JSON is actually read through — `recorded_provenance()` only ever sees an already-validated value |
| `ReplayMetadataView`, `ReportProvenanceGroupView` | `api/schemas.py` | Served DTOs; they shadow the rule rather than import it, because that module's contract is that spectator DTOs do not couple to orchestrator symbols |
| `_GameReportEvalView` | `api/routes/eval.py` | Validated from a dump, so it inherits no validator from the model it mirrors |

What is enforced, measured on the committed tree with each model loaded
directly: `True`, `False`, `2.0`, `"2"` and `"v2"` raise `ValidationError`;
`None`, `1` and `2` load; `3` still raises. Only two of those were reachable
gaps before — `Literal[1, 2]` already rejected `False` (`== 0`), `"2"` and
`"v2"`, and accepted `True` and `2.0` — and the perturbation below shows
exactly those two.

*Planted proofs.* 33 new cases across three modules. Reverting
`require_integer_temporal_version` to a pass-through (the pre-fix behaviour)
and running the affected selection gives `7 failed, 10 passed`, failing
`test_provenance_refuses_a_clock_version_that_is_not_an_integer[True]` and
`[2.0]`, `test_game_report_refuses_a_clock_version_that_is_not_an_integer[True]`
and `[2.0]`, `test_a_committed_report_whose_clock_is_a_json_boolean_is_refused`,
and `test_the_redaction_view_refuses_a_non_integer_clock[True]` and `[2.0]`.
Reverting the DTO copy in `api/schemas.py` the same way gives `7 failed, 9
passed` in `tests/api/test_schemas.py`, including every case of
`test_the_dto_clock_guard_agrees_with_the_recorded_one`, which compares the
copy against the original on the same inputs so the shadow cannot drift.

*No committed report is affected, and that is measured rather than assumed.*
`grep -c temporal_observation_version <dir>/tournament-eval-report.json` is `0`
for all four committed sets, so none of them can carry a non-integer clock; all
four `--check` runs and both `verify_samples.sh` passes stay green (table
below).

**2 — the pull request was `CONFLICTING`; it is merged now, not deferred.**
Round 1 declared the shared `tests/fixtures/` inventory row a cell for whoever
retargets. That deferral is superseded: `work/evidence-renderer-salience` at
`bd6f05dc` is MERGED into this branch (never rebased — this branch's commits
are pushed). `docs/artifacts.md` was the only conflicting path. Both
descriptive clauses are kept — the renderer branch changed only the number, not
the row's text — and the value is recomputed from `git ls-files` with the merge
staged rather than copied from round 1's table: **29 files / 2,098,510 bytes**,
which is what round 1 predicted. The `audits/` row carries the base branch's
restamped `14,852,039 bytes / 202 files` and re-measures correct on the merged
tree.

Round 1's objection to merging — that it goes stale the moment the base pushes
again — is answered, not denied: the base tip was re-fetched at the start of
this round and again immediately before the merge, both `bd6f05dc`, and the sha
is named in the merge commit so a later base tip is a visible re-merge rather
than a silent drift. Verified on the merged tree:
`.venv/bin/python scripts/verify_ml_evidence.py` exit 0, `checks: 60 | OK 48 |
FAIL 0 | ABSENT 7 | INFO 5`, "every check passed";
`tests/scripts/test_verify_ml_evidence.py` 80 passed.

**3 — the frozen held-out set.** No restamp is owed by this card.
Intersecting `experiments.held_out_prefixes.GENERATOR_SOURCES` with this card's
own commits (`git diff --name-only 201849fc db6ffb9e`) gives `[]`, and with this
round's source changes gives `[]`. The base branch does touch two of them
(`agents/memory/store.py`, `experiments/held_out_prefixes.py`) and had already
restamped for both of its commits; that manifest comes through the merge
byte-identical (`git diff origin/work/evidence-renderer-salience --
audits/deduction-candidate/held-out/manifest.json` is empty), and
`tests/experiments/test_held_out_prefixes.py` is green (28 passed). No band
prefix was printed or opened.

**4 — three non-blocking findings were code.** Each is fixed with its own
perturbation, restored after measuring:

* **The served surface never named the clock.** `PublicResults.tsx`'s identity
  card rendered factory, mechanisms, both policy methods and "Rule settings",
  and dropped `temporal_observation_version` — so the "This set mixes recorded
  behavior configurations" banner could fire above two cards that read
  character-for-character alike, which is the opposite of what Record impact
  asks for. The card now ends with "Observation clock: v2." (or "not
  recorded."). Perturbation: removing that line fails the new
  `PublicResults.test.tsx` case (`1 failed | 3 passed`), which renders two
  groups differing only by clock and asserts both versions appear.
* **`check_report`'s committed-shape guard had drifted from the exclusion set
  it partners.** The clock key had been added to `_historical_report_exclusions`
  and not to the five-key literal in `check_report`. Both now read one
  `_RECORDED_IDENTITY_GAME_KEYS` tuple, so the guard cannot drift again by
  construction — it no longer has its own list. What a test can still catch is
  the *exclusions* half drifting from the tuple, and
  `test_the_committed_shape_guard_names_every_projected_identity_key` pins that
  (it also asserts every name is a real field of the model the guard reads, so a
  typo cannot silently never match). Perturbation: dropping the clock key from
  the tuple fails 12 tests in `tests/scripts/test_build_sample_report.py`,
  including all four committed `--check` sets — the tuple is load-bearing in
  both directions. The original drift could only ever have produced a loud false
  STALE, so nothing unsafe shipped.
* **The walker's parity comment claimed something it did not establish.** The
  inline comment said the v3 mismatch is handled "exactly as ... every other
  check", while this one alone leaves state behind: `before_tick` asks every
  living agent to decide before it raises, so the reconstruction is stepped for
  a tick it disagrees with. The comment now names the mechanism that makes that
  harmless, and the mechanism is pinned rather than argued — see finding 5.

**5 — one non-blocking finding is refuted, with the refutation pinned.** The
scope lens held that a profile whose `on_violation` returns would leave the walk
running on a half-stepped `PolicyReconstruction`, calling `after_tick` at
`eval/replay_walk.py` on a reconstruction whose agents had already stepped. That
cannot happen, and not merely because no shipping profile does it: `_violate` is
declared `NoReturn` and raises `RuntimeError` naming the profile if a hook
returns, for every violation kind — and `on_violation` is itself typed
`Callable[[WalkViolation], NoReturn]`, so a returning hook does not type-check
either. A guard was written for this and then deleted rather than shipped as
unreachable code. The new
`test_a_mismatch_cannot_be_swallowed_onto_a_half_stepped_reconstruction` casts a
returning hook past the type checker, walks the frozen fixture under the planted
policy defect, and asserts the `RuntimeError` — with the hook having seen the
violation exactly once, at the diverging tick. Perturbation: making `_violate`
return instead of raising fails that test.

**6 — the remaining non-blocking findings, and what happened to each.**

* *`PolicyReconstruction.__init__` raises bare `ValueError`s outside the new
  routing.* Correct, and correct as it stands: both are CONSTRUCTION
  preconditions — this object cannot be built at all — not checks over a
  recording, which is what a profile's policy decides. `eval/replay_walk.py`
  reaches neither (it gates on `format_version == 3` and pins the service to
  version 2 before constructing). The source now says so where the raise is,
  rather than leaving the reader to infer it from NC3-1's contract.
* *Two touched files were named nowhere in the card.* Fixed by the follow-through
  list below, which now names every file outside `## Expected scope`.
* *The merged inventory figure was valid only against the renderer branch's
  current tip.* No longer a forward-looking figure: it is this tree's measured
  value, recomputed at merge time.
* *The `.our` / `.their` sentence in round 2 inverted the labels it had just
  defined.* Corrected in place with a supersession marker; the correct
  assignment is `2,085,311 / 27` on `.our` (the renderer branch, the first tip
  argument) and `2,067,334 / 25` on `.their` (this branch).
* *The NC6-1 reproduction command was not runnable as written.*
  `experiments/investigation_evaluation.py` declares `--output-dir` as
  `required=True`, so the command as spelled exited with an argparse error. The
  line now carries the flag. Its figures stay the dated pre-fix measurement at
  `201849fc`; the post-fix state was re-measured this round on the merged tree,
  two runs into fresh directories: `artifact hash keys: 245 differing: 0 by
  basename: {}`, against `245 differing: 35` before. The committed
  `audits/investigation-candidate/2026-09-06-normal-policies.json` still carries
  245 hashes of which 35 are `view.json`, which is the "not retro-certified"
  limitation holding.
* *Results opened "in five commits" while the branch carried eight.* The
  sentence now says which five it means and points at `--first-parent` for the
  branch's own count, which this round takes to eleven.
* *Commit `583eba5d`'s `Card:` line lacks the blank line before it.* Half of
  this reproduces and half does not, and the difference matters. Measured over
  the ten first-parent commits this card owns: `583eba5d` is the only one whose
  `Card:` line sits directly under the last prose line — the other nine have the
  blank line. But `git interpret-trailers --parse` returns `Co-Authored-By`
  ALONE on all ten, `583eba5d` included, so the claim that the others "parse
  both trailers" does not reproduce here. The reason is the house commit format
  itself: it puts a blank line between `Card:` and the final
  `Co-Authored-By:` line, which makes `Card:` its own paragraph, and git reads
  only the last block as the trailer block. So the malformed commit is real and
  the diagnosis attached to it was not; the defect is cosmetic in both cases.
  It stays as it is either way — the branch policy forbids amending a pushed
  commit, and rewriting nine descendants over one blank line is the worse
  trade.
* *Codex reviewed `e26045b`, two commits behind the head that was reviewed.*
  Still true, and still harmless — see "Codex review" below.

**Codex review.** Re-polled at this round's start:
`gh api repos/dkdan10/AiLibi/pulls/441/comments` → `0`,
`.../pulls/441/reviews` → `0`, `.../issues/441/comments` → one comment, the
`chatgpt-codex-connector` summary ("Code Review | Completed | `e26045b` | PR
opened"), with no findings body. There are therefore no Codex findings to
address, valid or invalid: nothing to reproduce, confirm or refute. The review
ran against `e26045b`, and every commit between it and `db6ffb9e` was
documentation-only, so its clean result did cover the source as it then stood —
but it has not seen this round's source, and Codex re-triggers only on PR-open,
draft-ready, or an explicit review comment, none of which this round performs.

**Out-of-scope follow-through, each named with its reason.** `## Expected
scope` admits `eval/`, `api/schemas.py`, `api/replay_loader.py`,
`api/public_results.py`, `scripts/build_sample_report.py`, the two experiment
harnesses, their tests, and generated frontend types. These files are outside
it and are kept:

* `orchestrator/replay.py` — the integer rule's home. Lifting it out of
  `ReplayEntry` into a shared function is what makes "the report mirrors the
  recorded field" enforceable rather than a comment; a copy in `eval/` would be
  the drift the finding objected to.
* `api/routes/eval.py` — the route declares
  `model_config = ConfigDict(frozen=True, extra="forbid")` precisely so a new
  `GameReport` field trips the redaction re-validation loudly, so the mirrored
  field is required, not optional. Deleting it turns `tests/api` red (the
  redaction round-trip raises). The integer check follows the field.
* `scripts/gen_frontend_types.py` — one entry in the generator's optional-field
  list; `generate_prompts --check` and `tsc:check` are green only with it, and
  it is what produces the `frontend/src/types/api.ts` the scope line does admit.
* `frontend/src/components/PublicResults.tsx` and its test — the served card
  that names the clock, added this round for the finding above. The DTO change
  had already forced the test file (`TS2741`: the two
  `ReportProvenanceGroupView` literals were incomplete once the DTO gained a
  required additive field).
* `orchestrator/policy_reconstruction.py` — `PolicyReconstructionMismatch` is
  the exception NC3-1 asks for; it has to live with the class that raises it.
  This round adds a comment there and no behaviour.
* `tasks/work/evidence-renderer-salience.md`, `agents/memory/`,
  `tests/agents/`, `tests/fixtures/memory_rendering/`,
  `experiments/held_out_prefixes.py` and
  `audits/deduction-candidate/held-out/manifest.json` — the base branch's own
  card, arriving through the merge. Not this card's changes; they leave the
  diff when the pull request is retargeted to `main` after the base merges.

**Gates re-run on this round's tree.** `check.sh` ran twice — once on the
source changes before this subsection was written, once on the exact bytes this
round commits — with identical counts; duration is the only figure that moved,
which is why it is not recorded. Every exit code was read from the command, not
from a pipeline.

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — `7265 passed, 20 skipped, 3 xfailed`, mypy "no issues found in 471 source files", `390 historical phase tasks and 390 prompts; 43 work cards`, `All 390 prompts are in sync.`, frontend `19 files / 515 tests` and build |
| `bash scripts/verify_samples.sh` | exit 0 — "All 50 samples verified clean." twice |
| `build_sample_report.py --check` × 4 | all four exit 0, "consistent with its replays." each; `0` committed clock stamps in each set's report |
| `cd frontend && npm run e2e` | exit 0 — `13 passed (2.7m)`, 3 skipped |
| `.venv/bin/python scripts/verify_ml_evidence.py` | exit 0 — `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`, "every check passed" |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py` | exit 0 — 80 passed |
| `.venv/bin/python -m pytest tests/experiments/test_held_out_prefixes.py` | exit 0 — 28 passed |
| `.venv/bin/python -m pytest tests/orchestrator/ --collect-only -q` | exit 0 — 583 tests collected |
