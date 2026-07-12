# Agent Prompt — 16.15 The elicitation batch: citations, roll-call, provenance surface, the vent tail, the self-accusation fix

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.15 — The elicitation batch: citations, roll-call, provenance surface, the vent tail, the self-accusation fix, anchored to audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2a/J3 (the surface design); audits/audit-phase-15-close.md §11 (the vent-tail cells: samples 53/73 mentioned; corpus 188/255) + §5.2 of the wave-0 close (the self-accusation artifact, 3/851); experiments/lab/qwen36_prompt_scratch/README.md (the model's proven style manual on the GO path — structural contracts over prohibitions, positive phrasing, one worked example per ask, hard length caps); the locked set directory per 16.2 (GO: agents/strategic/prompts/qwen3_6_27b/; the NO-GO rewrite is 16.2's surgery). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-elicitation-batch`
**Depends on:** 16.2, 16.5, 16.6, 16.7, 16.14
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2a/J3 (the surface design); audits/audit-phase-15-close.md §11 (the vent-tail cells: samples 53/73 mentioned; corpus 188/255) + §5.2 of the wave-0 close (the self-accusation artifact, 3/851); experiments/lab/qwen36_prompt_scratch/README.md (the model's proven style manual on the GO path — structural contracts over prohibitions, positive phrasing, one worked example per ask, hard length caps); the locked set directory per 16.2 (GO: agents/strategic/prompts/qwen3_6_27b/; the NO-GO rewrite is 16.2's surgery)
**Complexity:** Integration

The prompt surface that makes the Wave-1 machinery SPEAK, all four templates, ONE version bump
owned here (GO path: the set advances v1 → v2 in its `PROMPT_VERSION_SETS` entry; under NO-GO
16.2 rewrites this task to per-template bumps on `qwen3_32b` — three v5 templates → v6,
`vote_ballot` v6 → v7 — never a set-level relabel that would mint a colliding
`vote_ballot.qwen3_32b.v6`). Five coordinated asks: (a) **J2a provenance surface** — the ballot
template renders each candidate's suspicion WITH its provenance split (carried prior vs
this-meeting evidence, soft-only rows annotated) via 16.3's kwargs; (b) **J3 citation-required
confidence** — the ballot asks for a cited turn id or observation id with every EJECT (16.5's
rendered ids give it something to cite; the sanctioned gut-read example is REWRITTEN to cite or
skip), with confidence verbalized against the citation; (c) **roll-call elicitation** — the
opening/turn templates ask each speaker to state where they were (emitting 16.7's
`WhereaboutsClaim`) and to voice relevant sightings of others; (d) **the vent tail** — the
elicitation ask that targets the ~20/73 unspoken held vents (close audit cells; the mechanism
exists, the ask must land harder); (e) **the self-accusation fix** — the impostor turn/ballot
framing that closes the 3/851 self-naming artifact. Every ask is mechanism-tested by fixture
(template output contains the elicitation; a compliant response parses into the typed kinds);
UPTAKE is 16.17's measurement, record-only discipline.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (all four templates — the locked set per 16.2; behind 16.13's creation and 16.14's record)
- orchestrator/game.py (the locked set's PROMPT_VERSION_SETS entry — the single bump this task owns; behind 16.13's line)
- tests/meetings/test_elicitation_fixtures.py (new: per-ask mechanism fixtures)
- tests/agents/test_bespoke_prompt_sets.py (version-pin region for the bumped entry)

**Files NOT in scope:**
- meetings/ + agents/memory/ (the machinery landed in Wave 1; this is surface only)
- scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (version literals flip at 16.17, the adopting record)
- replays/samples/ (the re-record is 16.17)

**Definition of done:**
- [ ] All five asks land with per-ask fixtures: rendered output carries the elicitation; a synthetic compliant response round-trips into `WhereaboutsClaim`/observation-cited ballots/vent observations through the real validation path.
- [ ] The provenance surface renders ONLY when the render inputs supply it (lever/kwarg-gated — committed-set renders stay byte-identical, golden green), and the soft-only annotation matches 16.3's typed decomposition on a fixture.
- [ ] The gut-read example is gone: the ballot template's exemplars either cite (turn or observation id) or SKIP — no sanctioned null-citation EJECT remains in any template.
- [ ] The version bump is exactly one registry entry (pinned); pre- and post-batch prompt bodies can never share a version stamp.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Write the asks as tight structural directives with one worked example each (the v5 vent-elicitation
lesson: the example moves uptake more than the instruction). The J3 rewrite is the delicate one —
the template currently BLESSES null citations; invert the exemplar without inverting the SKIP
allowance (memory-based SKIP stays legitimate; memory-based EJECT now cites the observation id
16.5 renders). Fixtures assert presence and parseability, never model behavior.

## Integration risk

Five asks in one bump is deliberate (one attributable prompt layer at 16.17) but couples their
review: a defect found in one ask after the bump re-bumps the set. Mitigate with per-ask fixture
coverage and the A/B habit — an operator spot-run on a handful of contexts before merge is cheap
insurance the contract permits (not a recorded artifact, just diligence). The roll-call ask
interacts with turn budget (nine speakers stating whereabouts consumes tokens) — keep the ask to
one line of the response schema, not a paragraph.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.watchability"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.store"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-16-elicitation-batch` with a title like `task 16.15: the elicitation batch: citations, roll-call, provenance surface, the vent tail, the self-accusation fix`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2a/J3 (the surface design); audits/audit-phase-15-close.md §11 (the vent-tail cells: samples 53/73 mentioned; corpus 188/255) + §5.2 of the wave-0 close (the self-accusation artifact, 3/851); experiments/lab/qwen36_prompt_scratch/README.md (the model's proven style manual on the GO path — structural contracts over prohibitions, positive phrasing, one worked example per ask, hard length caps); the locked set directory per 16.2 (GO: agents/strategic/prompts/qwen3_6_27b/; the NO-GO rewrite is 16.2's surgery)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
