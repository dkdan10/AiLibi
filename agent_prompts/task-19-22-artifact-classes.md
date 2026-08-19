# Agent Prompt — 19.22 Artifact classes + the coevo prune + the fast-clone path

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.22 — Artifact classes + the coevo prune + the fast-clone path, anchored to audits/audit-phase-19-triage.md §7 item 23 [C; VERIFIED §8 row 11] + locked decision 5; the verified consumer set (planning session): exactly two test files read coevo bytes — tests/scripts/test_generate_campaign_tables.py (pins `measurement-stability.json` key-for-key) and tests/training/test_finalist_eval_pins.py (pins weights under `intermediates/`, `runnerups/`, run-01/run-c1/run-c2 generation dirs, and `realpath-crew/controls/…`); the tree: training/artifacts/coevo = ~109MB / 1,473 files, the realpath* subtrees ~104MB / 403 files; audits/audit-phase-18-close.md §6.3 C4 (the coevo namespace rules — the prune must not disturb `DEFAULT_RANKING_ROOTS` semantics). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-artifact-classes`
**Depends on:** 19.13, 19.19, 19.21 (the raw-slate ruling precedes the ONE immutable evidence commit this task creates)
**Section refs:** audits/audit-phase-19-triage.md §7 item 23 [C; VERIFIED §8 row 11] + locked decision 5; the verified consumer set (planning session): exactly two test files read coevo bytes — tests/scripts/test_generate_campaign_tables.py (pins `measurement-stability.json` key-for-key) and tests/training/test_finalist_eval_pins.py (pins weights under `intermediates/`, `runnerups/`, run-01/run-c1/run-c2 generation dirs, and `realpath-crew/controls/…`); the tree: training/artifacts/coevo = ~109MB / 1,473 files, the realpath* subtrees ~104MB / 403 files; audits/audit-phase-18-close.md §6.3 C4 (the coevo namespace rules — the prune must not disturb `DEFAULT_RANKING_ROOTS` semantics)
**Complexity:** Medium

Implement locked decision 5. `docs/artifacts.md` defines the four artifact classes:
(a) small canonical fixtures in git; (b) manifests/hashes/summaries in git; (c) large
immutable evidence in the evidence branch; (d) disposable regenerated views. Then the
prune: FIRST enumerate every byte the two consumer test files pin (they are the
authority — the enumeration is the contract's first step and its output is committed
into the manifest); everything else under `training/artifacts/coevo/` moves to the
orphan evidence branch `evidence/phase-18-coevo` — as ONE immutable commit that also
carries the recovered finalist raw slate. 19.21 RESOLVED ON THE RECOVERY PATH (ruling
2026-08-15): the slate exists and the owner pushed `evidence/raw-slate-staging` at
`c27ab7b5f5e7e10bfab5c6dc752362b137862cac`, carrying 1,569 files / 298.157 MiB under
`finalist-eval-raw/` plus one ref-root `README.md`. Consume it FROM THAT SHA, not from
the branch name, and re-verify every file against `training/reports/_finalist_eval_raw/
MANIFEST.md` before folding (the coordination session confirmed the manifest's 1,569
rows match the ref's path set exactly, with a sampled digest check clean); retire the
staging ref after the fold. TWO CARRY-FORWARD CAUTIONS, both verified against the bytes:
the ref-root `README.md` is the ONE staged file no committed sha covers (MANIFEST.md §2
declares this openly — give it a digest in the evidence commit's own manifest), and that
same README carries two figures that DISAGREE with the bytes it describes — "297.8 MiB"
(actual 298.157 → 298.2, which the in-tree MANIFEST states correctly) and a
"→ 2026-08-01" recording window (the last timestamp anywhere in the slate is
2026-07-31T18:00:06Z). MANIFEST.md is the authority; do not copy the README's two
numbers forward. The evidence commit carries a per-file
sha-256 manifest committed in-tree. The branch is PUSHED, its tip commit sha is PINNED
in the in-tree manifest, and `scripts/fetch_evidence.sh` fetches BY THAT SHA (never by
branch name — the pin is the immutability guarantee), registering the class-(c) rows in
`docs/artifacts.md` including 19.21's outcome. Pinned bytes,
`measurement-stability.json`, and the provenance records stay in-tree. `replays/` does
not move (locked decision 5). README and the reading guide document
`git clone --filter=blob:none` as the fast path, with the honest caveat that
full-history clones stay heavy absent a future deliberate rewrite.

**Files in scope:**
- training/artifacts/coevo/; (the prune — unpinned bytes removed from the working tree)
- docs/artifacts.md (new)
- README.md; (the fast-clone note)
- docs/reading-guide.md; (the same note where the guide describes cloning)
- scripts/fetch_evidence.sh (new — a small helper that checks out the evidence branch's bytes back into place)

**Files NOT in scope:**
- replays/ (stays whole — locked decision 5)
- tests/scripts/test_generate_campaign_tables.py + tests/training/test_finalist_eval_pins.py (their pinned bytes must remain in-tree so the tests are untouched)
- .git history (no rewrite)

**Definition of done:**
- [ ] The consumer enumeration is committed (the manifest marks each retained path with its pinning test); the full suite passes with NO test edits — the prune provably removed only unpinned bytes.
- [ ] Moved weight/sidecar PAIRS stay paired in the evidence branch and the in-tree manifest carries their hashes — verification-after-fetch must work (19.23 depends on it); a weight whose sidecar went one way while it went the other is a manifest error.
- [ ] The evidence branch is pushed as ONE immutable commit (coevo bytes + the recovered slate, folded from the `evidence/raw-slate-staging` sha above and re-verified against the committed manifest before the fold), its TIP SHA is pinned in the in-tree manifest, its bytes match the manifest sha-for-sha, EVERY file it carries has a digest (including the ref-root README the staging manifest leaves uncovered), and `scripts/fetch_evidence.sh` restores them by that pinned sha; the staging ref is retired and the working-tree size reduction is quoted in the PR.
- [ ] The fast-clone path is documented with the honest history caveat.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Build the retained-path allowlist by parsing the two test files' path literals plus
`training/artifacts/coevo/PATHS.md`/provenance conventions, then verify by running the
suite against a scratch tree with everything else removed BEFORE committing the prune.
The evidence branch is orphan (`git checkout --orphan evidence/phase-18-coevo`) carrying
only the moved bytes + a README naming the manifest commit.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.realpath_schema"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-19-artifact-classes` with a title like `task 19.22: artifact classes + the coevo prune + the fast-clone path`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 23 [C; VERIFIED §8 row 11] + locked decision 5; the verified consumer set (planning session): exactly two test files read coevo bytes — tests/scripts/test_generate_campaign_tables.py (pins `measurement-stability.json` key-for-key) and tests/training/test_finalist_eval_pins.py (pins weights under `intermediates/`, `runnerups/`, run-01/run-c1/run-c2 generation dirs, and `realpath-crew/controls/…`); the tree: training/artifacts/coevo = ~109MB / 1,473 files, the realpath* subtrees ~104MB / 403 files; audits/audit-phase-18-close.md §6.3 C4 (the coevo namespace rules — the prune must not disturb `DEFAULT_RANKING_ROOTS` semantics)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
