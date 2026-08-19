# Agent Prompt — 19.8 Corpus truth disclosures

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.8 — Corpus truth disclosures, anchored to audits/audit-phase-19-triage.md §7 item 9 [S-Claude/S-Codex; §8 rows 12, 13 VERIFIED; the roll-call coverage split is S-Codex and NOT independently re-run — verify-then-fix]; agents/tactical/impostor_policy.py:39-40 ("after the kill … the impostor must not file a report" — the structural reporter-innocence prior); replays/ml_corpus/README.md:228-236 (the no-husk doctrine the committed husks violate), :91-102 (the by-game split); the verified counts: 21.3% engine-rejected 9p kill submissions (48/225 samples), ~5% husk turns (53/971 samples; 137/2,726 corpus), 19/798 crew-witnessed kills with zero non-victim co-present at the decision frame. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-corpus-disclosures`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 9 [S-Claude/S-Codex; §8 rows 12, 13 VERIFIED; the roll-call coverage split is S-Codex and NOT independently re-run — verify-then-fix]; agents/tactical/impostor_policy.py:39-40 ("after the kill … the impostor must not file a report" — the structural reporter-innocence prior); replays/ml_corpus/README.md:228-236 (the no-husk doctrine the committed husks violate), :91-102 (the by-game split); the verified counts: 21.3% engine-rejected 9p kill submissions (48/225 samples), ~5% husk turns (53/971 samples; 137/2,726 corpus), 19/798 crew-witnessed kills with zero non-victim co-present at the decision frame
**Complexity:** Medium

The corpus is honest about what it contains and silent about what that implies. Add a
"capability disclosures" section to the corpus README and a short mirror note in each
samples MANIFEST, recording as measured facts: the absolute reporter-innocence prior
(structural — the scripted impostor cannot report or call meetings, so 100% of training
examples carry it; any learned impostor that self-reports invalidates the crew's learned
prior); the engine-rejected kill-submission rate; the player-visible
`[invalid accusation target …]` husk rate against the README's own no-husk doctrine;
zombie-vent re-litigation; skip-template repetition; wait-streak/ping-pong mover theater;
model-originated fourth-wall statements and machinery quotation; the role-correlated
public response shape (crew ~99.6–99.7% roll-call coverage vs impostor ~45.5–46.5% —
verify-then-fix: recompute the split from committed bytes before quoting it); and the
too-clean evidence economy. Disclosures record capability limitations — zero gameplay
tuning, zero byte changes outside the two documentation surfaces.

**Files in scope:**
- replays/ml_corpus/README.md
- replays/samples/4p1i/MANIFEST.md
- replays/samples/9p2i/MANIFEST.md

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (the prior is disclosed, not changed)
- replays/**/replay-seed-*.jsonl + tournament-eval-report.json (no bytes move)

**Definition of done:**
- [ ] Verify-then-fix first: every number written is recomputed from committed bytes this session with the stdlib command recorded in the PR (numerator/denominator quoted); the roll-call split in particular is re-derived, not copied from the audit.
- [ ] The disclosures section covers every phenomenon listed above with its committed-bytes citation, and explicitly reconciles the husk rate with the README's no-husk doctrine (a recorded deviation, not a silent contradiction).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The audits' parses are the recipe (turn counts, ballot counts, husk substrings, roll-call
response fields); reimplement each as a ~20-line stdlib script over the JSONL and paste
the outputs into the PR. Where your recount differs from an audit's figure, the recount
wins and the delta is noted — generated facts beat copied facts.

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
Open a PR from branch `phase-19-corpus-disclosures` with a title like `task 19.8: corpus truth disclosures`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 9 [S-Claude/S-Codex; §8 rows 12, 13 VERIFIED; the roll-call coverage split is S-Codex and NOT independently re-run — verify-then-fix]; agents/tactical/impostor_policy.py:39-40 ("after the kill … the impostor must not file a report" — the structural reporter-innocence prior); replays/ml_corpus/README.md:228-236 (the no-husk doctrine the committed husks violate), :91-102 (the by-game split); the verified counts: 21.3% engine-rejected 9p kill submissions (48/225 samples), ~5% husk turns (53/971 samples; 137/2,726 corpus), 19/798 crew-witnessed kills with zero non-victim co-present at the decision frame), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
