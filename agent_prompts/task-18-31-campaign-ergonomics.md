# Agent Prompt — 18.31 Campaign ergonomics: resume, persistence, loadable freezes, generated tables

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.31 — Campaign ergonomics: resume, persistence, loadable freezes, generated tables, anchored to training/reports/report-impostor-campaign.md §11 (the five demonstrated defects + costs), F1/F9/F12/F14 + §12 Errata items 1 and 10 (the mis-stamp and log-gap lessons); training/realpath.py:702, 873 (`_verify_stamps`, `run_realpath_rerank`); training/coevo/hall_of_fame.py:242, 397 (`create`, `add_member`); training/coevo/driver.py (the freeze/persistence sites); scripts/run_tournament.py:560 (`_load_candidate_policy` — the consuming entry point, NOT edited). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-campaign-ergonomics`
**Depends on:** 18.24
**Section refs:** training/reports/report-impostor-campaign.md §11 (the five demonstrated defects + costs), F1/F9/F12/F14 + §12 Errata items 1 and 10 (the mis-stamp and log-gap lessons); training/realpath.py:702, 873 (`_verify_stamps`, `run_realpath_rerank`); training/coevo/hall_of_fame.py:242, 397 (`create`, `add_member`); training/coevo/driver.py (the freeze/persistence sites); scripts/run_tournament.py:560 (`_load_candidate_policy` — the consuming entry point, NOT edited)
**Complexity:** Integration

The routed machinery task the 18.24 campaign's operational evidence demands (the
integration-risk discipline working as designed: mid-campaign defects became a routed
contract, never silent patches). Six fixes, each small, each priced by incurred cost:
(1) RESUME for `run_realpath_rerank` — skip a (candidate, seed) element whose replay
already exists AND whose read-back stamp `weights_sha256` equals the candidate's genome
digest AND whose recording reaches GAME_OVER with the byte-completeness fence green; the
skip predicate is CONJUNCTIVE and any miss re-records (all three checks exist in the
tree — they are simply not wired to a resume path). (2) Per-generation champion-genome
persistence in the driver — each generation's champion persisted beside the campaign
rows (or the ES champion trace exposed), ADDITIVE AND DIGEST-INERT: the row digest
covers row JSON lines only and must not move; the work-dir no-clobber discipline extends
to the new artifacts. (3) Tranche/invocation-keyed pre-screen records — a native writer
for pre-screen quote records (keyed by tranche/invocation, never in-place overwrite),
plus a native append-only leg log written by the leg library itself (the blocker-4
ordering evidence stops depending on operator shell redirection — the 18.24 session-5
gap is the demonstration). (4) Natively loadable freezes — `HallOfFame.add_member` and
every driver freeze path write the four-file loadable artifact (`weights.json`, sha
sidecar, five-field `stamp.json`, provenance `config.json`), with `encoder_version`/
`hidden` dispatched from the side config per family (the §12 Errata item-1 mis-stamp is
the failure this kills), loadable through `_load_candidate_policy` end-to-end. (5) A
deterministic table generator rendering the campaign-report table families (§3 row
tables, §4 leg tables, the §4.0 stability table) from committed artifacts. (6) The free
protocol precondition documented at the seam: the stability-table computation runs from
the generator against any two-tranche ranking set (what F12 tells every future campaign
to do after its first retest).

**Files in scope:**
- training/realpath.py (the resume path + the native pre-screen/leg-log writers)
- training/coevo/driver.py (the champion-persistence artifact ONLY)
- training/coevo/hall_of_fame.py (the loadable-freeze writer)
- scripts/generate_campaign_tables.py (new — the table/stability generator CLI)
- tests/training/test_realpath.py + tests/training/test_coevo_driver.py + tests/training/test_hall_of_fame.py + tests/scripts/test_generate_campaign_tables.py (the fixes' pins)

**Files NOT in scope:**
- training/coevo/factory.py + rollout.py (untouched)
- training/artifacts/coevo/ (the 18.24 record is frozen history — the generator READS it as its test fixture, never rewrites it)
- scripts/run_tournament.py (the consuming entry point is the invariant this task satisfies, never the thing it edits)
- training/reports/ (18.24's report is a merged record; its §12 Errata is the correction channel)

**Definition of done:**
- [ ] An interrupted re-rank resumes: a leg with pre-existing (candidate, seed) replays skips exactly the verified-complete elements and re-records everything else, refusing to skip on ANY verification miss (stamp-sha mismatch, non-GAME_OVER, completeness-fence fail) — fixture-pinned in both directions; the driver persists every generation's champion digest-inertly (the 18.21 double-run row-digest pin passes unchanged) under the standing no-clobber discipline; pre-screen records and leg logs write natively, tranche/invocation-keyed, append-only.
- [ ] Every hall/driver freeze writes the four-file artifact with family-correct `encoder_version`/`hidden` and loads through `_load_candidate_policy` end-to-end in a test (both families: a utility-genome and a v3 masked-MLP fixture); the table generator reproduces the committed `measurement-stability.json` numbers from the committed ranking artifacts and renders the row/leg table families deterministically (same bytes twice).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The resume rule is conjunctive on purpose — a skip on any weaker predicate silently
converts a corrupted or foreign replay into "already done"; when in doubt, re-record (the
cost asymmetry is ~8 minutes vs a poisoned evidence table). Two dispositions the rule
must state: a `TICK_BUDGET_REACHED` replay has no GAME_OVER row by design and is
therefore NEVER skippable — it re-records, deliberately; and the completeness fence is
dir-scoped (`compute_kill_craft_report`), so per-(candidate, seed) verification is
reached via per-seed staging or a roster-first write order — sanctioned here — never by
editing `eval/kill_craft.py` (out of scope). The driver persistence writes
beside the rows file (e.g. a `gen-champions/` dir under the work dir), inheriting the
work-dir no-clobber preflight; 18.21's double-run digest test is the guard that row
emission never moved. The freeze writer needs `hidden` and a stamp-grade run label that
`CoevoSideConfig`/`CoevoCampaignConfig` do not yet carry — additive, default-valued,
digest-inert config-metadata fields are SANCTIONED for exactly this (the frozen-machinery
rule bends for declared additive metadata, never for behavior); take
`encoder_version`/`hidden` from config — never re-derive from genome length (length
collisions between future families are exactly the ambiguity stamps exist to remove). The stability
generator's numbers must reproduce the committed `measurement-stability.json` from the
committed `realpath*/` ranking files — that reproduction IS its acceptance fixture, free
and already in-tree.

## Public types this task introduces
- `training.coevo.hall_of_fame.write_loadable_artifact`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

`training/coevo/driver.py` and `hall_of_fame.py` are proven-frozen machinery with
determinism digests and 29/22-test suites — every existing test must pass unchanged, and
the persistence/freeze additions must be provably inert to rows, digests, and existing
artifact bytes (the 18.24 record under `training/artifacts/coevo/` is a frozen fixture:
`git status` clean over it after the full suite is part of the review bar). The resume
path touches the same library 18.25's legs will run within days — the conjunctive
predicate's false-positive direction (skipping something unverified) is the only truly
dangerous failure mode; bias every ambiguity toward re-recording.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.conviction.serving"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`
- `uv run python -c "import training.anchor_study"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-campaign-ergonomics` with a title like `task 18.31: campaign ergonomics: resume, persistence, loadable freezes, generated tables`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/reports/report-impostor-campaign.md §11 (the five demonstrated defects + costs), F1/F9/F12/F14 + §12 Errata items 1 and 10 (the mis-stamp and log-gap lessons); training/realpath.py:702, 873 (`_verify_stamps`, `run_realpath_rerank`); training/coevo/hall_of_fame.py:242, 397 (`create`, `add_member`); training/coevo/driver.py (the freeze/persistence sites); scripts/run_tournament.py:560 (`_load_candidate_policy` — the consuming entry point, NOT edited)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
