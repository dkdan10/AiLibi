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

Implemented on `work/recorded-provenance-gaps` in five commits off `201849fc`:
a frozen format-3 fixture, the observation-clock provenance field, the
`view.json` timestamp exclusion, the meeting-keyed memory guard, and the v3
policy re-decision as a profile option.

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
* **NC6-1.** Two runs of `.venv/bin/python -m experiments.investigation_evaluation`
  into fresh directories: `artifact hash keys: 245 differing: 35 / by basename:
  {'view.json': 35} / everything else identical: True`, with `created_at`
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

1. **The field is typed `TemporalObservationVersion` (`Literal[1, 2] | None`),
   not the card's literal `int | None`.** It is a narrowing of that type, to the
   two versions `observation/version.py` can resolve; a report claiming a clock
   this build cannot reconstruct under is a corrupt claim, and the recorded
   field it mirrors (`ReplayEntry.temporal_observation_version`) carries the same
   alias. This matches the house style for sibling version fields
   (`ExperimentConfigView.format_version`) and answers the earlier review's C4-5
   complaint that version fields should reject non-version input.
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

No committed report or recording changed: `git diff --stat 201849fc HEAD` touches
nothing under `replays/` or `audits/`. The only `docs/artifacts.md` edit is the
`tests/fixtures/` inventory row the new fixture moves (23 files / 2,054,135 bytes
→ 25 / 2,067,334, recomputed from `git ls-files tests/fixtures` with the change
staged); the coordinator-owned `audits/` row is untouched, because no `audits/`
byte moves. The frozen held-out manifest needs no restamp: none of the files this
card edits appears in `experiments/held_out_prefixes.GENERATOR_SOURCES`, and
`tests/experiments/test_held_out_prefixes.py` is green (28 passed).

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

This branch does not resolve the collision, and that is a decision rather than
an omission:

* Rebasing onto `work/evidence-renderer-salience` would rewrite this branch's
  already-pushed commits, which the branch policy forbids.
* Merging that branch's tip in would carry another card's in-review code inside
  this pull request, and would go stale the moment its own fix round pushes —
  the same conflict, one tip later.

So the row is declared here as a shared, coordinator-recomputed cell. Whoever
retargets this pull request to `main` after the renderer card merges sets it to
**29 files / 2,098,510 bytes**, keeping both descriptive clauses — this branch's
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
